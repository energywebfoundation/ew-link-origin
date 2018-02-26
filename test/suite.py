import unittest

from test.simulator import EnergyMeterTest


def suite():
    suite = unittest.TestSuite()
    suite.addTest(EnergyMeterTest('extended'))
    suite.countTestCases()
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
