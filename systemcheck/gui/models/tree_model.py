from PyQt5 import QtWidgets, QtCore
from pprint import pprint
from systemcheck.model.systems import SystemTreeNode
import sqlalchemy_utils
from typing import Any, Union
import logging

class SystemTreeModel(QtCore.QAbstractItemModel):

    def __init__(self, rootnode, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self._rootNode=rootnode


    def rowCount(self, parent: QtCore.QModelIndex) -> int:
        if not parent.isValid():
            parentNode=self._rootNode
        else:
            parentNode=parent.internalPointer()

        return parentNode._child_count()

    def columnCount(self, parent=None, *args, **kwargs)->int:


        return self._rootNode._visible_column_count()


    def data(self, index: QtCore.QModelIndex, role: int)->Any:

        if not index.isValid():
            return False

        node = index.internalPointer()

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return node._value_by_visible_colnr(index.column())

    def setData(self, index:QtCore.QModelIndex, value: Any, role=QtCore.Qt.EditRole)->bool:
        """ setData Method to make the model modifieabls """

        if index.isValid():

            if role == QtCore.Qt.EditRole:
                node = index.internalPointer()
                node._set_value_by_visible_colnr(index.column(), value)
                return True
        return False

    def headerData(self, column:int, orientation:int, role:int)->str:
        if role==QtCore.Qt.DisplayRole:

            if orientation==QtCore.Qt.Horizontal:

                info=self._rootNode._info_by_visible_colnr(column)
                return info.get('qt_label') or ''

    def flags(self, index:QtCore.QModelIndex)->int:
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def insertRow(self, position: int, parent:QtCore.QModelIndex)->bool:
        """ Add a single child to the model

        :param position: The position where the new child should get inserted
        :param parent: The parent of the new child """
        self.insertRows(position, 1, parent)

    def insertRows(self, position: int, count: int, parent=QtCore.QModelIndex())->bool:
        """ Insert Multiple Children at given position

        :param position: The postition at which a new child should get inserted
        :param count: The number of new children that should get added
        :param parent: The parent of the new children

        """

        parentNode = self.getNode(parent)

        self.beginInsertRows(parent, position, position + count - 1)

        for row in range(count):
            childCount = parentNode._child_count()
            childNode = SystemTreeNode(type='FOLDER', name="untitled " + str(childCount))
            success = parentNode._insert_child(position, childNode)

        self.endInsertRows()

        return success

    def removeRow(self, row: int, parent:QtCore.QModelIndex)->bool:
        """ Remove a single child from the model

        :param row: The position of the child to remove
        :param parent: The parent index of the child

        """
        return self.removeRows(row, 1, parent)

    def removeRows(self, row: int, count: int, parent:QtCore.QModelIndex)->bool:
        """ Remove multiple children from the model

        :param row: The position from which the deletion should start
        :param count: The number of children to remove
        :param parent: The parent of the children

        """

        self.beginRemoveRows(parent, row, row)

        node = self.getNode(parent)

        for i in range(count):
            node._remove_child(row+i)

        self.endRemoveRows()

        return True

    def parent(self, index: QtCore.QModelIndex)->QtCore.QModelIndex:

        if not index.isValid():
            return QtCore.QModelIndex()

        node = index.internalPointer()
        parentNode = node.parent

        if parentNode == self._rootNode:
            return QtCore.QModelIndex()

        return self.createIndex(parentNode._row(), 0, parentNode)

    def index(self, row: int, column: int, parent: QtCore.QModelIndex)-> QtCore.QModelIndex:

        parentNode = self.getNode(parent)

        childItem = parentNode._child(row)

        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def getNode(self, index:QtCore.QModelIndex) -> Any:
        """ Returns the actual node object behind a index"""
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node

        return self._rootNode
