from PyQt5 import QtWidgets, QtCore, QtGui

class ResultOverview(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()


    def setupUi(self):
        layout=QtWidgets.QVBoxLayout()
        self.tree = QtWidgets.QTreeView()
        layout.addWidget(self.tree)


    def setModel(self, model):
        self.model = model
        self.tree.setModel(model)

