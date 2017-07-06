# -*- coding: utf-8 -*-

""" Generic Utiltities

This file contains some generic utilities that are used across the application.



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
import sys
import os

def main_is_frozen():
    """ Determines whether scripts are executed using pyInstaller or actual scripts.
    :return: True if using py2exe or pyinstaller or False if using scripts"""

    return (hasattr(sys, '_MEIPASS'))


def get_absolute_path(relative_path):
    """ Returns the absolute path for the relative path taking into account the freeze status """

    if main_is_frozen():
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(sys.argv[0]), relative_path)


def get_absolute_systemcheck_path(relative_path=None):
    """ Returns the absolute path for the relative path taking into account the freeze status """
    import systemcheck
    if main_is_frozen():
        path1=sys._MEIPASS
    else:
        path1=os.path.dirname(systemcheck.__file__)

    if relative_path is None:
        return path1
    return os.path.join(path1, relative_path)