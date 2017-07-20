# -*- coding: utf-8 -*-

""" Configuration

This file sets up the global configuration for the system check application


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
from systemcheck.utils import get_absolute_systemcheck_path

import os


CONFIG = ConfigParser()
path_to_settings=os.path.join(get_absolute_systemcheck_path(), 'settings.ini')

CONFIG.read(path_to_settings)
CONFIG['application']['absolute_path']=get_absolute_systemcheck_path()



