import calendar
import datetime
import requests

from core.abstract.input import EnergyDataSource, EnergyData, Device


class LoxoneV1(EnergyDataSource):
    """
    Fronius solar plant integration via the Loxone Miniserver
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
        accumulated_power = data['Body']['Data']['TOTAL_ENERGY']['Value'] * pow(10, -6)
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


class LoxoneV1Test(LoxoneV1):
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
