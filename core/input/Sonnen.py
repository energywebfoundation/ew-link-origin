"""
Interface for the Sonnen api
- Sonnen api delivers consuming and producing data which are processed separately
- delivers consumption and production !!! from the previous day two hours behinde !!!
- constructor takes the site_id as parameter
- !!! Access by hardcoded api key !!!
"""

import requests
import datetime
from datetime import timezone, timedelta, tzinfo
from core.abstract.input import EnergyData, Device, EnergyDataSource


# consuming asset
class Sonnen_consume(EnergyDataSource):

    def __init__(self, site_id: str):

        self.site = site_id
        self.api_url = 'https://4ljl2ccd1i.execute-api.eu-central-1.amazonaws.com/dev/'

    def read_state(self) -> EnergyData:
        raw = self._get_daily_data()
        '''
            {
                "message": "Query executed sucessfully.",
                "data": {
                    "asset_id": 101,
                    "sum_charge_kWh": 22.101,
                    "utc_offset": "01:00",
                    "sum_discharge_kWh": 11.101,
                    "requested_hour": 11,
                    "requested_date": "2018-03-27"
                }
            }
        '''

        # build the device object
        device_meta = {
            'manufacturer': 'Unknown',
            'model': 'Unknown',
            'serial_number': 'Unknown',
            'geolocation': (0, 0)
        }
        device = Device(**device_meta)

        # get produced energy
        accumulated_power = raw['data']['sum_charge_kWh']

        utc = UTC()

        # build access_epoch
        now = datetime.datetime.now().astimezone()
        access_timestamp = now.isoformat()

        # build measurement_epoch
        measurement_timestamp = datetime.datetime.strptime(
            raw['data']['requested_date'] + 'T' + str(datetime.timedelta(hours=int(raw['data']['requested_hour']))),
            '%Y-%m-%dT%H:%M:%S')
        measurement_timestamp = measurement_timestamp.replace(tzinfo=utc).isoformat()

        return EnergyData(device, access_timestamp, raw, accumulated_power, measurement_timestamp)

    def _get_daily_data(self) -> dict:

        # calculate the current time and one hour back from there

        d = datetime.datetime.now(timezone.utc).astimezone()
        utc_offset = d.utcoffset()

        marginal_query = {
            'date': str(datetime.date.today() - timedelta(days=1)),  # expects year-month-day
            'hour': datetime.datetime.now().hour - 2,  # the hour of day
            'utc_offset': utc_offset,
            'asset_id': self.site
        }

        provisional_header = {"x-api-key": "ldEwCUZscBaNXHgm9qoeR9RnUKnzhQ5t7umVRNfH"}
        endpoint = self.api_url + 'charge_discharge'

        r = requests.get(endpoint, params=marginal_query, headers=provisional_header)
        ans = r.json()
        if len(ans['message']) < 1:
            raise AttributeError('Empty response from api.')
        if ans['message'] == 'Forbidden':
            raise AttributeError('Wrong auth')
        return ans


# producing asset
class Sonnen_produce(EnergyDataSource):

    def __init__(self, site_id: str):

        self.site = site_id
        self.api_url = 'https://4ljl2ccd1i.execute-api.eu-central-1.amazonaws.com/dev/'

    def read_state(self) -> EnergyData:
        raw = self._get_daily_data()
        '''
            {
                "message": "Query executed sucessfully.",
                "data": {
                    "asset_id": 101,
                    "sum_charge_kWh": 22.101,
                    "utc_offset": "01:00",
                    "sum_discharge_kWh": 11.101,
                    "requested_hour": 11,
                    "requested_date": "2018-03-27"
                }
            }
        '''

        # build the device object
        device_meta = {
            'manufacturer': 'Unknown',
            'model': 'Unknown',
            'serial_number': 'Unknown',
            'geolocation': (0, 0)
        }
        device = Device(**device_meta)

        # get produced energy
        accumulated_power = raw['data']['sum_discharge_kWh']

        utc = UTC()

        # build access_epoch
        now = datetime.datetime.now().astimezone()
        access_timestamp = now.isoformat()

        # build measurement_epoch
        measurement_timestamp = datetime.datetime.strptime(
            raw['data']['requested_date'] + 'T' + str(datetime.timedelta(hours=int(raw['data']['requested_hour']))),
            '%Y-%m-%dT%H:%M:%S')
        measurement_timestamp = measurement_timestamp.replace(tzinfo=utc).isoformat()

        return EnergyData(device, access_timestamp, raw, accumulated_power, measurement_timestamp)

    def _get_daily_data(self) -> dict:

        # calculate the current time and one hour back from there

        d = datetime.datetime.now(timezone.utc).astimezone()
        utc_offset = d.utcoffset()

        marginal_query = {
            'date': str(datetime.date.today()),  # expects year-month-day
            'hour': datetime.datetime.now().hour - 1,  # the hour of day
            'utc_offset': utc_offset,
            'asset_id': self.site
        }

        provisional_header = {"x-api-key": "ldEwCUZscBaNXHgm9qoeR9RnUKnzhQ5t7umVRNfH"}
        endpoint = self.api_url + 'charge_discharge'

        r = requests.get(endpoint, params=marginal_query, headers=provisional_header)
        ans = r.json()
        if len(ans['message']) < 1:
            raise AttributeError('Empty response from api.')
        if ans['message'] == 'Forbidden':
            raise AttributeError('Wrong auth')
        return ans


# sonne 101 consume
class Sonnen_101_c(Sonnen_consume):

    def __init__(self):
        super().__init__(site_id='101')


# sonne 101 produce
class Sonnen_101_p(Sonnen_produce):

    def __init__(self):
        super().__init__(site_id='101')


# sonne 102 consume
class Sonnen_102_c(Sonnen_consume):

    def __init__(self):
        super().__init__(site_id='102')


# sonne 102 produce
class Sonnen_102_p(Sonnen_produce):

    def __init__(self):
        super().__init__(site_id='102')


ZERO = timedelta(0)


class UTC(tzinfo):
    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO


if __name__ == '__main__':
    sp1 = Sonnen_102_c()
    sp1.read_state()
    sp2 = Sonnen_102_p()
    sp2.read_state()
