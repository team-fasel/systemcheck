# -*- coding: utf-8 -*-

""" Generic UI Models


"""

# define authorship information
__authors__ = ['Lars Fasel']
__author__ = ','.join(__authors__)
__credits__ = []
__copyright__ = 'Copyright (c) 2017'
__license__ = 'MIT'



import logging
from typing import Any

from PyQt5 import QtCore, QtGui, QtWidgets

class SettingsModel(QtCore.QAbstractItemModel):

    def __init__(self, abstractItem):
        super().__init__()
        self.logger = logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))
        self._abstractItem = abstractItem


    def columnCount(self, parent=None, *args, **kwargs)->int:

        return self._abstractItem._qt_column_count()

    def rowCount(self, parent=None, *args, **kwargs)->int:

        return 1

    def data(self, index: QtCore.QModelIndex, role: int)->Any:
        column = index.column()
        if not index.isValid():
            return False

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return self._abstractItem._qt_data_colnr(index.column())

    def flags(self, index:QtCore.QModelIndex)->int:
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

    def setData(self, index:QtCore.QModelIndex, value: Any, role=QtCore.Qt.EditRole)->bool:
        """ setData Method to make the model modifiable """

        if index.isValid():
            if role == QtCore.Qt.EditRole:
                self._abstractItem._qt_set_value_by_colnr(index.column(), value)

            return True
        return False

    def index(self, row:int, column:int, parent=None)->QtCore.QModelIndex:

        index = self.createIndex(0, column, QtCore.QModelIndex())

        return index

    def parent(self):
        return QtCore.QModelIndex()
