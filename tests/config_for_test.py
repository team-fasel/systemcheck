# -*- coding: utf-8 -*-

""" Setup Config Items for Testing



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


from configparser import ConfigParser
from pprint import pprint

TEST_CONFIG=ConfigParser()
TEST_CONFIG.read('settings.ini')
