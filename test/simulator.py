import unittest

import time

from core.abstract.input import EnergyData, CarbonEmissionData
from core.input.simulator import EnergyMeter


class EnergyDataTest(unittest.TestCase):

    def simple(self, energy_data):
        self.assertIsInstance(energy_data, EnergyData, 'wrong data type')

    def extended(self, energy_data):
        self.simple(energy_data)
        # Todo: Add data type for each param and quality asserts


class CarbonEmissionInputTest(unittest.TestCase):

    def simple(self, carbon_emission_data):
        self.assertIsInstance(carbon_emission_data, CarbonEmissionData, 'wrong data type')

    def extended(self, carbon_emission_data):
        self.simple(carbon_emission_data)
        # Todo: Add data type for each param and quality asserts


class EnergyMeterTest(unittest.TestCase):

    def setUp(self):
        self.meter = EnergyMeter()

    def simple(self):
        energy_data_test = EnergyDataTest()
        energy_data_test.simple(self.meter.read_state())

    def extended(self):
        energy_data_test = EnergyDataTest()
        energy_data_test.extended(self.meter.read_state())
        state_one = self.meter.read_state()
        time.sleep(1)
        state_two = self.meter.read_state()
        self.assertTrue(state_one.measurement_timestamp < state_two.measurement_timestamp)
        self.assertTrue(state_one.accumulated_power < state_two.accumulated_power)
        self.assertNotEqual(state_one.raw, state_two.raw)
