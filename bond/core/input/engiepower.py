"""
Interface for the Engie api
- Engie api delivers producing data
- delivers consumption and production from the past hour
- constructor takes the site_id, username and password as parameters
- Access by username and password
"""
import calendar
import datetime
import requests

from core.abstract.input import EnergyDataSource, EnergyData, Device


class SmireTestAPI(EnergyDataSource):

    def __init__(self, usr: str, pwd: str, site: str):
        """
        Blue Saphire Test Smire API. https://test.smire.bluesafire.io
        :param usr: Username used for login
        :param pwd: Passphrase
        """
        self.credentials = (usr, pwd)
        self.site = site
        self.api_url = 'https://test.smire.bluesafire.io/api/'

    def read_state(self, days=1) -> EnergyData:
        # raw
        raw = self._get_daily_data(days)
        data = [{'date': a, 'produced': b} for a, b in zip(raw['datetime'], raw['production'])]
        # device
        device_meta = {
            'manufacturer': 'Unknown',
            'model': 'Unknown',
            'serial_number': 'Unknown',
            'geolocation': (raw['site']['latitude'], raw['site']['longitude'])
        }
        device = Device(**device_meta)
        # accumulated power in KWh
        accumulated_power = data[-1]['produced'] * pow(10, -3)
        # access_epoch
        now = datetime.datetime.now().astimezone()
        access_epoch = calendar.timegm(now.timetuple())
        # measurement epoch
        measurement_timestamp = datetime.datetime.strptime(data[-1]['date'], "%Y-%m-%d")
        measurement_epoch = calendar.timegm(measurement_timestamp.timetuple())
        return EnergyData(device=device, access_epoch=access_epoch, raw=raw, accumulated_power=accumulated_power,
                          measurement_epoch=measurement_epoch)

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

    def __sample_data(self):
        """
        TODO: Engie smire api sample json
        """
        return {}


class Eget(SmireTestAPI):

    def __init__(self, usr: str, pwd: str):
        super().__init__(usr, pwd, 'eget')


class Frasnes(SmireTestAPI):

    def __init__(self, usr: str, pwd: str):
        super().__init__(usr, pwd, 'frasnes')


class Burgum(SmireTestAPI):

    def __init__(self, usr: str, pwd: str):
        super().__init__(usr, pwd, 'burgum')


class Fontanelles(SmireTestAPI):

    def __init__(self, usr: str, pwd: str):
        super().__init__(usr, pwd, 'fontanelles')


class SmireAPI(EnergyDataSource):
    """
    import future
    TODO: New smire api
    """

    def __init__(self):
        """
        Blue Saphire Smire API. https://smire.bluesafire.io
        """
        raise NotImplementedError
