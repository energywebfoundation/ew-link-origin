"""
Interface for the Engie api
- Engie api delivers producing data
- delivers consumption and production from the past hour
- constructor takes the site_id, username and password as parameters
- Access by username and password
"""

import requests
import datetime
from datetime import tzinfo, timedelta

from core.abstract.input import EnergyDataSource, EnergyData, Device


class SmireAPI(EnergyDataSource):

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
        accumulated_power = state[-1]['produced'] * pow(10, 3)

        # instance of mini utc class (tzinfo)
        cest = CEST()

        now = datetime.datetime.now().astimezone()
        access_timestamp = now.isoformat()

        measurement_timestamp = datetime.datetime.strptime(state[-1]['date'], "%Y-%m-%d")
        measurement_timestamp = measurement_timestamp.replace(tzinfo=cest).isoformat()  # forcing the france timezone

        return EnergyData(device, access_timestamp, raw, accumulated_power, measurement_timestamp)

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


class Frasnes(SmireAPI):

    def __init__(self, usr: str, pwd: str):
        super().__init__(usr, pwd, 'frasnes')


class Burgum(SmireAPI):

    def __init__(self, usr: str, pwd: str):
        super().__init__(usr, pwd, 'burgum')


class Fontanelles(SmireAPI):

    def __init__(self, usr: str, pwd: str):
        super().__init__(usr, pwd, 'fontanelles')


ZERO = timedelta(0)
TWO = timedelta(hours=2)

class UTC(tzinfo):
    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO


class CEST(tzinfo):
    def utcoffset(self, dt):
        return TWO

    def tzname(self, dt):
        return "CEST"

    def dst(self, dt):
        return TWO

'''
if __name__ == '__main__':
    ex = Eget('', '')
    ex.read_state()
'''