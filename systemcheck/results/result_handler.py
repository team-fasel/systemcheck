from PyQt5 import QtWidgets, QtGui, QtCore
from typing import Any, Union
import logging
from pprint import pformat


class Node(object):
    """ Generic Tree Node

    This tree node is used to build the results tree

    """


    def __init__(self, name, parent=None):
        """ Initialize the tree node
        :param name: Name of the node, gets displayed in the tree view
        :param parent: The parent node
        """

        self._name = name
        self._resultObject = None
        self._children = []
        self._parent = parent

        if parent is not None:
            parent.addChild(self)

    def typeInfo(self):
        return "NODE"

    def addChild(self, child):
        self._children.append(child)

    def insertChild(self, position, child):

        if position < 0 or position > len(self._children):
            return False

        self._children.insert(position, child)
        child._parent = self
        return True

    def removeChild(self, position):

        if position < 0 or position > len(self._children):
            return False

        child = self._children.pop(position)
        child._parent = None

        return True

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    def child(self, row):
        return self._children[row]

    def childCount(self):
        return len(self._children)

    def parent(self):
        return self._parent

    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)

    def log(self, tabLevel=-1):

        output = ""
        tabLevel += 1

        for i in range(tabLevel):
            output += "\t"

        output += "|------" + self._name + "\n"

        for child in self._children:
            output += child.log(tabLevel)

        tabLevel -= 1
        output += "\n"

        return output

    def __repr__(self):
        return self.log()


class ResultNode(Node):


    def __init__(self, name, resultObject, parent=None):
        super(ResultNode, self).__init__(name, parent)
        self._resultObject = resultObject

    @property
    def resultObject(self):
        return self._resultObject

    @resultObject.setter
    def resultObject(self, resObj):
        self._resultObject = resObj

    def typeInfo(self):
        return "RESULT"


class ResultTreeModel(QtCore.QAbstractItemModel):
    """ Results Tree Model


    This tree model is used for displaying the results of the executed actions in the TreeView of the results widget """

    def __init__(self, header, groupBy, root=None, parent=None):
        """ Initialize ResultTreeModel

        :param header: List of strings that define the Header
        :param groupBy: A list of attributes that are used to build the tree. The last attribute represents the lowest level in the tree
        :param parent: The parent for the Abstract Item Model
        :param root: The root node for the model
        """
        super().__init__(parent)

        if root is None:
            root=Node('RootNode')

        self._rootNode = root
        self._header = header
        self.groupBy = groupBy

        self.logger = logging.getLogger(self.__class__.__name__)


    def rowCount(self, parent:QtCore.QModelIndex)->int:
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()

        return parentNode.childCount()

    def columnCount(self, parent:QtCore.QModelIndex)->int:
        return 1

    def data(self, index:QtCore.QModelIndex, role:int):

        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if index.column() == 0:
                return node.name

        # if role == QtCore.Qt.DecorationRole:
        # TODO: REturn some meaningful icons

    def findIndexByName(self, name:str, parent:QtCore.QModelIndex)->Union[QtCore.QModelIndex, None]:
        """ Find Index using the Node's name

        :param name: The 'Name' of the node. Basically what is displayed in the tree view
        :param parent: The index of the parent node """

        rowcount = self.rowCount(parent)

        for row in range(rowcount):
            index = self.index(row, 0, parent)
            node = self.getNode(index)
            if node._name == name:
                return index

        return None

    def setData(self, index:QtCore.QModelIndex, value:Any, role:int=QtCore.Qt.EditRole):

        if index.isValid():

            if role == QtCore.Qt.EditRole:
                node = index.internalPointer()
                node.setName(value)

                return True
        return False


    def headerData(self, section:int, orientation:int, role:int):
        if role == QtCore.Qt.DisplayRole:
            if orientation==QtCore.Qt.Horizontal:
                return self._header[section]


    def flags(self, index:QtCore.QModelIndex)->int:
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def parent(self, index:QtCore.QModelIndex)->QtCore.QModelIndex:
        """ Return Parent of the QModelIndex"""

        node = self.getNode(index)
        parentNode = node.parent()

        if parentNode == self._rootNode:
            return QtCore.QModelIndex()

        return self.createIndex(parentNode.row(), 0, parentNode)

    def index(self, row:int, column:int, parent:QtCore.QModelIndex)->QtCore.QModelIndex:
        """ Return a QModelIndex that corresponds to the given row, column and parent node """

        parentNode = self.getNode(parent)

        childItem = parentNode.child(row)

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

    def insertRows(self, position:int, rows:int, parent=QtCore.QModelIndex(), childNode=None):
        success=True
        parentNode = self.getNode(parent)
        self.beginInsertRows(parent, position, position + rows - 1)

        if childNode is not None:
            for row in range(rows):
                childCount = parentNode.childCount()
                if childNode is None:
                    childNode = Node("untitled" + str(childCount))
                success = parentNode.insertChild(position, childNode)

        self.endInsertRows()
        return success

    def insertResult(self, resultObject, parent=None):
        self.logger.debug('inserting Result {}'.format(pformat(resultObject)))
        success = False

        if parent is None:
            self.logger.debug('Inserting at root level')
            parent=QtCore.QModelIndex()

        # Need to traverse the result tree
        prevParentIndex = parent
        prevNodeObject = self.getNode(prevParentIndex)
        self.logger.debug('Retrieved initial parent node: {}'.format(pformat(prevNodeObject)))

        hierarchy=dict()

        for levelNr, level in enumerate(self.groupBy):
            self.logger.debug('Processing Level {}: {}'.format(levelNr, level))
            text=getattr(resultObject, level)
            self.logger.debug('Retrieved text from result object for {}: {}. Searching for object'.format(level, text))
            newParentIndex = self.findIndexByName(text, prevParentIndex)


            if newParentIndex is None:
                self.logger.debug('No Object with that text found. Building a new tree node')
                prevParentNodeObject = self.getNode(prevParentIndex)
                if levelNr<len(self.groupBy)-1:
                    self.logger.debug('Did not reach lowest level yet. Creating a normal tree node with text: "%s"', text)
                    newNode = Node(text)
                else:   #That means, we reached the lowest level of the hierarchy
                    self.logger.debug('Reached lowest level in hierarchy (%i), adding ResultObject node', levelNr)
                    if resultObject.rating == 'error':
                        self.logger.debug('ResultObject had error status. Changing text to include message')
                        text = '{} ({})'.format(text, resultObject.errorMessage or 'no Error Message')
                        self.logger.debug('Text for result object: %s', text)
                    newNode = ResultNode(name=text, resultObject=resultObject)

                self.logger.debug('inserting node with name "%s" under "%s"', newNode.name, prevParentNodeObject.name)
                prevParentNodeObject.insertChild(0, newNode)
                self.insertRows(0, 1, prevParentIndex)
                self.logger.debug('searching for text "%s" again', newNode.name)
                prevParentIndex = self.findIndexByName(text, prevParentIndex)
                if prevParentIndex is None:
                    self.logger.error('Searched for "%s" but did not find it. ', newNode.name)
                else:
                    node = self.getNode(prevParentIndex)
                    self.logger.debug('Found node with name "%s"', node.name)
                    if newNode.name == node.name:
                        self.logger.debug('Names Match, everything ok')
                    else:
                        self.logger.error('Names do not Match. Tree Hierarchy is wrong')
            else:
                self.logger.debug('Node with text "%s" found. Using it as new Root Node', text)
                prevParentIndex=newParentIndex
                self.logger.debug('Hierarchy: \n%s', self.getNode(prevParentIndex).log())


        return success


    def removeRows(self, position:int, rows:int, parent:QtCore.QModelIndex=QtCore.QModelIndex()):

        parentNode = self.getNode(parent)
        self.beginRemoveRows(parent, position, position + rows - 1)

        for row in range(rows):
            success = parentNode.removeChild(position)

        self.endRemoveRows()

        return success

    @property
    def groupBy(self):
        return self._groupBy

    @groupBy.setter
    def groupBy(self, groupBy):
        self._groupBy = groupBy

class ResultTableModel(QtCore.QAbstractTableModel):
    """ The Table Model for the Results Details


    """

    def __init__(self, resultObject):
        """ Initialize Tesult Table Model


        :param resultObject: The result object of the check

        """
        super().__init__()
        self._resultObject = resultObject

    def rowCount(self, parent=None):
        return len(self._resultObject.result)

    def columnCount(self, parent=None):
        colCount = len(list(self._resultObject.resultDefinition.keys()))
        return colCount

    def data(self, index, role):

        if index.isValid():

            col=index.column()
            row = index.row()
            columns = list(self._resultObject.resultDefinition.keys())
            columnName = columns[col]

            if role == QtCore.Qt.DisplayRole:
                relevant_result = self._resultObject.result[row]
                value = relevant_result.get(columnName)
                return value

    def flags(self, index):
        if not index.isValid():
            return None
        return QtCore.Qt.ItemIsEnabled

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role==QtCore.Qt.DisplayRole:
            columns = list(self._resultObject.resultDefinition.values())
            return columns[col]

class ResultHandler(QtCore.QObject):
    """ Result Handler for Checks

    The result handler processes incoming check results.
    """

    resultAdd_signal = QtCore.pyqtSignal('PyQt_PyObject')
    resultAdded_signal = QtCore.pyqtSignal('PyQt_PyObject')
    resultInitialize_signal = QtCore.pyqtSignal('PyQt_PyObject')

    def __init__(self):
        super().__init__()
        self.__results=[]
        self.resultAdd_signal.connect(self.addResult)
        self.logger = logging.getLogger(self.__class__.__name__)


    def addResult(self, result):
        """ Add a Check Result

        :param result: The result object of a check """


#        self.__results.append(result)
        self.resultAdded_signal.emit(result)


    def buildTreeModel(self, groupBy=None):
        if groupBy is None:
            groupBy=['rating', 'checkName', 'systeminfo']
        model = ResultTreeModel(header=['Results Overview'], groupBy=groupBy)
        self.resultAdded_signal.connect(model.insertResult)
#        for result in self.__results:
#            model.insertResult(result)
        return model

    def buildResultTableModel(self, resultObject):
        self.logger.debug('Building Table Model for result object: %s', pformat(resultObject))
        model = ResultTableModel(resultObject)
        return model

    def on_resultExport(self):
        pass

    def on_resultImport(self):
        pass

