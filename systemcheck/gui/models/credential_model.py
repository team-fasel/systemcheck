# -*- coding: utf-8 -*-

""" A QAbstractTable Model for the credentials.


"""

# define authorship information
__authors__     = ['Lars Fasel']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2017'
__license__     = 'MIT'


from PyQt5 import QtCore, QtWidgets
from systemcheck.model.credentials import Credential
from sqlalchemy import inspect, asc, desc
import logging

class CredentialModel(QtCore.QAbstractTableModel):

    def __init__(self, abstracttable):
        self.logger = logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))
        super().__init__()
        self._abstracttable = abstracttable
        self.session = inspect(self._abstracttable).session
        self._data = self.session.query(Credential).all()

    def rowCount(self, parent):
        session = inspect(self._abstracttable).session
        rowcount = session.query(Credential).count()
        return rowcount

    def columnCount(self, parent):
        return self._abstracttable._visible_column_count()

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != QtCore.Qt.DisplayRole:
            return None

        credential_record=self._data[index.row()]
        value = credential_record._value_by_visible_colnr(index.column())
        return value

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[col]
        return None

    def sort(self, col, order):
        """sort table by given column number col"""

        self.layoutAboutToBeChanged.emit()
        #TODO: doesn't look nice. OK for now, but needs to be dynamic to make a reusable QAbstractTableModel.
        if order == QtCore.Qt.AscendingOrder:
            if col == 0:
                self._data = self.session.query(Credential).all().order_by(asc(Credential.application))
            if col == 1:
                self._data = self.session.query(Credential).all().order_by(asc(Credential.description))
            if col == 2:
                self._data = self.session.query(Credential).all().order_by(asc(Credential.username))
            if col == 3:
                self._data = self.session.query(Credential).all().order_by(asc(Credential.type))
        elif order == QtCore.Qt.DescendingOrder:
            if col == 0:
                self._data = self.session.query(Credential).all().order_by(desc(Credential.application))
            if col == 1:
                self._data = self.session.query(Credential).all().order_by(desc(Credential.description))
            if col == 2:
                self._data = self.session.query(Credential).all().order_by(desc(Credential.username))
            if col == 3:
                self._data = self.session.query(Credential).all().order_by(desc(Credential.type))
        self.layoutChanged.emit()

