from PyQt5 import QtCore, QtWidgets, QtGui
import systemcheck
from systemcheck.resources import icon_rc

class AbapWidget(QtWidgets.QWidget):

#    icon = QtGui.QIcon(':SAP')

    def __init__(self):
        super().__init__()
        self.setupUi()
        self.show()


    def setupUi(self):

        self.setWindowTitle('ABAP Widget')
#        self.setWindowIcon(self.icon)

        self.systems = systemcheck.systems.ABAP.gui.widgets.AbapSystemsWidget()
        self.checks = systemcheck.checks.gui.widgets.ChecksWidget()
        self.results = systemcheck.checks.gui.widgets.CheckResultsWidget()

        self.checkResults_splitter = QtWidgets.QSplitter()
        self.checkResults_splitter.setOrientation(QtCore.Qt.Vertical)
        self.checkResults_splitter.addWidget(self.checks)
        self.checkResults_splitter.addWidget(self.results)


        self.systemsCheck_splitter = QtWidgets.QSplitter()
        self.systemsCheck_splitter.setContentsMargins(0, 0, 0, 0)
        self.systemsCheck_splitter.addWidget(self.systems)
        self.systemsCheck_splitter.addWidget(self.checkResults_splitter)
        self.systemsCheck_splitter.setStretchFactor(0, 0)
        self.systemsCheck_splitter.setSizes([100, 600])

        self.systemsCheck_splitter.setOrientation(QtCore.Qt.Horizontal)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.systemsCheck_splitter)
        self.setLayout(layout)

    def setModel(self, system=False, check=False):

        if system:
            self.systemmodel = system
            self.systems.tree.setModel(system)

        if check:
            self.checkmodel = check
            self.checks.setModel(check)