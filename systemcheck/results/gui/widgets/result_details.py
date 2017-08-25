from PyQt5 import QtWidgets, QtCore, QtGui


class ResultDetailModel(QtCore.QAbstractTableModel):

    def __init__(self, resultObject):
        super().__init__()
        self.__resultObject = resultObject


    def rowCount(self, parent=None, *args, **kwargs):
        rowcount=(self.__resultObject.result)
        return rowcount

    def columnCount(self, parent=None, *args, **kwargs):
        colCount=len(self.__resultObject.resultDefinition)
        return colCount

    def data(self, index:QtCore.QModelIndex, role:int=QtCore.Qt.DisplayRole):

        if index.isValid():
            rowNr = index.row()
            colNr = index.column()

            if role == QtCore.Qt.DisplayRole:
                columnName = self.__resultObject.resultDefinition.keys()[colNr]
                value = self.__resultObject.result[rowNr].get(columnName)

                return value

    def headerData(self, column:int, orientation:int, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            columnLabel = self.__resultObject.resultDefinition.values()[column]
            return columnLabel


class ResultDetails(QtWidgets.QWidget):

    resultDetailDisplay = QtCore.pyqtSignal('PyQt_PyObject')

    def __init__(self):
        super().__init__()

    def setupUi(self):
        layout = QtWidgets.QVBoxLayout()
        self.table = QtWidgets.QTableView()
        layout.addWidget(self.table)
        self.setVisible(False)
        self.resultDetailDisplay.connect(self.on_resultDetailDisplay)

    @QtCore.pyqtSlot('PyQt_PyObject')
    def on_resultDetailDisplay(self, resultObject):
        pass

    def setModel(self, model):
        self.model = model
        self.table.setModel(model)

