import time

from core.input.simulator import EnergyMeter
from test.custom import VerboseTest
from test.data import EnergyDataTest


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
