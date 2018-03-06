import calendar

import requests
import datetime

from core.abstract.input import ExternalDataSource, CarbonEmissionData


class Wattime(ExternalDataSource):

    def __init__(self, usr, pwd):
        """
        Wattime API credentials. http://watttime.org/
        :param usr: Username used for login
        :param pwd: Users password
        """
        self.credentials = {'username': usr, 'password': pwd}
        self.api_url = 'https://api.watttime.org/api/v1/'

    def read_state(self, ba) -> CarbonEmissionData:
        """
        Reach wattime api, parse and convert to CarbonEmissionData.
        :param ba: Balancing Authority. https://api.watttime.org/tutorials/#ba
        """
        # 1. Authenticate in Wattime api
        auth_token = self.get_auth_token()
        # 2. Fetch marginal data
        raw = self.get_marginal(ba, auth_token)
        # 3. Converts lb/MW to kg/MW
        accumulated_co2 = raw['marginal_carbon']['value']
        # 4. Converts time stamps to epoch
        now = datetime.datetime.now()
        access_epoch = calendar.timegm(now.timetuple())
        measurement_timestamp = datetime.datetime.strptime(raw['timestamp'], "%Y-%m-%dT%H:%M:%SZ")
        measurement_epoch = calendar.timegm(measurement_timestamp.timetuple())
        return CarbonEmissionData(access_epoch, raw, accumulated_co2, measurement_epoch)

    def get_auth_token(self) -> str:
        """
        Exchange credentials for an access token.
        :return: Access token string suitable for passing as arg in other methods.
        """
        endpoint = self.api_url + 'obtain-token-auth/'
        r = requests.post(endpoint, data=self.credentials)
        ans = r.json()
        if (not r.status_code == 200) or len(ans['token']) < 5:
            raise AttributeError('Failed getting a new token.')
        return ans['token']

    def get_marginal(self, ba, auth_token) -> dict:
        """
        Gets marginal carbon emission based on real time energy source mix of the grid.
        :param ba: Balancing Authority. https://api.watttime.org/tutorials/#ba
        :param auth_token: authentication token
        :return: Measured data in lb/MW plus other relevant raw metadata.
        """
        last_hour = datetime.datetime.now() - datetime.timedelta(hours=1),
        marginal_query = {
            'ba': ba,
            'start_at': last_hour.strftime("%Y-%m-%dT%H:00:00"),
            'end_at': last_hour.strftime("%Y-%m-%dT%H:59:59"),
            'page_size': 1,
            'freq': '',
            'market': 'RTHR'
        }
        endpoint = self.api_url + 'marginal/'
        h = {'token': auth_token}
        r = requests.get(endpoint, headers=h, params=marginal_query)
        ans = r.json()
        if ans['count'] < 1 or ans['count'] > 1:
            raise AttributeError('Ambiguous response from api.')
        return ans['results'][0]

    def get_ba(self, lon, lat, auth_token) -> str:
        """
        Fetch Balancing Authority data based on geo spatial coordinates.
        :param lon: longitude
        :param lat: latitude
        :param auth_token: authentication token
        :return: Abbreviated ba name suitable for marginal requests.
        """
        geo_query = {
            'type': 'Point',
            'coordinates': [lon, lat]
        }
        endpoint = self.api_url + 'balancing_authorities/'
        h = {'token': auth_token}
        r = requests.get(endpoint, headers=h, params=geo_query)
        ans = r.json()
        return ans['abbrev']
