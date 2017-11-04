from PyQt5 import QtCore, QtWidgets, QtGui
from pprint import pprint
from systemcheck.results.gui.widgets import ResultDisplay
from systemcheck.results import ResultHandler


class ResultWidget(QtWidgets.QWidget):

    resultExport_signal = QtCore.pyqtSignal()
    resultImport_signal = QtCore.pyqtSignal()
    resultAdd_signal = QtCore.pyqtSignal('PyQt_PyObject')
    resultClear_signal = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.resultHandler=ResultHandler()
        self.setupUi()


    def on_resultClear(self):
        self.ui.details.setModel(None)
        self.ui.details.setVisible(False)
        rowcount=self.overviewModel.rowCount(QtCore.QModelIndex())
        self.overviewModel.removeRows(0, rowcount, QtCore.QModelIndex())

    def on_resultExport(self):
        raise NotImplemented

    def on_resultImport(self):
        raise NotImplemented

    def on_resultOverview_currentChanged(self):

        index = self.ui.overview.tree.currentIndex()
        node = index.internalPointer()
        if node.typeInfo() == 'RESULT':
            resultObject = node.resultObject
            if resultObject:
                detailModel = self.resultHandler.buildResultTableModel(resultObject)
                self.ui.details.setModel(detailModel)
                self.ui.details.setVisible(True)
            else:  #That means, a tree node was clicked that didn't contain a result. 
                self.ui.details.setModel(None)
                self.ui.details.setVisible(False)
            return
        else:
                self.ui.details.setModel(None)
        self.ui.details.setVisible(False)

    def setupUi(self):

        self.overviewModel=self.resultHandler.buildTreeModel()
        self.resultAdd_signal.connect(self.resultHandler.addResult)


        self.ui = ResultDisplay()
        self.ui.setModel(self.overviewModel)
        self.ui.overview.tree.selectionModel().currentChanged.connect(self.on_resultOverview_currentChanged)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        self.setLayout(layout)
        self.show()




