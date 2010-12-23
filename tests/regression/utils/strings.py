import unittest
from djpcms.utils import force_str, stringtype


__all__ = ['TestUtilsStrings']


class TestUtilsStrings(unittest.TestCase):

    def test_force_str(self):
        ts = bytes('test string')
        self.assertEqual(force_str(ts),stringtype('test string'))
        
    