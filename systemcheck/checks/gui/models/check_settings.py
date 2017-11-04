from PyQt5 import QtCore, QtWidgets, QtGui
import logging
from systemcheck import checks
import systemcheck.utils
from sqlalchemy import inspect
from typing import Any
from systemcheck.resources import icon_rc

class CheckSettingsModel(QtCore.QAbstractItemModel):

    def __init__(self, abstractItem):
        super().__init__()
        self.logger = logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))
        self._abstractItem = abstractItem


    def columnCount(self, parent=None, *args, **kwargs)->int:

        return self._abstractItem._visible_column_count()

    def rowCount(self, parent=None, *args, **kwargs)->int:

        return 1

    def data(self, index: QtCore.QModelIndex, role: int)->Any:
        column = index.column()
        if not index.isValid():
            return False

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            value = self._abstractItem._qt_data_colnr(index.column())
            return value

    def flags(self, index:QtCore.QModelIndex)->int:
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

    def setData(self, index:QtCore.QModelIndex, value: Any, role=QtCore.Qt.EditRole)->bool:
        """ setData Method to make the model modifiable """

        if index.isValid():
            if role == QtCore.Qt.EditRole:
                self._abstractItem._qt_set_value_by_colnr(index.column(), value)
                #self.dataChanged.emit(index, index)
            return True
        return False

    def index(self, row:int, column:int, parent=None)->QtCore.QModelIndex:

        index = self.createIndex(0, column, QtCore.QModelIndex())

        return index

    def parent(self):
        return QtCore.QModelIndex()


class CheckParameterTableModel(QtCore.QAbstractTableModel):

    def __init__(self, checknode=None, parent=None):
        super(CheckParameterTableModel, self).__init__(parent)
        self.__headings = []
        self.__checknode=checknode

    def alchemyObject(self):
        return self.__checknode

    def rowCount(self, index:QtCore.QModelIndex=QtCore.QModelIndex()):
        """ Returns the number of rows the model holds. """
        nrows = self.__checknode
        return self.__checknode._parameter_count()

    def columnCount(self, index:QtCore.QModelIndex=QtCore.QModelIndex()):
        """ Returns the number of columns the model holds. """
        if self.rowCount():
            return 1


    def data(self, index, role:int=QtCore.Qt.DisplayRole):
        """ Depending on the index and role given, return data. If not
            returning data, return None (PySide equivalent of QT's
            "invalid QVariant").
        """
        if not index.isValid():
            return None

        rowNr=index.row()
        colNr=index.column()

        if not 0 <= rowNr < len(self.__checknode.params):
            return None

        if role == QtCore.Qt.DisplayRole:
            param = self.__checknode.params[rowNr]
            column = param.__qtmap__[colNr]

            value = getattr(param, column.name)
            return value

        return None

    def headerData(self, section, orientation:int, role:int=QtCore.Qt.DisplayRole):
        """ Set the headers to be displayed. """
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return 'Parameter Set'

        return None

    def insertRows(self, position:int, rows:int=1, index:QtCore.QModelIndex=QtCore.QModelIndex()):
        """ Insert a row into the model. """



        self.beginInsertRows(QtCore.QModelIndex(), position, position + rows - 1)

        check_alc_object = type(self.__checknode)
        objectClass = check_alc_object.params.info.get('rel_class')

        for row in range(rows):
            if objectClass:
                object = objectClass(param_set_name='< New >')
                self.__checknode.params.insert(position + row, object)

        self.endInsertRows()
        return True

    def removeRows(self, position, rows=1, index:QtCore.QModelIndex=QtCore.QModelIndex()):
        """ Remove a row from the model. """
        self.beginRemoveRows(QtCore.QModelIndex(), position, position + rows - 1)

        del self.__checknode.params[position:position + rows]
        self.__checknode._commit()

        self.endRemoveRows()
        return True

    def setData(self, index, value, role=QtCore.Qt.EditRole):

        if index.isValid():
            if role == QtCore.Qt.EditRole:
                rowNr=index.row()
                colNr=index.column()

                param = self.__checknode.params[rowNr]
                param._qt_set_value_by_colnr(colnr=colNr, value=value)


    def flags(self, index):
        """ Set the item flags at the given index. Seems like we're
            implementing this function just to see how it's done, as we
            manually adjust each tableView to have NoEditTriggers.
        """
        if index.isValid():
            return QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled


class CheckRestrictionModel(QtCore.QAbstractTableModel):

    def __init__(self, checknode=None, parent=None):
        super().__init__()
        self.__headings = []
        self.__checknode=checknode

    def alchemyObject(self):
        return self.__checknode

    def rowCount(self, index:QtCore.QModelIndex=QtCore.QModelIndex()):
        """ Returns the number of rows the model holds. """
        nrows = self.__checknode._restriction_count()
        return nrows


    def columnCount(self, index:QtCore.QModelIndex=QtCore.QModelIndex()):
        return 6


    def data(self, index, role:int=QtCore.Qt.DisplayRole):
        """ Depending on the index and role given, return data. If not
            returning data, return None (PySide equivalent of QT's
            "invalid QVariant").
        """
        if not index.isValid():
            return None

        rowNr=index.row()
        colNr=index.column()

        if not 0 <= rowNr < len(self.__checknode.params):
            return None

        if role == QtCore.Qt.DisplayRole:
            restriction = self.__checknode.restrictions[rowNr]
            column = restriction.__qtmap__[colNr]

            value = getattr(restriction, column.name)
            return value

        return None

    def headerData(self, section, orientation:int, role:int=QtCore.Qt.DisplayRole):
        """ Set the headers to be displayed. """
#        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
#            return 'Parameter Set'

        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:

            nodetype=inspect(type(self.__checknode)).relationships['restrictions'].mapper.class_
            column=nodetype.__qtmap__[section]
            return column.info.get('qt_label')


    def insertRows(self, position:int, rows:int=1, index:QtCore.QModelIndex=QtCore.QModelIndex()):
        """ Insert a row into the model. """

        node=inspect(type(self.__checknode)).relationships['restrictions'].mapper.class_

        self.beginInsertRows(QtCore.QModelIndex(), position, position + rows - 1)

        for row in range(rows):
            object = node()
            self.__checknode.restrictions.append(object)

        self.endInsertRows()
        return True

    def removeRows(self, position, rows=1, index:QtCore.QModelIndex=QtCore.QModelIndex()):
        """ Remove a row from the model. """
        self.beginRemoveRows(QtCore.QModelIndex(), position, position + rows - 1)

        del self.__checknode.params[position:position + rows]
        self.__checknode._commit()

        self.endRemoveRows()
        return True

    def setData(self, index, value, role=QtCore.Qt.EditRole):

        if index.isValid():
            if role == QtCore.Qt.EditRole:
                rowNr=index.row()
                colNr=index.column()

                restriction = self.__checknode.restrictions[rowNr]
                restriction._qt_set_value_by_colnr(colnr=colNr, value=value)


    def flags(self, index):
        """ Set the item flags at the given index. Seems like we're
            implementing this function just to see how it's done, as we
            manually adjust each tableView to have NoEditTriggers.
        """
        if index.isValid():
            return QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsEditable
