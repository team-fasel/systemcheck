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
from systemcheck.models.credentials import Credential
from systemcheck.config import CONFIG, SESSION
from sqlalchemy import inspect, asc, desc
import logging

class CredentialModel(QtCore.QAbstractTableModel):

    def __init__(self, session=None):

        self.logger = logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))
        super().__init__()
        self._abstracttable = Credential
        if session is None:
            self._session = SESSION
        else:
            self._session = session
        self._data = self._session.query(Credential).all()

    def rowCount(self, parent=QtCore.QModelIndex()):
        rowcount = self._session.query(Credential).count()
        return rowcount

    def columnCount(self, parent=QtCore.QModelIndex()):

        columns =  [colData
                for colData in Credential.__table__.columns
                if colData.info.get('qt_show')]

        return len(columns)

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
            return self._abstracttable._visible_headers()
        return None

    def sort(self, col, order):
        """sort table by given column number col"""

        self.layoutAboutToBeChanged.emit()
        #TODO: doesn't look nice. OK for now, but needs to be dynamic to make a reusable QAbstractTableModel.
        if order == QtCore.Qt.AscendingOrder:
            if col == 0:
                self._data = self.session.query(Credential).all().order_by(asc(Credential.id))
            if col == 1:
                self._data = self.session.query(Credential).all().order_by(asc(Credential.application))
            if col == 2:
                self._data = self.session.query(Credential).all().order_by(asc(Credential.description))
            if col == 3:
                self._data = self.session.query(Credential).all().order_by(asc(Credential.username))
            if col == 4:
                self._data = self.session.query(Credential).all().order_by(asc(Credential.type))
        elif order == QtCore.Qt.DescendingOrder:
            if col == 0:
                self._data = self.session.query(Credential).all().order_by(desc(Credential.id))
            if col == 1:
                self._data = self.session.query(Credential).all().order_by(desc(Credential.application))
            if col == 2:
                self._data = self.session.query(Credential).all().order_by(desc(Credential.description))
            if col == 3:
                self._data = self.session.query(Credential).all().order_by(desc(Credential.username))
            if col == 4:
                self._data = self.session.query(Credential).all().order_by(desc(Credential.type))
        self.layoutChanged.emit()

    def insertRows(self, position, count, parent=QtCore.QModelIndex()):
        self.beginInsertRows(parent, position, position + count - 1)

        while count:
            new_record=Credential(username = 'initial {}'.format(count),
                                  description = 'initial')
            self._session.add(new_record)
            count -= 1
        self.endInsertRows()

    def removeRows(self, position, count, parent=QtCore.QModelIndex()):
        self.beginRemoveRows(parent, position, position+count-1)

        for row in range(position, position+count):
            self._session.delete(self._data[row])

        self.endRemoveRows()
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        item = self._data[index.row()]
        item._set_value_by_visible_colnr(index.column(), value)
#        self.dataChanged.emit(index)
