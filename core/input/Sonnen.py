import calendar

import requests
import datetime

from core.abstract.input import ExternalDataSource, EnergyData, Device

# consuming asset
class Sonnen_consume(ExternalDataSource):

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
        accumulated_power = int(("%.2f" % raw['data']['sum_charge_kwh'] * 1000).replace('.', ''))

        # build access_epoch
        now = datetime.datetime.now()
        access_epoch = calendar.timegm(now.timetuple())

        # TODO: figure out all that timezone stuff
        # build measurement_epoch
        measurement_timestamp = datetime.datetime.strptime(raw['requested_date'], '%Y-%m-%d')
        measurement_epoch = calendar.timegm(measurement_timestamp.timetuple())

        return EnergyData(device, access_epoch, raw, accumulated_power, measurement_epoch)

    def _get_daily_data(self) -> dict:

        # calculate the current time and one hour back from there

        marginal_query = {
            'date': 5,  # expects year-month-day
            'hour': 'last_hour',  # the hour of day
            'utc_offset': '01:00',  # TODO: ask jens about that
            'asset_id': self.site
        }

        endpoint = self.api_url + 'charge_discharge'

        r = requests.get(endpoint, params=marginal_query)
        ans = r.json()
        if len(ans['sites']) < 1:
            raise AttributeError('Empty response from api.')
        return ans


# producing asset
class Sonnen_produce(ExternalDataSource):

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
        accumulated_power = int(("%.2f" % raw['data']['sum_discharge_kwh'] * 1000).replace('.', ''))

        # build access_epoch
        now = datetime.datetime.now()
        access_epoch = calendar.timegm(now.timetuple())

        # TODO: figure out all that timezone stuff
        # build measurement_epoch
        measurement_timestamp = datetime.datetime.strptime(raw['requested_date'], '%Y-%m-%d')
        measurement_epoch = calendar.timegm(measurement_timestamp.timetuple())

        return EnergyData(device, access_epoch, raw, accumulated_power, measurement_epoch)

    def _get_daily_data(self) -> dict:

        # calculate the current time and one hour back from there

        marginal_query = {
            'date': 5,  # expects year-month-day
            'hour': 'last_hour',  # the hour of day
            'utc_offset': '01:00',  # TODO: ask jens about that
            'asset_id': self.site
        }

        endpoint = self.api_url + 'charge_discharge'

        r = requests.get(endpoint, params=marginal_query)
        ans = r.json()
        if len(ans['sites']) < 1:
            raise AttributeError('Empty response from api.')
        return ans


# sonne 101 consume
class Sonnen_101_c(Sonnen_consume):

    def __init__(self, site_id: '101'):
        super().__init__(site_id)


# sonne 101 produce
class Sonnen_101_p(Sonnen_produce):

    def __init__(self, site_id: '101'):
        super().__init__(site_id)


if __name__ == '__main__':
    sp1 = Sonnen_101_c('101')
    sp1.read_state()
    sp2 = Sonnen_101_p('101')
    sp2.read_state()