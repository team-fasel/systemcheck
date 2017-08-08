# -*- coding: utf-8 -*-

""" Generic UI Widgets


"""

# define authorship information
__authors__     = ['Lars Fasel']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2017'
__license__     = 'MIT'

import systemcheck.systems.generic.gui.widgets
from systemcheck.gui.widgets.widgets import TreeView
from PyQt5 import QtCore, QtWidgets

class SystemTreeView(TreeView):
    """ A Generic QTreeView for systems """

    def __init__(self, parent=None):
        super().__init__(parent)




