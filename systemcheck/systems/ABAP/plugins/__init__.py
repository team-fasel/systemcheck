# -*- coding: utf-8 -*-

""" Definition of ABAP specific Check Plugins

=
"""

# define authorship information
__authors__     = ['Lars Fasel']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2017'
__license__     = 'MIT'

import systemcheck.systems.ABAP.plugins.actions
from systemcheck.systems.ABAP.plugins.action_types import CheckAbapFoundationAction, \
    CheckAbapAction

