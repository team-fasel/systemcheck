import logging
import sys
from collections import OrderedDict

from PyQt5 import QtWidgets, QtCore, QtGui

from systemcheck.gui.qtalcmapper import generateQtDelegate, getQtWidgetForAlchemyType
from systemcheck.gui.widgets import TreeView
from systemcheck.gui.models import SettingsModel
from pprint import pprint

__authors__     = ['Lars Fasel']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2017'
__license__     = 'MIT'


def exception_hook(exctype, value, traceback):
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


class SettingsWidget(QtWidgets.QWidget):
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
                self.alchemyObject = getattr(treeNode, treeNode.type)
                self.setLayout(layout)
                self.delegate=generateQtDelegate(self.alchemyObject)
                self.dataMapper=QtWidgets.QDataWidgetMapper()
                self.model=SettingsModel(self.alchemyObject)
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


class SystemsWidget(QtWidgets.QWidget):
    """ The Generic Systems Widget

    The Systems Widget consists of actually 2  or more widgets

    * The TreeView that contains all the systems and displays them in a tree
    * The SystemSettingsWidget that gets geenerated everytime when a system is clicked on in the tree.


    """

    def __init__(self, model: QtCore.QAbstractItemModel=None):
        super().__init__()

        self.logger = logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))
        self.setupUi()

        if model:
            self.setModel(model)

    def on_addFolder(self):
        if len(self.tree.selectedIndexes()) == 0:
            index = QtCore.QModelIndex()
        else:
            index = self.tree.currentIndex()

        self.model.insertRow(0, index)
        if not self.tree.isExpanded(index):
            self.tree.expand(index)


    def on_deleteItem(self):
        index = self.tree.currentIndex()

        parent=index.parent()
        self.model.removeRow(index.row(), parent)

    def on_treeSelectionChanged(self, selected: QtCore.QModelIndex, deselected: QtCore.QModelIndex):

        splitterWidgetCount=self.splitter.count()
        if splitterWidgetCount >1:
            for index in range(1, splitterWidgetCount):
                widget=self.splitter.widget(index)
                widget.deleteLater()

        settingsw=self.generateSettingsWidget(selected)
        if settingsw:
            self.splitter.addWidget(settingsw)
            settingsw.show()
#        self.logger.debug(pformat(node))

    def generateSettingsWidget(self, selected:QtCore.QModelIndex):
        """ Generate the widget that allows configuration of systems

        The settings widget is generated dynamically based on the SQLAlchemy object behind the selected tree node.

        """

        settingsw=SettingsWidget(self.model, selected)
        return settingsw

    def setupUi(self):
        """ Configure the User Interface """

        layout=QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.splitter=QtWidgets.QSplitter()
        self.splitter.setOrientation(QtCore.Qt.Vertical )
        self.tree=TreeView()
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.openContextMenu)
        self.splitter.addWidget(self.tree)
        layout.addWidget(self.splitter)

        self.treeContextMenu = QtWidgets.QMenu()

        self.addSubFolder_act = QtWidgets.QAction(QtGui.QIcon(":AddFolder"), 'Add Sub Folder', self)
        self.addFolder_act = QtWidgets.QAction(QtGui.QIcon(":AddFolder"), 'Add Folder', self)
        self.addFolder_act.triggered.connect(self.on_addFolder)
        self.deleteItem_act = QtWidgets.QAction(QtGui.QIcon(":Trash"), 'Delete Item', self)
        self.deleteItem_act.triggered.connect(self.on_deleteItem)
        self.setLayout(layout)
        self.show()


    def openContextMenu(self, position):

        menu=QtWidgets.QMenu()
        menu = self.systemSpecificContextMenu(position, menu)
        menu.exec_(self.tree.viewport().mapToGlobal(position))

    def setModel(self, model):
        self.model = model
        self.tree.setModel(model)
        self.tree.selectionModel().currentChanged.connect(self.on_treeSelectionChanged)

    def systemSpecificContextMenu(self, position:QtCore.QPoint, menu:QtWidgets.QMenu):
        """ Generate the system specific context menu

        This function has to be reimplemented in the system specific tree models.

        :param position:  The coordinates of the selected tree node
        :param meny: The generic context menu

        """

        raise NotImplemented