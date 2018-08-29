import unittest

from test.carbonemission import WattimeTest
from test.simulator import EnergyMeterTest


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    test_suite = unittest.TestSuite()
    test_suite.addTest(EnergyMeterTest('extended'))
    test_suite.addTest(WattimeTest('extended'))
    runner.run(test_suite)
