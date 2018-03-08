from core.input.eumel import DataLogger
from test.abstract import VerboseTest, EnergyDataTest


class EumelTest(VerboseTest):

    def setUp(self):
        self.meter = DataLogger('http://sarnau5myhome.spdns.de:8002/', self.usr, self.pwd)

    def simple(self):
        energy_data_test = EnergyDataTest()
        energy_data_test.simple(self.meter.read_state())

    def extended(self):
        energy_data_test = EnergyDataTest()
        energy_data_test.extended(self.meter.read_state())
