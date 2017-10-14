# -*- coding: utf-8 -*-

""" Generic Utilies and Helpers for the systemcheck Application

This package contains generic utilities and helpers. Generic means, they don't require
PyQt or any other system specific functionality.

"""

# define authorship information
__authors__     = ['Lars Fasel']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2017'
__license__     = 'MIT'


from .generic import get_absolute_path, get_absolute_systemcheck_path, Result, Fail, \
    get_lower_interval, get_user_attributes
from .sqlalchemy import get_or_create
