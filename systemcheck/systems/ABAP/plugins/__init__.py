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

from systemcheck.systems.ABAP.plugins.plugin_types import CheckAbapCountTableEntries, CheckAbapFoundationPlugin, \
    CheckAbapPlugin, CheckAbapRsusr002Plugin, CheckAbapRsusr020Plugin, CheckAbapRsusr200Plugin

