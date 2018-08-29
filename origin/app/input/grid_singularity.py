"""
Interface for the Gridsingularity api
- Gridsingularity api delivers consuming and producing data which are processed separately
- delivers production from the past hour
- constructor takes the site_id, client_id, client_secret, username and password as parameter
- Access by using a requested token which is generated with each call
"""

import requests
import datetime
from datetime import tzinfo, timedelta

from core.input import EnergyData, Device, EnergyDataSource


# consumption asset
class GridSingularity(EnergyDataSource):

    def __init__(self, api_url: str, site_id: str, client_id: str, client_secret: str, username: str, password: str):

        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.site = site_id
        self.api_url = api_url

    def read_state(self) -> EnergyData:

        token_request = self.api_url + 'oauth2/token'
        marginal_query = {
            'grant_type': 'password',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'username': self.username,
            'password': self.password
        }

        r = requests.post(token_request, data=marginal_query)
        ans = r.json()
        if len(ans['access_token']) < 1:
            raise AttributeError('Empty/Error response from api.')

        # get raw data
        raw = self._get_daily_data(ans['access_token'])
        '''
        {
            "serviceLocationId": 26145,
            "consumptions": [
                {
                    "timestamp": 1508709600000,
                    "consumption": 24,
                    "solar": 0,
                    "alwaysOn": 108
                },
                {
                    "timestamp": 1508796000000,
                    "consumption": 34.9,
                    "solar": 0,
                    "alwaysOn": 0
                },
                ...                 
              ] 
            }
        '''
        # add all consumption together and save latest timestamp
        total_consumption = 0
        latest_timestamp = 0
        for element in raw["consumptions"]:
            total_consumption += element['consumption']
            if element["timestamp"] > latest_timestamp:
                latest_timestamp = element["timestamp"]

        # build the device object
        device_meta = {
            'manufacturer': 'Unknown',
            'model': 'Unknown',
            'serial_number': 'Unknown',
            'geolocation': (0, 0)
        }
        device = Device(**device_meta)

        # get produced energy from filtered object
        accumulated_power = total_consumption

        # instance of mini utc class (tzinfo)
        utc = UTC()

        # build access_timestamp
        now = datetime.datetime.now().astimezone()
        access_timestamp = now.isoformat()

        # build measurement_timestamp
        # measurement_timestamp = datetime.datetime.strptime(str(latest_timestamp/1000), '%S')
        measurement_timestamp = datetime.datetime.fromtimestamp(latest_timestamp / 1000).strftime(
            "%A, %B %d, %Y %I:%M:%S")
        measurement_timestamp = datetime.datetime.strptime(measurement_timestamp, '%A, %B %d, %Y %I:%M:%S')
        measurement_timestamp = measurement_timestamp.replace(tzinfo=utc).isoformat()

        return EnergyData(device, access_timestamp, raw, accumulated_power, measurement_timestamp)

    def _get_daily_data(self, authToken: str) -> dict:
        # calculate the current time and one hour back from there
        d = datetime.datetime.utcnow()
        epoch = datetime.datetime(1970, 1, 1)
        # * 1000 parse int (no clue why grid is asking for that format)
        time_now = int((d - epoch).total_seconds() * 1000)
        time_one_hour_ago = int(time_now - 3600 * 1000 * 25)

        marginal_query = {
            'aggregation': 2,
            'from': time_one_hour_ago,
            'to': time_now
        }

        # build the endpoint for the request
        endpoint = self.api_url + 'servicelocation/' + self.site + '/consumption'

        provisional_header = {"Authorization": "Bearer " + authToken}

        # start request
        r = requests.get(endpoint, params=marginal_query, headers=provisional_header)
        ans = r.json()
        if len(ans['consumptions']) < 1:
            raise AttributeError('Empty response from api.')
        return ans


class GridSingularity_26145(GridSingularity):

    def __init__(self, api_url: str, client_id: str, client_secret: str, username: str, password: str):
        super().__init__(api_url, '26145', client_id, client_secret, username, password)


class UTC(tzinfo):

    def __init__(self):
        self.ZERO = timedelta(0)

    def utcoffset(self, dt):
        return self.ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return self.ZERO
