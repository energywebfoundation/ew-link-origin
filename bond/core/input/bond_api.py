"""
Interface for the Bond API
- Bond API delivers prosumer data
"""
import calendar
import datetime
import requests
import json

from core.abstract.input import EnergyData, Device, EnergyDataSource


class BondAPIv1(EnergyDataSource):

    def __init__(self, base_url, source, device_id, user=None, password=None):
        """
        Bond api spec v1.x module

        :param base_url: Must start with protocol. ie. https://my-url
        :param source: Must be 'produced' or 'consumed'
        :param device_id: Please mind it will be url encoded.
        :param user: User credential.
        :param password: Password for basic authentication method.
        """
        if source not in ('produced', 'consumed'):
            raise AssertionError
        self.base_url = base_url
        self.api_url = '{}/{}/{}'.format(base_url, source, device_id)
        self.auth = (user, password)

    def read_state(self) -> EnergyData:
        # raw
        raw, data, measurement_list = self._reach_source(self.api_url)
        # device
        device_meta = data[-1]['device']
        device = Device(**device_meta)
        # accumulated energy in Wh
        if device.is_accumulated:
            accumulated_energy = self.to_wh(measurement_list[-1]['energy'], device.energy_unit)
        else:
            accumulated_energy = self.to_wh(sum(i['energy'] for i in measurement_list), device.energy_unit)
        # access_epoch
        now = datetime.datetime.now().astimezone()
        access_epoch = calendar.timegm(now.timetuple())
        #  measurement epoch
        measurement_time = datetime.datetime.strptime(measurement_list[-1]['measurement_time'], "%Y-%m-%dT%H:%M:%S%z")
        measurement_epoch = calendar.timegm(measurement_time.timetuple())
        return EnergyData(device=device, access_epoch=access_epoch, raw=raw, accumulated_energy=accumulated_energy,
                          measurement_epoch=measurement_epoch)

    def _reach_source(self, url) -> (str, dict):
        http_packet = requests.get(url=url, auth=self.auth)
        raw = http_packet.content.decode()
        if not http_packet.ok:
            raise EnvironmentError
        data = http_packet.json()
        return self._parse_source(raw, data)

    def _parse_source(self, raw: str, data: dict):
        measurement_list = data['measuredEnergy']
        if data['next']:
            _, __, ___ = self._reach_source(self.base_url + data['next'])
            return tuple(x + y for x, y in zip(([raw], [data], measurement_list), (_, __, ___)))
        return [raw], [data], measurement_list


class BondAPIv1TestDevice1(BondAPIv1):
    """
    Data parsing test fixture
    """

    def _reach_source(self, url) -> (str, dict):
        raw = {
            "base_url/produced/0": '{"count": 0, "previous": null, "next": "/second", "device": {"manufacturer": "Siemens", "model": "ABC-123", "serial_number": "345345345", "latitude": "54.443567", "longitude": "-23.312543", "energy_unit": "kilowatt_hour", "is_accumulated": true }, "measuredEnergy": [{"energy": 100, "measurement_time": "2018-03-15T10:30:00+00:00"}, {"energy": 200, "measurement_time": "2018-03-15T12:30:00+00:00"}, {"energy": 250, "measurement_time": "2018-03-15T14:30:00+00:00"} ] }',
            "base_url/second": '{"count": 1, "previous": "first", "next": null, "device": {"manufacturer": "Siemens", "model": "ABC-123", "serial_number": "345345345", "latitude": "54.443567", "longitude": "-23.312543", "energy_unit": "kilowatt_hour", "is_accumulated": true }, "measuredEnergy": [{"energy": 390, "measurement_time": "2018-03-15T16:30:00+00:00"}, {"energy": 400, "measurement_time": "2018-03-15T18:30:00+00:00"} ] }'
        }
        data = json.loads(raw[url])
        return self._parse_source(str(raw), data)


class BondAPIv1TestDevice2(BondAPIv1):
    """
    Data parsing test fixture
    """

    def _reach_source(self, url) -> (str, dict):
        raw = {
            "base_url/produced/0": '{"count": 0, "previous": null, "next": "/second", "device": {"manufacturer": "Siemens", "model": "ABC-123", "serial_number": "345345345", "latitude": "54.443567", "longitude": "-23.312543", "energy_unit": "watt_hour", "is_accumulated": false }, "measuredEnergy": [{"energy": 12304, "measurement_time": "2018-03-15T10:30:00+00:00"}, {"energy": 8568, "measurement_time": "2018-03-15T12:30:00+00:00"}, {"energy": 63456, "measurement_time": "2018-03-15T14:30:00+00:00"} ] }',
            "base_url/second": '{"count": 1, "previous": "/first", "next": null, "device": {"manufacturer": "Siemens", "model": "ABC-123", "serial_number": "345345345", "latitude": "54.443567", "longitude": "-23.312543", "energy_unit": "watt_hour", "is_accumulated": false }, "measuredEnergy": [{"energy": 0, "measurement_time": "2018-03-15T16:30:00+00:00"}, {"energy": 265, "measurement_time": "2018-03-15T18:30:00+00:00"} ] }'
        }
        data = json.loads(raw[url])
        return self._parse_source(str(raw), data)


class BondAPIv1TestDevice3(BondAPIv1):
    """
    Data parsing test fixture
    """

    def _reach_source(self, url) -> (str, dict):
        raw = {
            "base_url/produced/0": '{"count": 0, "previous": null, "next": null, "device": {"manufacturer": "Siemens", "model": "ABC-123", "serial_number": "345345345", "latitude": "54.443567", "longitude": "-23.312543", "energy_unit": "megawatt_hour", "is_accumulated": false }, "measuredEnergy": [{"energy": 12304, "measurement_time": "2018-03-15T10:30:00+00:00"}, {"energy": 8568, "measurement_time": "2018-03-15T12:30:00+00:00"}, {"energy": 6, "measurement_time": "2018-03-15T14:30:00+00:00"} ] }'
        }
        data = json.loads(raw[url])
        return self._parse_source(str(raw), data)


if __name__ == '__main__':
    d1 = BondAPIv1TestDevice1("base_url", "produced", 0)
    energy = d1.read_state()

    d1 = BondAPIv1TestDevice2("base_url", "produced", 0)
    energy = d1.read_state()

    d1 = BondAPIv1TestDevice3("base_url", "produced", 0)
    energy = d1.read_state()
