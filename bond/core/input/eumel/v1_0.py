import calendar
import datetime
import requests

from xml.etree import ElementTree
from core.abstract.input import EnergyDataSource, EnergyData, Device


class DataLoggerV1(EnergyDataSource):
    """
    Eumel DataLogger api access implementation
    """

    def __init__(self, ip, user, password):
        """
        :param ip: Data loggers network IP
        :param user:
        :param password:
        """
        self.eumel_api_url = ip + '/rest'
        self.auth = (user, password)

    def read_state(self, path=None) -> EnergyData:
        # raw
        if path:
            tree = ElementTree.parse('test_examples/EumelXMLOutput.xml')
            with open(path) as file:
                raw = file.read()
        else:
            http_packet = requests.get(self.eumel_api_url, auth=self.auth)
            raw = http_packet.content.decode()
            tree = ElementTree.fromstring(raw)
        tree_root = tree.getroot()
        tree_header = tree_root[0].attrib
        tree_leaves = {child.attrib['id']: child.text for child in tree_root[0][0]}
        # device
        device = Device(
            manufacturer=tree_header['man'],
            model=tree_header['mod'],
            serial_number=tree_header['sn'],
            geolocation=None)
        # accumulated power in Wh
        accumulated_power = int(float(tree_leaves['TotWhImp']))
        # access_epoch
        now = datetime.datetime.now().astimezone()
        access_epoch = calendar.timegm(now.timetuple())
        # measurement epoch
        measurement_timestamp = datetime.datetime.strptime(tree_header['t'], "%Y-%m-%dT%H:%M:%S%z")
        measurement_epoch = calendar.timegm(measurement_timestamp.timetuple())
        return EnergyData(device=device, access_epoch=access_epoch, raw=str(raw), accumulated_energy=accumulated_power,
                          measurement_epoch=measurement_epoch)


