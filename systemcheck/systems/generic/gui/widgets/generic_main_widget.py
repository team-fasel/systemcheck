from PyQt5 import QtWidgets, QtGui, QtCore
from systemcheck.gui.models import PolyMorphicFilterProxyModel
from systemcheck.gui.utils import message
from systemcheck.systems.generic.gui.widgets import GenericSystemWidget
from systemcheck.checks.gui.widgets.checks_widget import ChecksWidget
from systemcheck.results.gui.widgets.result_widget import ResultWidget
from systemcheck.resources import icon_rc
from typing import Any

class Signals(QtCore.QObject):
    
    checksDelete = QtCore.pyqtSignal()
    checksExport = QtCore.pyqtSignal()
    checksImport = QtCore.pyqtSignal()
    checksNew = QtCore.pyqtSignal()
    checksNewFolder = QtCore.pyqtSignal()
    checksPause = QtCore.pyqtSignal()
    checksRun = QtCore.pyqtSignal()
    checksStop = QtCore.pyqtSignal()
    resultClear = QtCore.pyqtSignal()
    resultExport = QtCore.pyqtSignal()
    resultImport = QtCore.pyqtSignal()
    systemsCheckLogon = QtCore.pyqtSignal()
    systemsDelete = QtCore.pyqtSignal()
    systemsDisable = QtCore.pyqtSignal()
    systemsEnable = QtCore.pyqtSignal()
    systemsExport = QtCore.pyqtSignal()
    systemsImport = QtCore.pyqtSignal()
    systemsNew = QtCore.pyqtSignal()
    systemsNewFolder = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

class GenericSystemMainWidget(QtWidgets.QWidget):

    def __init__(self, systemFilter:list = None, checkFilter:list = None, systemsWidget:QtWidgets.QWidget=None):
        super().__init__()
        self.signals = Signals()
        self.setupCommonUi(systemsWidget)

        self.__systemFilter=None
        self.__checkFilter=None

        self.setSystemFilter(systemFilter)
        self.setCheckFilter(checkFilter)

    def checkFilter(self):
        return self.__checkFilter

    def systemFilter(self):
        return self.__systemFilter

    def setCheckFilter(self, checkFilter:list):
        self.__checkFilter=checkFilter

    def setSystemFilter(self, systemFilter:list):
        self.__systemFilter = systemFilter

    def setupCommonUi(self, systemsWidget:QtWidgets.QWidget=None):

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        self.setWindowTitle('Generic Main Widget')
        self.setWindowIcon(QtGui.QIcon(':Checked'))
        self.setMinimumWidth(1024)
        self.setMinimumHeight(768)

        self.checksResults_splitter = QtWidgets.QSplitter()
        self.checksResults_splitter.setOrientation(QtCore.Qt.Vertical)
        self.systemsChecks_splitter = QtWidgets.QSplitter()
        self.systemsChecks_splitter.setOrientation(QtCore.Qt.Horizontal)

        if systemsWidget:
            self.systems = systemsWidget()
        else:
            self.systems = GenericSystemWidget()
        self.systemsChecks_splitter.addWidget(self.systems)
        self.systemsChecks_splitter.addWidget(self.checksResults_splitter)

        self.checks = ChecksWidget()
        self.checksResults_splitter.addWidget(self.checks)

        self.results = ResultWidget()
        self.checksResults_splitter.addWidget(self.results)

        layout.addWidget(self.systemsChecks_splitter)

        self.show()

        self.signals.checksDelete.connect(self.checks.on_checkDelete)
        self.signals.checksExport.connect(self.checks.on_checkExport)
        self.signals.checksImport.connect(self.checks.on_checkImport)
        self.signals.checksNew.connect(self.checks.on_checkNew)
        self.signals.checksNewFolder.connect(self.checks.on_checkNewFolder)
        self.signals.checksPause.connect(self.checks.on_checkPause)
        self.signals.checksRun.connect(self.checks.on_checkRun)
        self.signals.checksStop.connect(self.checks.on_checkStop)
        self.signals.resultClear.connect(self.results.on_resultClear)
        self.signals.resultExport.connect(self.results.resultHandler.on_resultExport)
        self.signals.resultImport.connect(self.results.resultHandler.on_resultImport)
        self.signals.systemsCheckLogon.connect(self.systems.on_checkLogon)
        self.signals.systemsNewFolder.connect(self.systems.on_newFolder)
        self.signals.systemsNew.connect(self.systems.on_new)
        self.signals.systemsDelete.connect(self.systems.on_delete)
        self.signals.systemsImport.connect(self.systems.on_import)
        self.signals.systemsExport.connect(self.systems.on_export)
        self.signals.systemsDisable.connect(self.systems.on_disable)
        self.signals.systemsEnable.connect(self.systems.on_enable)


    def setModel(self, system=None, check=None):

        if system:
            self.system_model = system

            if self.systemFilter():
                self.systemSortFilterProxyModel=PolyMorphicFilterProxyModel(self.systemFilter())
                self.systemSortFilterProxyModel.setSourceModel(self.system_model)
                self.systems.setModel(self.systemSortFilterProxyModel)
            else:
                self.systems.setModel(self.system_model)

        if check:
            self.check_model = check

            if self.checkFilter():
                self.checkSortFilterProxyModel=PolyMorphicFilterProxyModel(self.checkFilter())
                self.checkSortFilterProxyModel.setSourceModel(self.check_model)
                self.checks.setModel(self.checkSortFilterProxyModel)
            self.checks.setModel(self.check_model)

    def setFilters(self, system=False, checks=False):
        pass