from core.abstract.input import CarbonEmissionData
from core.input.carbonemission import Wattime
from test.abstract import VerboseTest, CarbonEmissionDataTest


class WattimeTest(VerboseTest):

    def setUp(self):
        self.meter = Wattime('energyweb', 'en3rgy!web', 24)
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
