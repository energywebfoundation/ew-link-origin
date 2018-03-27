import calendar

import requests
import datetime

from core.abstract.input import ExternalDataSource, EnergyData, Device

# consumption asset
class GridSingularity(ExternalDataSource):

    def __init__(self, site_id: str):

        self.site = site_id
        self.api_url = 'https://app1pub.smappee.net/dev/v1/servicelocation/'

    def read_state(self) -> EnergyData:
        raw = self._get_daily_data()
        '''
            {
            "serviceLocationId": 123,
            “consumptions” : [ 
                { “timestamp”: 1372672500000, “consumption”: 23, “solar”: 56, “alwaysOn”: 12 },
                { “timestamp”: 1372672800000, “consumption”: 67, “solar”: 57, “alwaysOn”: 12 },
                { “timestamp”: 1372673100000, “consumption”: 88, “solar”: 58, “alwaysOn”: 12 },
                ...                 
              ] 
            }
        '''
        # get the object with the right site_id
        state = {}

        for specific_site in raw["sites"]:
            if specific_site["site_id"] == self.site:
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
        accumulated_power = int(("%.2f" % specific_site['energy']['data']).replace('.', ''))

        # build access_epoch
        now = datetime.datetime.now()
        access_epoch = calendar.timegm(now.timetuple())

        # build measurement_epoch
        measurement_timestamp = datetime.datetime.strptime(specific_site['end_time'], '%Y-%m-%dT%H:%M:%SZ')
        measurement_epoch = calendar.timegm(measurement_timestamp.timetuple())

        return EnergyData(device, access_epoch, raw, accumulated_power, measurement_epoch)

    def _get_daily_data(self) -> dict:
        # calculate the current time and one hour back from there
        d = datetime.datetime.utcnow()
        epoch = datetime.datetime(1970, 1, 1)
        time_now = (d - epoch).total_seconds()
        time_one_hour_ago = time_now - 3600

        marginal_query = {
            'aggregation': 2,
            'from': time_one_hour_ago,
            'to': time_now
        }

        # build the endpoint for the request
        endpoint = self.api_url + self.site_id + '/consumption/'

        # do the access management (get access token)
        # TODO: ask jens about that junk

        # start request
        r = requests.get(endpoint, params=marginal_query, verify=False)
        ans = r.json()
        if len(ans['serviceLocationId']) < 1:
            raise AttributeError('Empty response from api.')
        return ans


class GridSingularity_123(GridSingularity):

    def __init__(self, site_id: '123'):
        super().__init__(site_id)


if __name__ == '__main__':
    gs = GridSingularity_123('123')
    gs.read_state()
