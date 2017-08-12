from PyQt5 import QtWidgets, QtCore, QtGui
import systemcheck
import logging
from systemcheck.gui.qtalcmapper import generateQtDelegate, getQtWidgetForAlchemyType
from systemcheck.checks.gui.widgets import CheckSettingsWidget, CheckParameterEditorWidget
from collections import OrderedDict
from typing import Any
from pprint import pprint

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
        self.checksTreeAtrributes_splitter.addWidget(self.tree)

        self.checkAttributes_tabw = QtWidgets.QTabWidget()
        self.checksTreeAtrributes_splitter.addWidget(self.checkAttributes_tabw)

        self.checkDescription_widget=CheckSettingsWidget()
        self.checkAttributes_tabw.addTab(self.checkDescription_widget, 'Description')


        self.checkParameters_widget = CheckParameterEditorWidget()
        self.checkAttributes_tabw.addTab(self.checkParameters_widget, 'Parameters')
        self.checkAttributes_tabw.setTabEnabled(1, False)
        self.checksTreeAtrributes_splitter.setContentsMargins(0, 0, 0, 0)

        widget=self.checksTreeAtrributes_splitter.widget(0)
        widget.setMaximumWidth(350)

        hlayout.addWidget(self.checksTreeAtrributes_splitter)
        self.setLayout(hlayout)

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

    def setModel(self, checks_model):
        self.checks_model = checks_model
        self.tree.setModel(checks_model)
        self.tree.setColumnHidden(1, True)
        self.tree.selectionModel().selectionChanged.connect(self.on_tree_selectionChanged)
