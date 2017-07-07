from PyQt5 import QtWidgets, QtCore
from pprint import pprint
from systemcheck.model.systems import SystemTreeNode
import sqlalchemy_utils

class SystemTreeModel(QtCore.QAbstractItemModel):

    def __init__(self, rootnode, parent=None):
        super().__init__(parent)

        self._rootNode=rootnode


    def rowCount(self, parent):
        if not parent.isValid():
            parentNode=self._rootNode
        else:
            parentNode=parent.internalPointer()

        return parentNode._child_count()

    def columnCount(self, parent=None, *args, **kwargs):

        return self._rootNode._visible_column_count()

    def data(self, index:QtCore.QModelIndex, role:int):

        if not index.isValid():
            return False

        node = index.internalPointer()

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return node._value_by_visible_colnr(index.column())

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        """ setData Method to make the model modifieabls """

        if index.isValid():

            if role == QtCore.Qt.EditRole:
                node = index.internalPointer()
                node._set_value_by_visible_colnr(index.column(), value)
                return True
        return False

    def headerData(self, column, orientation, role):
        if role==QtCore.Qt.DisplayRole:

            info=self._rootNode._info_by_visible_colnr(column)
            return info.get('qt_label')

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):

        parentNode = self.getNode(parent)

        self.beginInsertRows(parent, position, position + rows - 1)

        for row in range(rows):
            childCount = parentNode._child_count()
            childNode = SystemTreeNode(type='FOLDER', name="untitled " + str(childCount))
            success = parentNode.insertChild(position, childNode)

        self.endInsertRows()

        return success

    def parent(self, index):

        node = self.getNode(index)
        parentNode = node.parent

        if parentNode == self._rootNode:
            return QtCore.QModelIndex()

        return self.createIndex(parentNode._row(), 0, parentNode)

    def index(self, row, column, parent):

        parentNode = self.getNode(parent)

        childItem = parentNode._child(row)

        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def getNode(self, index):
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node

        return self._rootNode
