from PyQt5 import QtWidgets, QtCore, QtGui
from typing import Union

class PolyMorphicFilterProxyModel(QtCore.QSortFilterProxyModel):
    """ Polymorphic Filter Proxy Model

    Used to filter based on SQLAlchemy types
    """


    def __init__(self, filterClasses:set=None):
        super().__init__()
        if filterClasses:
            self.__filterClasses = filterClasses
        else:
            self.__filterClasses = []

    def checkedIndexes(self)->set:
        """ Return the checked indexes from the source model

        """
        checkedIndexes = self.sourceModel().checkedIndexes()
        if len(self.__filterClasses) == 0:
            return checkedIndexes

        relevantCheckedIndexes = set()

        for index in checkedIndexes:
            node = self.sourceModel().getNode(index)
            if len(self.__filterClasses)>0:
                if type(node) in self.__filterClasses:
                    relevantCheckedIndexes.add(index)
            else:
                relevantCheckedIndexes.add(index)


        return relevantCheckedIndexes

    def checkedNodes(self):
        indexes = self.checkedIndexes()

        checkedNodes=[self.sourceModel().getNode(index)
                          for index in indexes]

        return checkedNodes

    def filterAcceptsRow(self, rowNr:int, parent:QtCore.QModelIndex):
        """ Function to """


        if len(self.__filterClasses) == 0:
            return True

        model = self.sourceModel()
        index = model.index(rowNr, self.filterKeyColumn(), parent)

        node=index.internalPointer()

        if type(node) in self.__filterClasses:
            return True
        return False

    def getNode(self, proxyIndex):
        """ Get AbstractItem from Index


        :param proxyIndex: Index of the tree node with the object
        """

        source_index = self.mapToSource(proxyIndex)
        source_model = self.sourceModel()
        node = source_model.getNode(source_index)

        return node

    def insertRow(self, parent, position=0, nodeObject=None):
        """ Add a single child to the model

        :param position: The position where the new child should get inserted
        :param parent: The parent of the new child
        :param nodeType: Defines the type of the object that should get added. For example FOLDER, ABAP, HANA, ...
        :param nodeObject: The actual SQLAlchemy Node Object

        """

        sourceIndex = self.mapToSource(parent)

        if nodeObject is None:
            nodeObject = self.sourceModel()._treeNode(name="untitled")
        self.sourceModel().insertRow(position=position, parent=sourceIndex, nodeObject=nodeObject)
        self.invalidate()


        return True

    def insertRows(self, position, count, parent=QtCore.QModelIndex()):
        """ Insert Multiple Children at given position in the original model

        :param position: The postition at which a new child should get inserted
        :param count: The number of new children that should get added
        :param parent: The parent of the new children

        """

        sourceIndex = self.mapToSource(parent)
        parentNode = self.sourceModel().getNode(sourceIndex)

        self.sourceModel().beginInsertRows(sourceIndex, position, position + count - 1)

        for row in range(count):
            childCount = parentNode._qt_child_count()
            childNode = self._treeNode(name="untitled " + str(childCount))
            success = parentNode._qt_insert_child(position, childNode)

        self.endInsertRows()

        return success

    def removeRows(self, row, count, parent):
        """ Remove a single child from the model

        :param row: The position of the child to remove
        :param parent: The parent index of the child

        """

        for row_counter in range(count):
            proxyItemIndex = self.index(row+row_counter, 0, parent)
            sourceItemIndex = self.mapToSource(proxyItemIndex)
            sourceRow = sourceItemIndex.row()
            sourceParent = sourceItemIndex.parent()
            self.sourceModel().removeRow(sourceRow, sourceParent)
        self.invalidate()


    #TODO: Refactor the below into a designated system/check proxy model

    def checkedNodesWithLogonInfo(self):

        nodes=self.checkedNodes(filterObjects=True)

        relevantNodes = [node
                         for node in nodes
                         if node.logon_info() is not None]

        return relevantNodes

    def logonInfo(self, index:QtCore.QModelIndex)->Union[dict, None]:
        """ Logon Info for Specific Index

        :param index: The QModelIndex of the original model"""

        node=self.sourceModel().getNode(index)

        return node.logon_info()
