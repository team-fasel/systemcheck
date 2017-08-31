from PyQt5 import QtWidgets, QtCore, QtGui

class ResultOverview(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.setupUi()


    def setupUi(self):
        layout=QtWidgets.QVBoxLayout()
        self.tree = QtWidgets.QTreeView()
        layout.addWidget(self.tree)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.resultsExport_act=QtWidgets.QAction()


    def setModel(self, model):
        self.model = model
        self.tree.setModel(model)

