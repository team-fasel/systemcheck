# -*- coding: utf-8 -*-

""" Test to load systemcheck


"""

# define authorship information
__authors__     = ['Lars Fasel']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2017'
__license__     = 'MIT'

# maintanence information
__maintainer__  = 'Lars Fasel'
__email__       = 'systemcheck@team-fasel.com'


import unittest
from config_for_test import TEST_CONFIG

class TestLoadConfig(unittest.TestCase):

    def test_absolute_path(self):
        from systemcheck import CONFIG

        self.assertEqual(CONFIG['application']['absolute_path'], TEST_CONFIG['application']['absolute_path'])

