from bs4 import BeautifulSoup
from pymongo import MongoClient
import json
import requests
import re
import csv
import datetime
from logger import logger
import settings

route_data_endpoint = 'https://www.flightradar24.com/data/aircraft/{}'

with open('icao_codes.tsv', 'r') as f:
    airplane_codes = {}
    icao_codes = csv.reader(f, delimiter='\t')
    next(icao_codes, None)
    for row in icao_codes:
        code, iata, name = row
        airplane_codes[code] = name


def get_departure_airport(row):
    airport = row.findAll('td')[2].find('span').text
    airport_code = re.search('[A-Z]{3}', airport).group(0)
    return airport_code


def get_tz_offset(airport_code):
    client = MongoClient('localhost:27017')
    db = client.AircraftData
    result = db.AirportTZ.find_one({
        'code': airport_code
    })
    return abs(result['offset']['dst'])


def departure_time_for_row(tr):
    tds = tr.findAll('td')
    if len(tds) < 6 or tds[6].text.strip() == '-':
        return None
    year_month_day = tds[1].text.strip()
    time_depart = tds[6].text.strip()
    localtime = datetime.datetime.strptime('{} {}'.format(year_month_day, time_depart), '%Y-%m-%d %H:%M')
    departure_airport = get_departure_airport(tr)
    return localtime - datetime.timedelta(hours=get_tz_offset(departure_airport))


def std_in_past(row):
    std = departure_time_for_row(row)
    return std is None or std < datetime.datetime.now()


def most_recent_departure(soup):
    trs = soup.findAll('tr')[1:] # first tr in html isn't a flight row
    return next((tr for tr in trs if std_in_past(tr) and tr is not None), None)


def scrape_route_data(reg_no):
    url = route_data_endpoint.format(reg_no) #flightradar24.com/data/aircraft/{}
    logger.info("url={}".format(url))
    headers = {'user-agent': 'curl/7.38.0'} # cloudfare 418 workaround
    res = requests.get(url, headers=headers)
    route_row = most_recent_departure(BeautifulSoup(res.text, "lxml"))

    depart = route_row.findAll('td')[2].find('span').text
    depart = re.sub('[A-Z]{3}', '', depart).strip()
    arrive = route_row.findAll('td')[3].find('span').text
    arrive = re.sub('[A-Z]{3}', '', arrive).strip()

    return depart, arrive


def db_results(icao24):
    client = MongoClient('localhost:27017')
    db = client.AircraftData
    result = db.Registration.find_one({
        'icao': icao24.upper()
    })

    if not result:
        return None

    airline = result['operator'].encode('ascii')
    reg_no = result['regid'].encode('ascii')
    aircraft = result['type'].encode('ascii')

    return reg_no, aircraft, airline


def flight_info(flight):
    results = db_results(flight.icao24)

    if not results:
        logger.info('could find flight in db (flight={})'.format(flight))
        return None

    reg_no, aircraft, airline = results
    aircraft = ''.join(aircraft.split('-')[:-1])

    data = {
            'aircraft': aircraft,
            'airline': airline
    }

    if not reg_no:
        logger.info('couldn\'t find aircraft icao ({}) in db'.format(flight.icao24))
        return data

    route_results = scrape_route_data(reg_no)

    if route_results:
        from_airport, to_airport = route_results
        data.update({
                     'airport_depart': from_airport,
                     'airport_arrive': to_airport
                    })
    return data
