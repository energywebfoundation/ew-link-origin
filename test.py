import unittest

from test.simulator import EnergyMeterTest


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    test_suite = unittest.TestSuite()
    test_suite.addTest(EnergyMeterTest('extended'))
    runner.run(test_suite)
