"""
Interface for the Exelon api
- Exelon api delivers producing data
- delivers production from the past hour
- constructor takes the site_id as parameter
- !!! Access by hardcoded api key !!!
"""

import datetime
import requests

from core.abstract import UTC
from core.abstract.input import EnergyDataSource, EnergyData, Device


# producing asset - !! only returns data from before 2015
class Exelon(EnergyDataSource):

    def __init__(self, site_id: str):
        """
        TODO: remove url
        :param site_id:
        """
        self.site = site_id
        self.api_url = 'https://origin-dev.run.aws-usw02-pr.ice.predix.io/api/'

    def read_state(self) -> EnergyData:
        raw = self._get_daily_data()
        # get the object with the right site_id
        state = {}

        for specific_site in raw["production"]:
            if specific_site["assetPublicAddress"] == self.site:
                state = specific_site
                break

        # build the device object
        device_meta = {
            'manufacturer': 'Unknown',
            'model': 'Unknown',
            'serial_number': 'Unknown',
            'geolocation': (0, 0)
        }
        device = Device(**device_meta)

        # get produced energy from filtered object
        # accumulated_power = specific_site['energy']['data']
        accumulated_power = specific_site['amount']

        # build access_timestamp
        now = datetime.datetime.now().astimezone()
        access_timestamp = now.isoformat()

        # build measurement_timestamp
        measurement_timestamp = datetime.datetime.strptime(specific_site['endTime'], '%Y-%m-%dT%H:%M:%S.%fZ')
        measurement_timestamp = measurement_timestamp.replace(tzinfo=UTC()).isoformat()

        return EnergyData(device, access_timestamp, raw, accumulated_power, measurement_timestamp)

    def _get_daily_data(self) -> dict:
        # date_now = datetime.datetime.utcnow().isoformat()
        # date_one_hour_before = datetime.datetime.utcnow() - datetime.timedelta(seconds=3600)
        marginal_query = {
            'start': '2015-03-17T06:00:00.000Z',
            'end': '2015-03-18T04:59:59.999Z'
        }

        provisional_header = {
            "X-Api-Key": "CFX8trB6cHZ9usMtFFwfQQVNr5jWze4EUFjz89DnQX6YHAjwU93trunF5pUqveTfyD6Uep5AQfrHuXEcsrBDbnbKmDVSW25JY5VA"}
        endpoint = self.api_url + 'production'
        r = requests.get(endpoint, params=marginal_query, headers=provisional_header)
        ans = r.json()
        if len(ans['production']) < 1:
            raise AttributeError('Empty response from api.')
        return ans


# needs a site_id
class Exelon_1(Exelon):

    def __init__(self, site_id: str):
        super().__init__(site_id)