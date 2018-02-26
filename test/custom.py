import unittest


class VerboseTest(unittest.TestCase):

    def setUp(self):
        print("Test: ", self.__class__.__name__)
        print("Case: ", self._testMethodName)
