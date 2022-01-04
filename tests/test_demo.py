import unittest
import pytest
import sys
from util4tests import enable_test_logging

from pykg2tbl import MyModel, log


class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

    def test_modelError(self):
        m = MyModel()
        self.assertAlmostEqual(m.my_method(10), 0.01)  # when comparing floats one should allow for some margin
        with self.assertRaises(AssertionError):        # to trigger and test for intended failure
            m.my_method(200)


if __name__ == "__main__":
    enable_test_logging()
    log.info(
        f"Running tests in {__file__} with -v(erbose) and -s(no stdout capturing) flags " +
        "logging controlled by logconf.yml user-specified through (.)env var ${PYTEST_LOGCONF}")
    sys.exit(pytest.main(["-v", "-s",  __file__]))
