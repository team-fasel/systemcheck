from PyQt5 import QtWidgets, QtCore
from pprint import pprint
from systemcheck.model.systems import SystemTreeNode
import sqlalchemy_utils

class SystemTreeModel(QtCore.QAbstractItemModel):

    def __init__(self, rootnode, parent=None):
        super().__init__(parent)

        self._rootNode=rootnode

#        self.session=session
#        self.refresh()


#    def refresh(self):
#        self._rootNode = self.session.query(SystemTreeNode).filter(type=='ROOT')

    def rowCount(self, parent):
        if not parent.isValid():
            parentNode=self._rootNode
        else:
            parentNode=parent.internalPointer()

        return parentNode._child_count()

    def columnCount(self, parent=None, *args, **kwargs):

        return self._rootNode._visible_column_count()

    def data(self, index, role):

        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return node._value_by_visible_colnr(index.column())

    def headerData(self, column, orientation, role):
        if role==QtCore.Qt.DisplayRole:

            info=self._rootNode._info_by_visible_colnr(column)
            return info.get('qt_label')

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


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
