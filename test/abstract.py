import datetime
import unittest

from core.abstract.input import Device, EnergyData, CarbonEmissionData


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

        self.assertIsInstance(device.geolocation, float)


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