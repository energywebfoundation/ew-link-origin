import time

from core.abstract.input import CarbonEmissionData
from core.input.carbonemission import Wattime
from core.input.eumel import DataLogger
from core.input.simulator import EnergyMeter
from test.abstract import VerboseTest, EnergyDataTest


class EnergyMeterTest(VerboseTest):

    def setUp(self):
        self.meter = EnergyMeter()
        VerboseTest.setUp(self)

    def simple(self):
        energy_data_test = EnergyDataTest()
        energy_data_test.simple(self.meter.read_state())

    def extended(self):
        energy_data_test = EnergyDataTest()
        energy_data_test.extended(self.meter.read_state())
        state_one = self.meter.read_state()
        time.sleep(1)
        state_two = self.meter.read_state()
        self.assertTrue(state_one.measurement_epoch < state_two.measurement_epoch)
        self.assertTrue(state_one.accumulated_power < state_two.accumulated_power)
        self.assertNotEqual(state_one.raw, state_two.raw)


class WattimeTest(VerboseTest):

    def setUp(self):
        self.meter = Wattime()
        VerboseTest.setUp(self)

    def simple(self):
        self.assertIsInstance(self.meter.read_state('National+Grid'), CarbonEmissionData)

    def extended(self):
        # TODO: Add all methods and check outputs against api doc.
        pass


class EumelTest(VerboseTest):

    def __init__(self, ip, user, password):
        self.ip = ip
        self.usr = user
        self.pwd = password

    def setUp(self):
        self.meter = DataLogger(self.ip, self.usr, self.pwd)
        VerboseTest.setUp(self)

    def simple(self):
        self.assertIsInstance(self.meter.read_state('National+Grid'), CarbonEmissionData)

    def extended(self):
        # TODO: Add all methods and check outputs against api doc.
        pass
