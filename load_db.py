from pymongo import MongoClient
import csv
import json

client = MongoClient('localhost:27017')
db = client.AircraftData

#    icao,regid,mdl,type,operator
def add_to_db(row):
    icao, regid, mdl, typ, operator = row
    try:
        db.Registration.insert_one(
            {
            "icao": icao,
            "regid": regid,
            "mdl": mdl,
            "type": typ,
            "operator": operator
            })
    except Exception as e:
        print(str(e))


def load_aircrafts():
    print('Loading aircraft data into database...')
    with open('aircraft_db.csv', 'r') as f:
        reader = csv.reader(f)
        reader.next()
        for row in reader:
            add_to_db(row)
    print('Done')


def load_airport_tz():
    print('Loading airport timezones into database...')
    with open('airports_tz.json', 'r') as f:
        airport_tzs = json.loads(f.read())
        for key in airport_tzs.keys():
                try:
                    db.AirportTZ.insert_one(airport_tzs[key])
                except Exception as e:
                    print(str(e))
    print('Done')


if __name__ == '__main__':
    load_aircrafts()
    load_airport_tz()
