from pymongo import MongoClient
import csv

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

with open('aircraft_db.csv', 'r') as f:
    reader = csv.reader(f)
    reader.next()
    for row in reader:
        add_to_db(row)
