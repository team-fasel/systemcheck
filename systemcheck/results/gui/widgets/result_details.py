from PyQt5 import QtWidgets, QtCore, QtGui

class ResultDetails(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.setupUi()

    def setupUi(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.table = QtWidgets.QTableView()
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        self.setVisible(False)
        self.setLayout(layout)

    def setModel(self, model):
        self.model = model
        self.table.setModel(model)
        if model:
            self.table.horizontalHeader().setVisible(True)
            self.table.horizontalHeader().setStretchLastSection(True)
            self.table.resizeColumnsToContents()
            self.table.resizeRowsToContents()

