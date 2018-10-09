"""
Interface for the Exelon api
- Exelon api delivers production from the past hour
"""
import calendar
import datetime
import requests

from core.abstract.input import EnergyDataSource, EnergyData, Device


class ExelonAPI(EnergyDataSource):

    def __init__(self, api_url: str, site_id: str, api_key: str):
        """
        :param api_url: API url
        :param site_id: Site identification
        :param api_key: Key to access the api
        """
        self.site = site_id
        self.api_url = api_url
        self.api_key = api_key

    def read_state(self) -> EnergyData:
        # raw
        raw = self._get_daily_data()
        data = {}  # get the object with the right site_id
        for specific_site in raw["production"]:
            if specific_site["assetPublicAddress"] == self.site:
                data = specific_site
                break
        # device
        device_meta = {
            'manufacturer': 'Unknown',
            'model': 'Unknown',
            'serial_number': 'Unknown',
            'geolocation': (0, 0)
        }
        device = Device(**device_meta)
        # accumulated power in ?
        accumulated_power = int(data['amount'])
        # access_epoch
        now = datetime.datetime.now().astimezone()
        access_epoch = calendar.timegm(now.timetuple())
        # measurement epoch
        measurement_timestamp = datetime.datetime.strptime(data['endTime'], '%Y-%m-%dT%H:%M:%S.%fZ')
        measurement_epoch = calendar.timegm(measurement_timestamp.timetuple())
        return EnergyData(device=device, access_epoch=access_epoch, raw=raw, accumulated_energy=accumulated_power,
                          measurement_epoch=measurement_epoch)

    def _get_daily_data(self) -> dict:
        marginal_query = {
            'start': '2015-03-17T06:00:00.000Z',
            'end': '2015-03-18T04:59:59.999Z'
        }
        provisional_header = {
            "X-Api-Key": self.api_key}
        endpoint = self.api_url + 'production'
        r = requests.get(endpoint, params=marginal_query, headers=provisional_header)
        ans = r.json()
        if len(ans['production']) < 1:
            raise AttributeError('Empty response from api.')
        return ans

    def __sample_data(self):
        """
        TODO: Excelon test data
        """
        return {}


class ExelonTest(ExelonAPI):

    def __init__(self, url: str, api_key: str):
        super().__init__(url=url, api_key=api_key, site_id='Test')
