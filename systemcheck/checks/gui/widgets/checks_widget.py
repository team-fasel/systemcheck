from PyQt5 import QtWidgets, QtCore, QtGui
import systemcheck
import logging
#from systemcheck.checks.gui.widgets import CheckParameterEditorWidget
#from systemcheck.checks.gui.widgets import CheckSettingsWidget
from collections import OrderedDict
from typing import Any
from pprint import pprint

class ChecksWidget(QtWidgets.QWidget):


    checksNewFolder_signal = QtCore.pyqtSignal()
    checksNew_signal = QtCore.pyqtSignal()
    checksDelete_signal = QtCore.pyqtSignal()
    checksImport_signal = QtCore.pyqtSignal()
    checksExport_signal = QtCore.pyqtSignal()
    checksPause_signal = QtCore.pyqtSignal()
    checksRun_signal = QtCore.pyqtSignal()
    checksStop_signal = QtCore.pyqtSignal()
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
        vlayout = QtWidgets.QVBoxLayout()
        vlayout.setContentsMargins(0, 0, 0, 0)
        treewidget=QtWidgets.QWidget()
        treewidget.setLayout(vlayout)
        label = QtWidgets.QLabel('Checks:')
        vlayout.addWidget(label)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.setContentsMargins(0,0,0,0)
        hlayout.setSpacing(0)
        self.setWindowTitle('SystemCheck Checks')
        self.setWindowIcon(QtGui.QIcon(':Checked'))
        self.checksTreeAtrributes_splitter = QtWidgets.QSplitter()
        self.checksTreeAtrributes_splitter.setOrientation(QtCore.Qt.Horizontal)
        self.tree = QtWidgets.QTreeView()
        self.tree.setContentsMargins(0,0,0,0)
        self.tree.setHeaderHidden(True)
        self.tree.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.tree.setSortingEnabled(True)
        self.tree.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tree.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tree.header().setStretchLastSection(True)
        vlayout.addWidget(self.tree)
        self.checksTreeAtrributes_splitter.addWidget(treewidget)

        self.checkAttributes_tabw = QtWidgets.QTabWidget()
        self.checksTreeAtrributes_splitter.addWidget(self.checkAttributes_tabw)

        self.checkDescription_widget=systemcheck.checks.gui.widgets.CheckSettingsWidget()
        self.checkAttributes_tabw.addTab(self.checkDescription_widget, 'Description')


        self.checkParameters_widget = systemcheck.checks.gui.widgets.CheckParameterEditorWidget()
        self.checkAttributes_tabw.addTab(self.checkParameters_widget, 'Parameters')
        self.checkAttributes_tabw.setTabEnabled(1, False)
        self.checksTreeAtrributes_splitter.setContentsMargins(0, 0, 0, 0)

        widget=self.checksTreeAtrributes_splitter.widget(0)
        widget.setMaximumWidth(350)

        hlayout.addWidget(self.checksTreeAtrributes_splitter)
        self.setLayout(hlayout)
        self.setupActions()

    def setupActions(self):

        self.checksNewFolder_act = QtWidgets.QAction(QtGui.QIcon(':AddFolder'), 'Add Folder')
        self.checksNewFolder_act.triggered.connect(self.on_checkNewFolder)
        self.checksNewFolder_act.setEnabled(False)

        self.checksNew_act = QtWidgets.QAction(QtGui.QIcon(':AddFile'), 'Add New Check...')
        self.checksNew_act.triggered.connect(self.on_checkNew)
        self.checksNew_act.setEnabled(False)

        self.checksDelete_act =  QtWidgets.QAction(QtGui.QIcon(':Trash'), 'Delete Selected Checks')
        self.checksDelete_act.triggered.connect(self.on_checkDelete)
        self.checksDelete_act.setEnabled(False)

        self.checksImport_act = QtWidgets.QAction(QtGui.QIcon(':Import'), 'Import Checks...')
        self.checksImport_act.triggered.connect(self.on_checkImport)
        self.checksImport_act.setEnabled(False)

        self.checksExport_act = QtWidgets.QAction(QtGui.QIcon(':Export'), 'Export Checks...')
        self.checksExport_act.triggered.connect(self.on_checkExport)
        self.checksExport_act.setEnabled(False)

        self.checksRun_act = QtWidgets.QAction(QtGui.QIcon(':Play'), 'Run Checks')
        self.checksRun_act.triggered.connect(self.on_checkRun)
        self.checksRun_act.setEnabled(False)

        self.checksPause_act = QtWidgets.QAction(QtGui.QIcon(':Pause'), 'Pause Checks')
        self.checksPause_act.triggered.connect(self.on_checkPause)
        self.checksPause_act.setEnabled(False)

        self.checksStop_act = QtWidgets.QAction(QtGui.QIcon(':Stop'), 'Stop Checks')
        self.checksStop_act.triggered.connect(self.on_checkPause)
        self.checksStop_act.setEnabled(False)

    def menu(self):
        menu = QtWidgets.QMenu('&Checks')
        menu.addActions([self.checksNewFolder_act, self.checksNew_act])
        menu.addSeparator()
        menu.addActions([self.checksDelete_act, self.checksImport_act, self.checksExport_act])
        menu.addSeparator()
        menu.addActions([self.checksRun_act, self.checksStop_act, self.checksPause_act])

    def on_tree_selectionChanged(self):

        print('selection changed')
        current = self.tree.currentIndex()
        node = current.internalPointer()
        self.checkDescription_widget.updateCheck.emit(node)
        if node.type == 'FOLDER':
            self.checkAttributes_tabw.setTabEnabled(1, False)
        else:
            self.checkAttributes_tabw.setTabEnabled(1, True)
            self.checkParameters_widget.updateCheck.emit(node)

    def on_checkNew(self):
        raise NotImplemented

    def on_checkNewFolder(self):
        raise NotImplemented

    def on_checkDelete(self):
        raise NotImplemented

    def on_checkRun(self):
        raise NotImplemented

    def on_checkExport(self):
        raise NotImplemented

    def on_checkImport(self):
        raise NotImplemented

    def on_checkStop(self):
        raise NotImplemented

    def on_checkPause(self):
        raise NotImplemented

    def setModel(self, checks_model):
        self.checks_model = checks_model
        self.tree.setModel(checks_model)
        self.tree.setColumnHidden(1, True)
        self.tree.selectionModel().selectionChanged.connect(self.on_tree_selectionChanged)
