import os
import re
import csv
import locale
import datetime
import paramiko

from collections import namedtuple
from core.abstract import CEST
from core.input import EnergyDataSource, EnergyData, Device


class TWLFile(EnergyDataSource):
    
    def __init__(self, host: str, port: int, usr: str, pwd: str, site_exp: str):
        self.host = host
        self.port = port
        self.usr = usr
        self.pwd = pwd
        self.site_exp = site_exp

    def read_state(self) -> EnergyData:
        file_list = self.__get_files()
        raw = self.__parse_data(file_list)
        device_meta = {
            'manufacturer': 'Unknown',
            'model': 'Unknown',
            'serial_number': 'Unknown',
            'geolocation': (0, 0)
        }
        device = Device(**device_meta)
        locale.setlocale(locale.LC_NUMERIC, 'de_DE')
        accumulated_power = sum(locale.atof(twl_data.p_minus) for twl_data in raw if twl_data.p_minus) * pow(10, 3)
        locale.setlocale(locale.LC_NUMERIC, '')
        now = datetime.datetime.now().astimezone()
        access_timestamp = now.isoformat()
        measurement_timestamp = datetime.datetime.strptime(raw[-1].timestamp, "%Y-%m-%d %H:%M:%S")
        measurement_timestamp = measurement_timestamp.replace(tzinfo=CEST()).isoformat()
        self.__del_files(file_list)
        return EnergyData(device, access_timestamp, raw, accumulated_power, measurement_timestamp)

    def __get_files(self) -> [tuple]:
        """
        Log in to sftp service, filter files by date and site, copy them to local, delete them in remote, return local
        file list names with path.
        :return: Downloaded file list names with path.
        """
        transport = paramiko.Transport((self.host, self.port))
        transport.connect(username=self.usr, password=self.pwd)
        sftp = paramiko.SFTPClient.from_transport(transport)
        raw_file_list = sftp.listdir(path='./twl')
        site_regex = re.compile(self.site_exp)
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        date_regex = re.compile(r'^({})'.format(yesterday.strftime('%Y%m%d')))
        file_list = list(filter(site_regex.search, filter(date_regex.search, raw_file_list)))
        file_list_tuple = [('./twl/{}'.format(file_name), '/tmp/{}'.format(file_name)) for file_name in file_list]
        [sftp.get(*file_name_pair) for file_name_pair in file_list_tuple]
        transport.close()
        return file_list_tuple

    def __del_files(self, file_list: [tuple]):
        # remove local files
        [os.remove(file_name_tuple[1]) for file_name_tuple in file_list if os.path.isfile(file_name_tuple[1])]
        # remove remote files
        transport = paramiko.Transport((self.host, self.port))
        transport.connect(username=self.usr, password=self.pwd)
        sftp = paramiko.SFTPClient.from_transport(transport)
        [sftp.remove(file_name_tuple[0]) for file_name_tuple in file_list]
        transport.close()

    @staticmethod
    def __parse_data(file_list: [tuple]):
        csv.register_dialect('twl', delimiter=';', quoting=csv.QUOTE_NONE)
        twl_data = []
        for file_name_tuple in file_list:
            TWLData = namedtuple('TWLData', 'timestamp, p_plus, pre_plus, p_minus, pre_minus')
            raw_parsed_file = [l for l in map(TWLData._make, csv.reader(open(file_name_tuple[1]),  dialect='twl'))]
            twl_data.extend(raw_parsed_file[5:])
        return twl_data


class AG(TWLFile):

    def __init__(self, host: str, port: int, usr: str, pwd: str):
        self.host = host
        self.port = port
        self.usr = usr
        self.pwd = pwd
        super().__init__(host, port, usr, pwd, r'TWL_AG_PV')


class Lager(TWLFile):

    def __init__(self, host: str, port: int, usr: str, pwd: str):
        self.host = host
        self.port = port
        self.usr = usr
        self.pwd = pwd
        super().__init__(host, port, usr, pwd, r'TWL_Lager_PV')


class Wasserwerk2(TWLFile):

    def __init__(self, host: str, port: int, usr: str, pwd: str):
        self.host = host
        self.port = port
        self.usr = usr
        self.pwd = pwd
        super().__init__(host, port, usr, pwd, r'TWL_Wasserwerk_2')


class Wasserwerk1a1(TWLFile):

    def __init__(self, host: str, port: int, usr: str, pwd: str):
        self.host = host
        self.port = port
        self.usr = usr
        self.pwd = pwd
        super().__init__(host, port, usr, pwd, r'TWL_Wasserwerk_1_PV_Anlage_1')


class Wasserwerk1a2(TWLFile):

    def __init__(self, host: str, port: int, usr: str, pwd: str):
        self.host = host
        self.port = port
        self.usr = usr
        self.pwd = pwd
        super().__init__(host, port, usr, pwd, r'TWL_Wasserwerk_1_PV_Anlage_2')
