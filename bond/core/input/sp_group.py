"""
Interface for the SPGroup api
- SPGroup api delivers daily energy producing data
"""
import calendar
import time
import sched
import requests
import datetime

from core.abstract.input import EnergyData, Device, EnergyDataSource


class SPGroupAPI(EnergyDataSource):

    def __init__(self, site_id: str, api_url: str, api_key: str):
        self.site = site_id
        self.api_url = api_url
        self.api_key = api_key
        self.schedule = sched.scheduler(time.time, time.sleep)

    def read_state(self) -> EnergyData:
        # raw
        raw = self._get_daily_data()
        data = {}
        for specific_site in raw["sites"]:   # get the object with the right site_id
            if specific_site["site_id"] == self.site:
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
        # accumulated power in Wh
        accumulated_power = data['energy']['data'] * pow(10, -6)
        # access_epoch
        now = datetime.datetime.now().astimezone()
        access_epoch = calendar.timegm(now.timetuple())
        # measurement epoch
        measurement_timestamp = datetime.datetime.strptime(data['end_time'], '%Y-%m-%dT%H:%M:%SZ')
        measurement_epoch = calendar.timegm(measurement_timestamp.timetuple())
        return EnergyData(device=device, access_epoch=access_epoch, raw=str(raw), accumulated_power=accumulated_power,
                          measurement_epoch=measurement_epoch)

    def _get_daily_data(self) -> dict:
        marginal_query = {
            'limit': 5,
            'start': 'last_hour',
            'end': 'now'
        }
        # sending header until we get usr pwd
        provisional_header = {
            "Authorization": "Basic " + self.api_key}
        endpoint = self.api_url + 'produced'
        r = requests.get(endpoint, params=marginal_query, headers=provisional_header, verify=False)
        ans = r.json()
        if len(ans['sites']) < 1:
            raise AttributeError('Empty response from api.')
        return ans

    def __sample_data(self):
        return {
            "sites": [
                {
                    "site_id": "b1",
                    "start_time": "2018-03-26T08:21:20Z",
                    "end_time": "2018-03-26T09:21:20Z",
                    "energy": {
                        "unit": "wh",
                        "data": 875.4090909090909
                    }
                },
                ...
            ]
        }


class SPGroup_b1(SPGroupAPI):

    def __init__(self, api_url: str, api_key: str):
        super().__init__(site_id='b1', api_url=api_url, api_key=api_key)


class SPGroup_k1(SPGroupAPI):

    def __init__(self, api_url: str, api_key: str):
        super().__init__(site_id='k1', api_url=api_url, api_key=api_key)


class SPGroup_s1(SPGroupAPI):

    def __init__(self, api_url: str, api_key: str):
        super().__init__(site_id='s1', api_url=api_url, api_key=api_key)


class SPGroup_s2(SPGroupAPI):

    def __init__(self, api_url: str, api_key: str):
        super().__init__(site_id='s2', api_url=api_url, api_key=api_key)


class SPGroup_t1(SPGroupAPI):

    def __init__(self, api_url: str, api_key: str):
        super().__init__(site_id='t1', api_url=api_url, api_key=api_key)
