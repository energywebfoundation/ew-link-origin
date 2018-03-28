import calendar

import requests
import datetime

from core.abstract.input import ExternalDataSource, EnergyData, Device

# producing asset
class Exelon(ExternalDataSource):

    def __init__(self, site_id: str):

        self.site = site_id
        self.api_url = 'https://origin-dev.run.aws-usw02-pr.ice.predix.io/api/'

    def read_state(self) -> EnergyData:
        raw = self._get_daily_data()
        '''
        {
            "production": [
                {
                    "assetPublicAddress": "0x6e953cc665e527d10989172def6a91fd489e7cf11",
                    "amount": 6876.4,
                    "startTime": "2015-03-17T06:00:00.000Z",
                    "endTime": "2015-03-17T06:59:59.999Z"
                },
                ...
            ]
        }
        '''
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
        accumulated_power = int(("%.2f" % specific_site['amount']).replace('.', ''))

        # build access_epoch
        now = datetime.datetime.now()
        access_epoch = calendar.timegm(now.timetuple())

        # build measurement_epoch
        measurement_timestamp = datetime.datetime.strptime(specific_site['endTime'], '%Y-%m-%dT%H:%M:%S.%fZ')
        measurement_epoch = calendar.timegm(measurement_timestamp.timetuple())

        return EnergyData(device, access_epoch, raw, accumulated_power, measurement_epoch)

    def _get_daily_data(self) -> dict:
        date_now = datetime.datetime.utcnow().isoformat()
        date_one_hour_before = datetime.datetime.utcnow() - datetime.timedelta(seconds=3600)
        marginal_query = {
            'start': '2015-03-17T06:00:00.000Z',
            'end': '2015-03-18T04:59:59.999Z'

            #  Exelon currently only provides data for the year 2015
            # 'start': date_now,  # timestamp
            # 'end': date_one_hour_before.isoformat()  # timestamp
        }

        provisional_header = {"X-Api-Key": "CFX8trB6cHZ9usMtFFwfQQVNr5jWze4EUFjz89DnQX6YHAjwU93trunF5pUqveTfyD6Uep5AQfrHuXEcsrBDbnbKmDVSW25JY5VA"}
        endpoint = self.api_url + 'production'
        r = requests.get(endpoint, params=marginal_query, headers=provisional_header)
        ans = r.json()
        if len(ans['production']) < 1:
            raise AttributeError('Empty response from api.')
        return ans


# needs a site_id
class Exelon_1(Exelon):

    def __init__(self, site_id: '0x6e953cc665e527d10989172def6a91fd489e7cf11'):
        super().__init__(site_id)


if __name__ == '__main__':
    ex = Exelon_1('b1')
    ex.read_state()