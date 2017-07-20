# -*- coding: utf-8 -*-

""" ABAP Specific utilities of the systemcheck Application



"""

# define authorship information
__authors__     = ['Lars Fasel']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2017'
__license__     = 'MIT'


from systemcheck.systems.ABAP.utils.connection import Connection
from systemcheck.systems.ABAP.utils.mock_connection import MockConnection
from systemcheck.systems.ABAP.utils.snc import get_snc_name
