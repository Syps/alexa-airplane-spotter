from logger import logger
from opensky_api import StateVector, OpenSkyApi
import scrape
import settings
import requests
import json
import gpxpy.geo


TAKE_DUMP = True


class Point:


    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)


class Scanner:


    '''
    Returns a list of opensky_api StateVector's
    containing data on nearby planes
    '''
    def nearby():
        raise NotImplementedError


    def distance_from_window(self, flight):
        window_lat, window_lng = settings.coords['window']
        return gpxpy.geo.haversine_distance(window_lat, window_lng, flight.latitude, flight.longitude)


    def closest(self):
        flights = self.nearby()
        return min(flights, key=self.distance_from_window) if flights else None


class OpenSkyScanner(Scanner):


    '''
    This scanner pulls all state vectors from the open sky
    network. To filter down to only include planes in sight
    from window:

    1. make settings.py file
    2. define a dict w/ the following format:
        coords = {
            window: ( , ),
            left: ( , ),
            right: ( , )
        }

        Each value in coords is a tuple containing a lat and long.
        Together, these define the dimensions of the area in which
        the scanner will search for planes
    '''


    def __init__(self):
        self.api = OpenSkyApi()
        self.pt1 = Point(*settings.coords['window'])
        self.pt2 = Point(*settings.coords['right'])
        self.pt3 = Point(*settings.coords['left'])


    def _sign(self, p1, p2, p3):
        return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y)


    def _in_range(self, state):
        if not (state.latitude and state.longitude) or state.on_ground:
            return False;

        pt = Point(state.latitude, state.longitude)
        b1 = self._sign(pt, self.pt1, self.pt2) < 0.0
        b2 = self._sign(pt, self.pt2, self.pt3) < 0.0
        b3 = self._sign(pt, self.pt3, self.pt1) < 0.0

        return b1 == b2 == b3


    def _get_states(self):
        return self.api.get_states().states


    def nearby(self):
        states = self._get_states()
        return [state for state in states if self._in_range(state)]


class RtlScanner(Scanner):


    ENDPOINT = settings.data_endpoint


    class RtlException(Exception):
        def __init__(self):
            message = """
                Failed to establish connection to dump1090 json endpoint.
                Check that ./dump1090 --net is running, or that SSH tunnel
                is set up if dump1090 running on another computer.
                """
            super(RtlScanner.RtlException, self).__init__(message)


    def __init__(self, assert_conn=True):
        if assert_conn:
            try:
                data = requests.get(self.ENDPOINT)
            except requests.exceptions.ConnectionError:
                raise RtlScanner.RtlException()


    """
    OpenSkyApi StateVector Keys
    https://github.com/openskynetwork/opensky-api/blob/master/python/opensky_api.py

    keys = ["icao24", "callsign", "origin_country", "time_position",
            "time_velocity", "longitude", "latitude", "altitude",
            "on_ground",
            "velocity", "heading", "vertical_rate", "sensors"]
    """
    def _as_state_vector(self, data_pt):
        vector = []
        vector.append(data_pt['hex']) # icao24
        vector.append(data_pt['flight']) # callsign
        vector.append('') # origin_country
        vector.append('') # time_position
        vector.append('') # time_velocity
        vector.append(data_pt['lon']) # longitude
        vector.append(data_pt['lat']) # latitude
        vector.append(data_pt['altitude']) #altitude
        vector.append(False) # on ground
        vector.append(data_pt['speed']) # velocity
        vector.append('') # heading
        vector.append(data_pt['vert_rate']) #vertical_rate
        vector.append('') #sensors

        return StateVector(vector)


    def _valid_data(self, data_pt):
        if data_pt.get('seen', 1000) > 35: # 'seen' == seconds since last msg
            return False # stale messages == out of sight (ideally)
        if len(data_pt.get('hex', '').strip()) == 0:
            return False # invalid hex code
        return True


    def nearby(self):
        res = requests.get(self.ENDPOINT) # localhost:8080/data.json
        data = json.loads(res.text)
        data = filter(self._valid_data, data)
        return [self._as_state_vector(v) for v in data]


def get_scanner():
    return RtlScanner() if TAKE_DUMP else OpenSkyScanner()


def nearby():
    logger.info('scanning')
    flight = get_scanner().closest()
    logger.info('chose flight {}'.format(flight))
    return scrape.flight_info(flight) if flight else None


if __name__ == '__main__':
    nearby()
