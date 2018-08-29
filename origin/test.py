import time

import datetime
import unittest

from bond.origin import origin as input_simulator, origin as input_co2, origin as input_eumel

from core.input import Device, EnergyData, CarbonEmissionData


class VerboseTest(unittest.TestCase):

    def setUp(self):
        print("Test: ", self.__class__.__name__)
        print("Case: ", self._testMethodName)


class DeviceTest(unittest.TestCase):

    def simple(self, device):
        self.assertIsInstance(device, Device, 'Not a device instance.')

    def extended(self, device):
        self.simple(device)
        self.assertIsInstance(device.manufacturer, str)
        self.assertTrue(len(str(device.manufacturer)) > 3)

        self.assertIsInstance(device.model, str)
        self.assertTrue(len(str(device.model)) > 4)

        self.assertIsInstance(device.serial_number, str)
        self.assertTrue(len(str(device.serial_number)) > 2)

        self.assertIsInstance(device.geolocation, tuple)
        self.assertIsInstance(device.geolocation[0], float)
        self.assertIsInstance(device.geolocation[1], float)


class EnergyDataTest(unittest.TestCase):

    def __init__(self):
        self.device_test = DeviceTest()
        self.now = datetime.datetime.now()
        super().__init__()

    def simple(self, energy_data):
        self.assertIsInstance(energy_data, EnergyData, 'Not energy data instance.')
        self.device_test.simple(energy_data.device)

    def extended(self, energy_data):
        self.simple(energy_data)
        self.device_test.extended(energy_data.device)

        access_datetime = datetime.datetime.fromtimestamp(energy_data.access_epoch)
        self.assertIsInstance(access_datetime, datetime.datetime)
        self.assertTrue(self.now.year - 1 <= access_datetime.year)
        self.assertTrue(self.now.year + 1 >= access_datetime.year)

        self.assertIsInstance(energy_data.raw, str)
        self.assertTrue(len(str(energy_data.raw)) > 10)

        self.assertIsInstance(energy_data.accumulated_power, int)
        self.assertTrue(len(str(energy_data.accumulated_power)) > 1)

        measurement_datetime = datetime.datetime.fromtimestamp(energy_data.measurement_epoch)
        self.assertIsInstance(measurement_datetime, datetime.datetime)
        self.assertTrue(self.now.year - 1 <= measurement_datetime.year)
        self.assertTrue(self.now.year + 1 >= measurement_datetime.year)


class CarbonEmissionDataTest(unittest.TestCase):

    def __init__(self):
        self.now = datetime.datetime.now()
        super().__init__()

    def simple(self, carbon_emission_data):
        self.assertIsInstance(carbon_emission_data, CarbonEmissionData, 'Not a carbon emission data instance.')

    def extended(self, carbon_emission_data):
        self.simple(carbon_emission_data)

        access_datetime = datetime.datetime.fromtimestamp(carbon_emission_data.access_epoch)
        self.assertIsInstance(access_datetime, datetime.datetime)
        self.assertTrue(self.now.year - 1 <= access_datetime.year)
        self.assertTrue(self.now.year + 1 >= access_datetime.year)

        self.assertIsInstance(carbon_emission_data.raw, str)
        self.assertEquals(len(str(carbon_emission_data.raw)) > 10)

        self.assertIsInstance(carbon_emission_data.accumulated_co2, int)
        self.assertEquals(len(str(carbon_emission_data.accumulated_co2)) > 1)

        measurement_datetime = datetime.datetime.fromtimestamp(carbon_emission_data.measurement_epoch)
        self.assertIsInstance(measurement_datetime, datetime.datetime)
        self.assertTrue(self.now.year - 1 <= measurement_datetime.year)
        self.assertTrue(self.now.year + 1 >= measurement_datetime.year)


class EnergyMeterTest(VerboseTest):

    def setUp(self):
        self.meter = input_simulator.EnergyMeter()
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
        self.meter = input_co2.Wattime('usr', 'pwd', 24)
        VerboseTest.setUp(self)

    def simple(self):
        self.assertIsInstance(self.meter.read_state('National+Grid'), CarbonEmissionData)

    def extended(self):
        self.simple()
        co2_data_test = CarbonEmissionDataTest()
        co2_data_test.extended(self.meter.read_state('National+Grid'))
        co2_data_test.extended(self.meter.read_state('FR'))
        self.assertRaises(self.meter.read_state('BR'))
        # TODO: Add all methods and check outputs against api doc.
        pass


class Eumelv1Test(VerboseTest):

    def setUp(self):
        self.meter = input_eumel.DataLoggerV1('', self.usr, self.pwd)

    def simple(self):
        energy_data_test = EnergyDataTest()
        energy_data_test.simple(self.meter.read_state())

    def extended(self):
        energy_data_test = EnergyDataTest()
        energy_data_test.extended(self.meter.read_state())


class Eumelv2d2d1Test(VerboseTest):

    def setUp(self):
        self.meter = input_eumel.DataLoggerV2d1d1('', self.usr, self.pwd)

    def simple(self):
        energy_data_test = EnergyDataTest()
        energy_data_test.simple(self.meter.read_state())

    def extended(self):
        energy_data_test = EnergyDataTest()
        energy_data_test.extended(self.meter.read_state())
