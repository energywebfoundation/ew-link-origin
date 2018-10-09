import os
import re
import csv
import locale
import datetime
import calendar
import paramiko

from collections import namedtuple
from core.abstract.input import EnergyDataSource, EnergyData, Device


class PTTftp(EnergyDataSource):
    """
    PTT solar plant integration. Servers on Azure in diff subnets. Needs VPN access.

    """

    def __init__(self, host: str, port: int, usr: str, pwd: str, site_exp: str):
        # TODO
        self.host = host
        self.port = port
        self.usr = usr
        self.pwd = pwd
        self.site_exp = site_exp
        csv.register_dialect('ptt', delimiter=';', quoting=csv.QUOTE_NONE)

    def read_state(self) -> EnergyData:
        # raw
        raw, file_list = self._reach_source()
        # device
        device_meta = {
            'manufacturer': 'Unknown',
            'model': 'Unknown',
            'serial_number': 'Unknown',
            'geolocation': ('Unknown', 'Unknown')
        }
        device = Device(**device_meta)
        # accumulated power in Wh
        accumulated_power = int(sum(locale.atof(power.p_minus) for power in raw if power.p_minus))
        # access_epoch
        now = datetime.datetime.now().astimezone()
        access_epoch = calendar.timegm(now.timetuple())
        # measurement epoch
        measurement_timestamp = datetime.datetime.strptime(raw[-1].timestamp, "%Y-%m-%dT%H:%M:%S")
        measurement_epoch = calendar.timegm(measurement_timestamp.timetuple())
        self._del_files(file_list)
        return EnergyData(device=device, access_epoch=access_epoch, raw=str(raw), accumulated_energy=accumulated_power,
                          measurement_epoch=measurement_epoch)

    def _reach_source(self):
        file_list = self._get_files()
        raw = self._parse_data(file_list)
        return raw, file_list

    def _get_files(self) -> [tuple]:
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

    def _del_files(self, file_list: [tuple]):
        # remove local files
        [os.remove(file_name_tuple[1]) for file_name_tuple in file_list if os.path.isfile(file_name_tuple[1])]
        # remove remote files
        transport = paramiko.Transport((self.host, self.port))
        transport.connect(username=self.usr, password=self.pwd)
        sftp = paramiko.SFTPClient.from_transport(transport)
        [sftp.remove(file_name_tuple[0]) for file_name_tuple in file_list]
        transport.close()

    @staticmethod
    def _parse_data(file_list: [tuple]):
        twl_data = []
        for file_name_tuple in file_list:
            TWLData = namedtuple('TWLData', 'timestamp, p_plus, pre_plus, p_minus, pre_minus')
            raw_parsed_file = [l for l in map(TWLData._make, csv.reader(open(file_name_tuple[1]), dialect='ptt'))]
            twl_data.extend(raw_parsed_file[5:])
        return twl_data


class AG(PTTftp):
        # TODO

    def __init__(self, host: str, port: int, usr: str, pwd: str):
        self.host = host
        self.port = port
        self.usr = usr
        self.pwd = pwd
        super().__init__(host, port, usr, pwd, r'TWL_AG_PV')


class PTTftpTest(PTTftp):

    def _reach_source(self):
        # TODO
        file_list = ''
        raw = ''
        return raw, file_list
