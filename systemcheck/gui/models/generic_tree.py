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

class GenericTreeModel(QtCore.QAbstractItemModel):

    def __init__(self, rootnode, parent=None, treenode = None):
        super().__init__(parent)
        self.logger = logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))
        self._rootNode=rootnode
        self._treeNode=treenode
        self.checkedIndexes = set()

    def columnCount(self, parent=None, *args, **kwargs)->int:

        return self._rootNode._qt_column_count()

    def data(self, index: QtCore.QModelIndex, role: int)->Any:

        if not index.isValid():
            return False

        if role==QtCore.Qt.CheckStateRole:
            if index.column() == 0:
                if index in self.checkedIndexes:
                    return QtCore.Qt.Checked
                else:
                    return QtCore.Qt.Unchecked

        node = index.internalPointer()

        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                icon = node._qt_icon()
                if icon:
                    icon = QtGui.QIcon(node._qt_icon())
                    return icon

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            colnr = index.column()
            return node._qt_data_colnr(colnr)

    def flags(self, index:QtCore.QModelIndex)->int:
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable

    def getNode(self, index:QtCore.QModelIndex) -> Any:
        """ Returns the actual node object behind a index"""
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node

        return self._rootNode

    def headerData(self, column:int, orientation:int, role:int)->str:
        if role==QtCore.Qt.DisplayRole:

            if orientation==QtCore.Qt.Horizontal:
                header=self._rootNode._qt_header(column)
                return header

    def index(self, row: int, column: int, parent: QtCore.QModelIndex)-> QtCore.QModelIndex:

        parentNode = self.getNode(parent)

        childItem = parentNode._qt_child(row)

        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def insertRow(self, position: int, parent:QtCore.QModelIndex, nodeObject:Any=None)->bool:
        """ Add a single child to the model

        :param position: The position where the new child should get inserted
        :param parent: The parent of the new child
        :param nodeType: Defines the type of the object that should get added. For example FOLDER, ABAP, HANA, ...
        :param nodeObject: The actual SQLAlchemy Node Object

        """

        parent_node = self.getNode(parent)

        self.beginInsertRows(parent, position, position + 1)

        if nodeObject:
            parent_node._qt_insert_child(position, nodeObject)
        else:
            childNode = self._treeNode(type='FOLDER', name="untitled")
            parent_node._qt_insert_child(position, childNode)
        self.endInsertRows()
        return True

    def insertRows(self, position: int, count: int, parent:QtCore.QModelIndex=QtCore.QModelIndex())->bool:
        """ Insert Multiple Children at given position

        :param position: The postition at which a new child should get inserted
        :param count: The number of new children that should get added
        :param parent: The parent of the new children

        """

        parentNode = self.getNode(parent)

        self.beginInsertRows(parent, position, position + count - 1)

        for row in range(count):
            childCount = parentNode._qt_child_count()
            childNode = self._treeNode(name="untitled " + str(childCount))
            success = parentNode._qt_insert_child(position, childNode)

        self.endInsertRows()

        return success

    def parent(self, index: QtCore.QModelIndex)->QtCore.QModelIndex:

        #self.logger.debug('Find parent of index: {}'.format(pformat(index)))
        if not index.isValid():
            return QtCore.QModelIndex()

        node = index.internalPointer()

        #self.logger.debug('Identified node: {}'.format(pformat(node)))
        #self.logger.debug('Identified Parent node: {}'.format(pformat(node.parent_node)))

        parentNode = node.parent_node

        if parentNode == self._rootNode:
            return QtCore.QModelIndex()

        return self.createIndex(parentNode._qt_row(), 0, parentNode)

    def recursiveCheck(self, index:QtCore.QModelIndex, value:int):
        """ Set the CheckBox Status

        :param index: The QModelIndex of the item to check
        :param value: Status of the checkbox


        """

        if self.hasChildren(index):
            for childnr in range(self.rowCount(index)):
                child = super().index(childnr, 0, index)
                self.setData(child, value, QtCore.Qt.CheckStateRole)
        else:
            self.setData(index, value, QtCore.Qt.CheckStateRole)

        return True

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
            del node.children[row+i]
            node._commit()

        self.endRemoveRows()

        return True

    def rowCount(self, parent: QtCore.QModelIndex) -> int:
        if not parent.isValid():
            parentNode=self._rootNode
        else:
            parentNode=parent.internalPointer()

        return parentNode._qt_child_count()

    def setData(self, index:QtCore.QModelIndex, value: Any, role=QtCore.Qt.EditRole)->bool:
        """ setData Method to make the model modifieabls """

        if index.isValid():

            if role == QtCore.Qt.CheckStateRole:
                if index.column() == 0:
                    if value == QtCore.Qt.Checked:
                        self.checkedIndexes.add(index)
                    else:
                        self.checkedIndexes.remove(index)
                    if self.hasChildren(index):
                        self.recursiveCheck(index, value)



            if role == QtCore.Qt.EditRole:
                node = index.internalPointer()
                node._qt_set_value_by_colnr(index.column(), value)

            self.dataChanged.emit(index, index)
            return True
        return False


