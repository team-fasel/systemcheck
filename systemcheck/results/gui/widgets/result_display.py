from PyQt5 import QtWidgets, QtCore, QtGui
from . import result_details
from . import result_overview

class ResultDisplay(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi()

    def setupUi(self):
        self.splitter = QtWidgets.QSplitter()
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.overview = result_overview.ResultOverview()
        self.splitter.addWidget(self.overview)
        self.details = result_details.ResultDetails()
        self.splitter.addWidget(self.details)
        self.tree=QtWidgets.QTreeView()
        layout.addWidget(self.splitter)
        self.setLayout(layout)
        self.show()

    def setModel(self, model):
        self.model = model
        self.overview.setModel(model)

