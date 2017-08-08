from PyQt5 import QtWidgets, QtCore, QtGui
import systemcheck
import logging
from systemcheck.gui.qtalcmapper import generateQtDelegate, getQtWidgetForAlchemyType
from collections import OrderedDict
from typing import Any

class ChecksWidget(QtWidgets.QWidget):


    runChecks_signal = QtCore.pyqtSignal()
    pauseChecks_signal = QtCore.pyqtSignal()
    stopChecks_signal = QtCore.pyqtSignal()

    def __init__(self, model = None):
        super().__init__()
        self.logger = logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))
        self.setupUi()
        if model is not None:
            self.setModel(model)
        self.show()


    def setupUi(self):
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.setContentsMargins(0,0,0,0)
        hlayout.setSpacing(0)
        self.setWindowTitle('SystemCheck Checks')
        self.setWindowIcon(QtGui.QIcon(':Checked'))
        self.checksTreeDescription_splitter = QtWidgets.QSplitter()
        self.checksTreeDescription_splitter.setOrientation(QtCore.Qt.Horizontal)
        self.tree = QtWidgets.QTreeView()
        self.tree.setContentsMargins(0,0,0,0)
        self.tree.setHeaderHidden(True)
        self.tree.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.tree.setSortingEnabled(True)
        self.tree.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tree.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tree.header().setStretchLastSection(True)
        self.checksTreeDescription_splitter.addWidget(self.tree)

        self.checkDescription_tabw = QtWidgets.QTabWidget()
        self.checksTreeDescription_splitter.addWidget(self.checkDescription_tabw)

        self.checksTreeDescription_splitter.setContentsMargins(0, 0, 0, 0)

        widget=self.checksTreeDescription_splitter.widget(0)
        widget.setMaximumWidth(350)

        hlayout.addWidget(self.checksTreeDescription_splitter)
        self.setLayout(hlayout)

    def generateDescriptionWidget(self, selected:QtCore.QModelIndex):
        """ Generate the widget that allows configuration of systems

        The settings widget is generated dynamically based on the SQLAlchemy object behind the selected tree node.

        """

        settingsw=CheckDescriptionWidget(self.model, selected)
        return settingsw

    def generateParameterWidget(self, selected:QtCore.QModelIndex):
        """ Generate the widget that allows configuration of systems

        The settings widget is generated dynamically based on the SQLAlchemy object behind the selected tree node.

        """

        settingsw=CheckParameterWidget(self.model, selected)
        return settingsw


    def setModel(self, model):
        self.model = model
        self.tree.setModel(model)
        self.tree.setColumnHidden(1, True)
        self.tree.selectionModel().currentChanged.connect(self.on_treeSelectionChanged)

    def on_treeSelectionChanged(self, selected: QtCore.QModelIndex, deselected: QtCore.QModelIndex):

        self.checkDescription_tabw.removeTab(0)

        settingsw=self.generateDescriptionWidget(selected)
        if settingsw:
            self.checkDescription_tabw.insertTab(0, settingsw, 'Description')
            settingsw.show()

        paramwidget=self.generateParameterWidget(selected)
        if paramwidget:
            self.checkDescription_tabw.insertTab(1, paramwidget, 'Parameters')
            paramwidget.show()



class CheckDescriptionWidget(QtWidgets.QWidget):
    """ Configure System Settings


    """

    def __init__(self, model, currentIndex, parent=None):
        self.logger=logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))
        super().__init__(parent)
        layout=QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        treeNode=currentIndex.internalPointer()
        self.setVisible(False)
        if treeNode:
            if treeNode.type != 'FOLDER':
                self.alchemyObject = treeNode
                self.setLayout(layout)
                self.delegate=generateQtDelegate(self.alchemyObject)
                self.dataMapper=QtWidgets.QDataWidgetMapper()
                self.model=CheckDescriptionModel(self.alchemyObject)
                self.dataMapper.setModel(self.model)
                columns = self.alchemyObject._visible_columns()

                self.tablew = QtWidgets.QTableWidget(len(columns), 2)
                self.tablew.setAlternatingRowColors(True)
                self.tablew.horizontalHeader().hide()
                self.tablew.verticalHeader().hide()
                self.tablew.horizontalHeader().setStretchLastSection(True)
                layout.addWidget(self.tablew)
                self.widgets = OrderedDict()

                for colNr, column in enumerate(columns):
                    if colNr in self.delegate.delegates.keys():
                        lblWidget=QtWidgets.QTableWidgetItem(column.info.get('qt_label'))
                        self.tablew.setItem(colNr, 0, lblWidget)

        #                if isinstance(sqlalchemy_utils.functions.get_type(column), meta.ChoiceType):
        #                    wid=self.delegate.delegates[colNr].createEditor(self, self, column.info['choices'], None)
        #                else:
        #                    wid = self.delegate.delegates[colNr].createEditor(self, self, None, None)


                        wid = getQtWidgetForAlchemyType(column)
                        self.dataMapper.addMapping(wid, colNr)
                        self.widgets[colNr]=wid
                        self.tablew.setCellWidget(colNr, 1, wid)

                self.dataMapper.toFirst()

                self.tablew.resizeColumnsToContents()
                self.tablew.resizeRowsToContents()

class CheckDescriptionModel(QtCore.QAbstractItemModel):

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
            return self._abstractItem._value_by_visible_colnr(index.column())

    def flags(self, index:QtCore.QModelIndex)->int:
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

    def setData(self, index:QtCore.QModelIndex, value: Any, role=QtCore.Qt.EditRole)->bool:
        """ setData Method to make the model modifiable """

        if index.isValid():
            if role == QtCore.Qt.EditRole:
                self._abstractItem._set_value_by_visible_colnr(index.column(), value)

            return True
        return False

    def index(self, row:int, column:int, parent=None)->QtCore.QModelIndex:

        index = self.createIndex(0, column, QtCore.QModelIndex())

        return index

    def parent(self):
        return QtCore.QModelIndex()

class CheckParameterWidget(QtWidgets.QWidget):
    """ Configure System Settings


    """

    def __init__(self, model, currentIndex, parent=None):
        self.logger=logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))
        super().__init__(parent)
        layout=QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        treeNode=currentIndex.internalPointer()
        self.setVisible(False)
        if treeNode:
            if treeNode.type != 'FOLDER':
                self.alchemyObject = treeNode
                self.setLayout(layout)
                self.delegate=generateQtDelegate(self.alchemyObject)
                self.dataMapper=QtWidgets.QDataWidgetMapper()
                self.model=CheckDescriptionModel(self.alchemyObject)
                self.dataMapper.setModel(self.model)
                columns = self.alchemyObject._visible_columns()

                self.tablew = QtWidgets.QTableWidget(len(columns), 2)
                self.tablew.setAlternatingRowColors(True)
                self.tablew.horizontalHeader().hide()
                self.tablew.verticalHeader().hide()
                self.tablew.horizontalHeader().setStretchLastSection(True)
                layout.addWidget(self.tablew)
                self.widgets = OrderedDict()

                for colNr, column in enumerate(columns):
                    if colNr in self.delegate.delegates.keys():
                        lblWidget=QtWidgets.QTableWidgetItem(column.info.get('qt_label'))
                        self.tablew.setItem(colNr, 0, lblWidget)

        #                if isinstance(sqlalchemy_utils.functions.get_type(column), meta.ChoiceType):
        #                    wid=self.delegate.delegates[colNr].createEditor(self, self, column.info['choices'], None)
        #                else:
        #                    wid = self.delegate.delegates[colNr].createEditor(self, self, None, None)


                        wid = getQtWidgetForAlchemyType(column)
                        self.dataMapper.addMapping(wid, colNr)
                        self.widgets[colNr]=wid
                        self.tablew.setCellWidget(colNr, 1, wid)

                self.dataMapper.toFirst()

                self.tablew.resizeColumnsToContents()
                self.tablew.resizeRowsToContents()



class CheckParameterModel(QtCore.QAbstractItemModel):

    def __init__(self, abstractItem):
        super().__init__()
        self.logger = logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))
        self._abstractItem = abstractItem


    def columnCount(self, parent=None, *args, **kwargs)->int:

        if len(self._abstractItem.params >0):
            param=self._abstractItem.params[0]



        return self._abstractItem._visible_column_count()

    def rowCount(self, parent=None, *args, **kwargs)->int:

        return 1

    def data(self, index: QtCore.QModelIndex, role: int)->Any:
        column = index.column()
        if not index.isValid():
            return False

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return self._abstractItem._value_by_visible_colnr(index.column())

    def flags(self, index:QtCore.QModelIndex)->int:
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

    def setData(self, index:QtCore.QModelIndex, value: Any, role=QtCore.Qt.EditRole)->bool:
        """ setData Method to make the model modifiable """

        if index.isValid():
            if role == QtCore.Qt.EditRole:
                self._abstractItem._set_value_by_visible_colnr(index.column(), value)

            return True
        return False

    def index(self, row:int, column:int, parent=None)->QtCore.QModelIndex:

        index = self.createIndex(0, column, QtCore.QModelIndex())

        return index

    def parent(self):
        return QtCore.QModelIndex()
