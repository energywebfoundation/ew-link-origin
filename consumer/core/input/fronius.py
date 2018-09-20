import calendar
import datetime
from xml.etree import ElementTree

import requests

from core.abstract.input import EnergyDataSource, EnergyData, Device


class FroniusV1(EnergyDataSource):
    """
    Fronius solar plant integration via the Fronius API
    """

    def __init__(self, ip, device_id, user=None, password=None):
        self.api_url = ip + '/solar_api/v1/GetInverterRealtimeData.cgi'
        self.device_id = device_id
        self.auth = (user, password)

    def read_state(self) -> EnergyData:
        # raw
        raw, data = self._reach_source()
        # device
        device_meta = {
            'manufacturer': 'Loxone',
            'model': 'Miniserver',
            'serial_number': 'Unknown',
            'geolocation': ('Unknown', 'Unknown')
        }
        device = Device(**device_meta)
        # accumulated power in Wh
        accumulated_power = int(data['Body']['Data']['TOTAL_ENERGY']['Value']) * pow(10, -6)
        # access_epoch
        now = datetime.datetime.now().astimezone()
        access_epoch = calendar.timegm(now.timetuple())
        # measurement epoch
        measurement_timestamp = data['Head']['Timestamp'][:-6]
        measurement_timestamp = datetime.datetime.strptime(measurement_timestamp, "%Y-%m-%dT%H:%M:%S")
        measurement_epoch = calendar.timegm(measurement_timestamp.timetuple())
        return EnergyData(device=device, access_epoch=access_epoch, raw=raw, accumulated_power=accumulated_power,
                          measurement_epoch=measurement_epoch)

    def _reach_source(self) -> (str, dict):
        marginal_query = {
            'Scope': 'Device',
            'DeviceId': self.device_id,
            'DataCollection': 'CumulationInverterData'  # 3PInverterData CommonInverterData CumulationInverterData
        }
        http_packet = requests.get(self.api_url, params=marginal_query, auth=self.auth)
        data = http_packet.json()
        raw = http_packet.content.decode()
        return raw, data


class FroniusV1Test(FroniusV1):
    """
    Data parsing test fixture
    """

    def _reach_source(self) -> (str, dict):
        data = {
            "Body": {
                "Data": {
                    "DAY_ENERGY": {
                        "Unit": "Wh",
                        "Value": 30066
                    },
                    "DeviceStatus": {
                        "ErrorCode": 0,
                        "LEDColor": 0,
                        "LEDState": 0,
                        "MgmtTimerRemainingTime": -1,
                        "StateToReset": False,
                        "StatusCode": 7
                    },
                    "PAC": {
                        "Unit": "W",
                        "Value": 4407
                    },
                    "TOTAL_ENERGY": {
                        "Unit": "Wh",
                        "Value": 25981765
                    },
                    "YEAR_ENERGY": {
                        "Unit": "Wh",
                        "Value": 6369768
                    }
                }
            },
            "Head": {
                "RequestArguments": {
                    "DataCollection": "CumulationInverterData",
                    "DeviceClass": "Inverter",
                    "DeviceId": "1",
                    "Scope": "Device"
                },
                "Status": {
                    "Code": 0,
                    "Reason": "",
                    "UserMessage": ""
                },
                "Timestamp": "2018-09-06T15:05:13+02:00"
            }
        }
        raw = str(data)
        return raw, data


class Loxone(EnergyDataSource):
    """
    Fronius solar plant integration via the Loxone Miniserver
    """

    def __init__(self, ip, source, user=None, password=None):
        if source not in ('Produced', 'Consumed'):
            raise AssertionError
        self.api_url = '{}/dev/sps/io/{}/'.format(ip, source)
        self.auth = (user, password)

    def read_state(self) -> EnergyData:
        # raw
        raw, data = self._reach_source()
        # device
        device_meta = {
            'manufacturer': data['manufacturer'],
            'model': data['model'],
            'serial_number': data['serial_number'],
            'geolocation': (data['latitude'], data['longitude'])
        }
        device = Device(**device_meta)
        # accumulated power in KWh to Wh
        accumulated_power = int(float(data['accumulated_power']) * pow(10, 3))
        # access_epoch
        now = datetime.datetime.now().astimezone()
        access_epoch = calendar.timegm(now.timetuple())
        # measurement epoch
        # TODO: ask them to send it as string to parse as json
        measurement_epoch = access_epoch
        return EnergyData(device=device, access_epoch=access_epoch, raw=raw, accumulated_power=accumulated_power,
                          measurement_epoch=measurement_epoch)

    def _reach_source(self) -> (str, dict):
        http_packet = requests.get(self.api_url, auth=self.auth)
        raw = http_packet.content.decode()
        tree = ElementTree.fromstring(raw)
        tree_root = tree.attrib
        if int(tree_root['Code']) > 200:
            raise EnvironmentError
        data = tree_root['value'][10:-50].replace('"measuredEnergy":[{', '').replace('"', '')
        data = [tuple(pair.split(':')) for pair in data.split(',')]
        return raw, {k: v for k, v in data}


class LoxoneTest(Loxone):
    """
    Data parsing test fixture
    """

    def _reach_source(self) -> (str, dict):
        raw = '"device":{"manufacturer":"Siemens","model":"TD-3511","serial_number":"123456","latitude":"48.245","longitude":"14.039","measuredEnergy":[{"accumulated_power":1.111111,"measurement_time":2018-09-14T18:01:51+02:00}]}"'
        data = raw[10:-50].replace('"measuredEnergy":[{', '').replace('"', '')
        data = [tuple(pair.split(':')) for pair in data.split(',')]
        return raw, {k: v for k, v in data}
