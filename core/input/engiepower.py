import calendar

import requests
import datetime

from core.abstract.input import ExternalDataSource, EnergyData, Device


class SmireAPI(ExternalDataSource):

    def __init__(self, usr: str, pwd: str, site: str):
        """
        Blue Saphire Smire API. https://test.smire.bluesafire.io
        :param usr: Username used for login
        :param pwd: Passphrase
        """
        self.credentials = (usr, pwd)
        self.site = site
        self.api_url = 'https://test.smire.bluesafire.io/api/'

    def read_state(self, days=1) -> EnergyData:
        raw = self._get_daily_data(days)
        state = [{'date': a, 'produced': b} for a, b in zip(raw['datetime'], raw['production'])]
        device_meta = {
            'manufacturer': 'Unknown',
            'model': 'Unknown',
            'serial_number': 'Unknown',
            'geolocation': (raw['site']['latitude'], raw['site']['longitude'])
        }
        device = Device(**device_meta)
        accumulated_power = state[0]['produced']
        now = datetime.datetime.now()
        access_epoch = calendar.timegm(now.timetuple())
        measurement_timestamp = datetime.datetime.strptime(state[0]['date'], "%Y-%m-%d")
        measurement_epoch = calendar.timegm(measurement_timestamp.timetuple())
        return EnergyData(device, access_epoch, raw, accumulated_power, measurement_epoch)

    def _get_daily_data(self, days) -> dict:
        marginal_query = {
            'day_count': days,
            'site': self.site
        }
        endpoint = self.api_url + 'daily_data'
        r = requests.get(endpoint, params=marginal_query, auth=self.credentials)
        ans = r.json()
        if len(ans['production']) < 1:
            raise AttributeError('Empty response from api.')
        return ans


class Eget(SmireAPI):

    def __init__(self, usr: str, pwd: str):
        super().__init__(usr, pwd, 'eget')


class Fontanelles(SmireAPI):

    def __init__(self, usr: str, pwd: str):
        super().__init__(usr, pwd, 'fontanelles')

