from PyQt5 import QtWidgets, QtGui, QtCore
from systemcheck.gui.models import PolyMorphicFilterProxyModel
from systemcheck.systems.generic.gui.widgets import GenericSystemWidget
from systemcheck.checks.gui.widgets import ChecksWidget
from systemcheck.resources import icon_rc
from typing import Any

class GenericSystemMainWidget(QtWidgets.QWidget):

    checkNew_signal = QtCore.pyqtSignal()
    checkNewFolder_signal = QtCore.pyqtSignal()
    checkDelete_signal = QtCore.pyqtSignal()
    checkImport_signal = QtCore.pyqtSignal()
    checkExport_signal = QtCore.pyqtSignal()
    checkRun_signal = QtCore.pyqtSignal()
    checkPause_signal = QtCore.pyqtSignal()
    checkStop_signal = QtCore.pyqtSignal()
    resultAdd_signal = QtCore.pyqtSignal()
    resultExport_signal = QtCore.pyqtSignal()
    resultImport_signal = QtCore.pyqtSignal()
    systemCheckLogon_signal = QtCore.pyqtSignal()
    systemNewFolder_signal = QtCore.pyqtSignal()
    systemNew_signal = QtCore.pyqtSignal()
    systemDelete_signal = QtCore.pyqtSignal()
    systemImport_signal = QtCore.pyqtSignal()
    systemExport_signal = QtCore.pyqtSignal()

    def __init__(self, systemFilter:Any = None, checkFilter:list = None):
        super().__init__()
        self.setupCommonActions()
        self.setupCommonUi()
        self.__systemFilter=None
        self.__checkFilter=None

        self.setSystemFilter(systemFilter)
        self.setCheckFilter(checkFilter)

    def checkFilter(self):
        return self.__checkFilter

    def systemFilter(self):
        return self.__systemFilter

    def setSystemFilter(self, systemFilter:Any):
        self.__systemFilter = systemFilter

    def setCheckFilter(self, checkFilter:list):
        self.__checkFilter=checkFilter

    def setupCommonUi(self):
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        self.setWindowTitle('Generic Main Widget')
        self.setWindowIcon(QtGui.QIcon(':Checked'))
        self.setMinimumWidth(1024)
        self.setMinimumHeight(768)

        self.systemsChecks_splitter = QtWidgets.QSplitter()
        self.systemsChecks_splitter.setOrientation(QtCore.Qt.Horizontal)

        self.systems = GenericSystemWidget()
        self.systemsChecks_splitter.addWidget(self.systems)

        self.checks = ChecksWidget()
        self.systemsChecks_splitter.addWidget(self.checks)

        layout.addWidget(self.systemsChecks_splitter)
        self.show()

    def setupCommonActions(self):
        pass

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