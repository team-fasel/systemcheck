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


class GenericSystemSettingsWidget(QtWidgets.QWidget):
    """ Configure System Settings


    """

    def __init__(self, model, currentIndex, parent=None):
        self.logger=logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))
        super().__init__(parent)
        self.model = model

        layout=QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        treeNode=self.model.getNode(currentIndex)
        self.setVisible(False)
        if treeNode:
            if treeNode.type !='FOLDER':
                self.alchemyObject = treeNode
                self.setLayout(layout)
                self.delegate=generateQtDelegate(self.alchemyObject)
                self.dataMapper=QtWidgets.QDataWidgetMapper()
                self.model=SettingsModel(self.alchemyObject)
                self.dataMapper.setModel(self.model)
                columns = self.alchemyObject._qt_columns()

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

                        wid = getQtWidgetForAlchemyType(column)
                        self.dataMapper.addMapping(wid, colNr)
                        self.widgets[colNr]=wid
                        self.tablew.setCellWidget(colNr, 1, wid)

                self.dataMapper.toFirst()

                self.tablew.resizeColumnsToContents()
                self.tablew.resizeRowsToContents()


class GenericSystemWidget(QtWidgets.QWidget):
    """ The Generic Systems Widget

    The Systems Widget consists of actually 2  or more widgets

    * The TreeView that contains all the systems and displays them in a tree
    * The SystemSettingsWidget that gets geenerated everytime when a system is clicked on in the tree.


    """
    systemChangePassword_signal = QtCore.pyqtSignal()
    systemCheckLogon_signal = QtCore.pyqtSignal()
    systemDelete_signal = QtCore.pyqtSignal()
    systemExport_signal = QtCore.pyqtSignal()
    systemImport_signal = QtCore.pyqtSignal()
    systemNew_signal = QtCore.pyqtSignal()
    systemNewFolder_signal = QtCore.pyqtSignal()

    def __init__(self, model: QtCore.QAbstractItemModel=None):
        super().__init__()

        self.logger = logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))
        self.setupUi()
        if model:
            self.setModel(model)

    def toolbar(self):
        toolbar = QtWidgets.QToolBar()
        toolbar.addActions([self.systemNew_act, self.systemNewFolder_act])
        toolbar.addSeparator()
        toolbar.addActions([self.systemDelete_act, self.systemImport_act, self.systemExport_act])


    def on_changePassword(self):
        pass

    def on_checkLogon(self):
        pass

    def on_delete(self):
        index = self.tree.currentIndex()

        parent=index.parent()
        self.system_model.removeRow(index.row(), parent)
        pass

    def on_disable(self):
        pass

    def on_enable(self):
        pass

    def on_export(self):
        pass

    def on_import(self):
        pass

    def on_new(self):
        pass

    def on_newFolder(self):
        if len(self.tree.selectedIndexes()) == 0:
            index = QtCore.QModelIndex()
        else:
            index = self.tree.currentIndex()

        self.system_model.insertRow(0, index)
        if not self.tree.isExpanded(index):
            self.tree.expand(index)

    def on_treeSelectionChanged(self, selected: QtCore.QModelIndex, deselected: QtCore.QModelIndex):

        splitterWidgetCount=self.splitter.count()
        if splitterWidgetCount >1:
            for index in range(1, splitterWidgetCount):
                widget=self.splitter.widget(index)
                widget.deleteLater()

        settingsw=GenericSystemSettingsWidget(self.system_model, selected)
        if settingsw:
            self.splitter.addWidget(settingsw)
            settingsw.show()
#        self.logger.debug(pformat(node))

    def openContextMenu(self, position):

        menu=QtWidgets.QMenu()
        menu = self.systemSpecificContextMenu(position, menu)
        menu.exec_(self.tree.viewport().mapToGlobal(position))

    def setupUi(self):
        """ Configure the User Interface """

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        label = QtWidgets.QLabel('Systems:')
        layout.addWidget(label)
        self.splitter = QtWidgets.QSplitter()
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.tree = TreeView()
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.openContextMenu)
        self.splitter.addWidget(self.tree)
        layout.addWidget(self.splitter)

        self.treeContextMenu = QtWidgets.QMenu()

        self.addFolder_act = QtWidgets.QAction(QtGui.QIcon(':AddFolder'), 'Add Folder')
        self.deleteItem_act = QtWidgets.QAction(QtGui.QIcon(':Trash'), 'Delete')


        self.systemChangePassword_signal.connect(self.on_changePassword)
        self.systemCheckLogon_signal.connect(self.on_checkLogon)
        self.systemDelete_signal.connect(self.on_delete)
        self.systemExport_signal.connect(self.on_export)
        self.systemImport_signal.connect(self.on_import)
        self.systemNew_signal.connect(self.on_new)
        self.systemNewFolder_signal.connect(self.on_newFolder)
        self.setLayout(layout)
        self.show()


    def setModel(self, model):
        self.system_model = model
        self.tree.setModel(model)
        self.tree.selectionModel().currentChanged.connect(self.on_treeSelectionChanged)
        self.tree.setColumnHidden(1, True)

    def systemSpecificContextMenu(self, position:QtCore.QPoint, menu:QtWidgets.QMenu):
        """ Generate the system specific context menu

        This function has to be reimplemented in the system specific tree models.

        :param position:  The coordinates of the selected tree node
        :param meny: The generic context menu

        """

        raise NotImplemented