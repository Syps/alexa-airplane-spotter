from pymongo import MongoClient
import json

client = MongoClient('localhost:27017')
db = client.AircraftData


with open('airports_tz.json', 'r') as f:
    airport_tzs = json.loads(f.read())
    for key in airport_tzs.keys():
            try:
                db.AirportTZ.insert_one(airport_tzs[key])
            except Exception as e:
                print(str(e))
