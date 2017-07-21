# -*- coding: utf-8 -*-

""" Generic UI Widgets


"""

# define authorship information
__authors__     = ['Lars Fasel']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2017'
__license__     = 'MIT'

from PyQt5 import QtWidgets, QtCore, QtGui
from systemcheck.gui.models import CredentialModel
from systemcheck.resources import icon_rc
from systemcheck import SESSION

class CredentialsEditor(QtWidgets.QWidget):

    def __init__(self):

        super().__init__()

        layout=QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0,  0, 0)
        layout.setSpacing(0)
        self.combo = QtWidgets.QComboBox()
        self.edit_btn = QtWidgets.QPushButton()
        self.edit_btn.setToolTip('Edit the displayed credential')
        self.edit_btn.setIcon(QtGui.QIcon(":/EditUserMale"))
        self.add_btn = QtWidgets.QPushButton()
        self.add_btn.setToolTip('Add a new credential')
        self.add_btn.setIcon(QtGui.QIcon(":/AddUserMale"))
        self.updatePassword_btn = QtWidgets.QPushButton()
        self.updatePassword_btn.setToolTip("Update Stored Password for shown credential")
        self.updatePassword_btn.setIcon(QtGui.QIcon(":/Password"))

        layout.addWidget(self.combo)
        layout.addWidget(self.edit_btn)
        layout.addWidget(self.add_btn)
        layout.addWidget(self.updatePassword_btn)

        self.credentials_model = CredentialModel()

        self.setLayout(layout)
        self.show()

    def setModel(self, model):
        pass

    def createEditor(self, parent, option, index):
        pass