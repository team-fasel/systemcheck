from PyQt5 import QtCore, QtWidgets, QtGui

from systemcheck.results.gui.widgets import ResultDisplay


class ResultTableModel(QtCore.QAbstractTableModel):

    resultAdd_signal = QtCore.pyqtSignal('PyQt_PyObject')

    def __init__(self):
        super().__init__()

        self.__results = []
        self.__headers = ['Check Name', 'System', 'Rating', 'Object']

        self.resultAdd_signal.connect(self.on_resultAdd)

    def _getObject(self, index):

        if index.isValid():
            rowNr = index.row()
            return self.__results[rowNr]

    def columnCount(self, parent=None, *args, **kwargs):
        """ For this model, we need only a few columns:

        0: The name of the Check (object.check_name)
        1: The name of the system (object.systeminfo)
        2: The check rating (object.rating)

        """

        column_count = 3
        return column_count

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            rowNr = index.row()
            colNr = index.column()

            if colNr==0:
                value = self.__results[rowNr].check_name
                return value
            elif colNr==1:
                value = self.__results[rowNr].systeminfo
                return value
            elif colNr==2:
                value = self.__results[rowNr].rating
                return value


    def headerData(self, colNr:int, orientation:int=QtCore.Qt.Horizontal, role=QtCore.Qt.DisplayRole):

        if orientation==QtCore.Qt.Horizontal:
            return self.__headers[colNr]

    def on_resultAdd(self, resultObject):
        self.__results.append(resultObject)


    def removeRows(self, position:int, count:int, parent=None, *args, **kwargs):
        """ Remove rows from the model """
        self.beginRemoveRows(QtCore.QModelIndex(), position, position + count - 1)
        del self.__results[position:position+count]
        self.endRemoveRows()

        return True

    def rowCount(self, parent=None, *args, **kwargs):
        row_count = len(self.__results)
        return row_count


class ResultWidget(QtWidgets.QWidget):

    resultExport_signal = QtCore.pyqtSignal()
    resultImport_signal = QtCore.pyqtSignal()
    resultAdd_signal = QtCore.pyqtSignal('PyQt_PyObject')
    resultClear_signal = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi()

    def on_resultClear(self):

        resultCount=self.model.rowCount()
        self.model.removeRows(0, resultCount)

    def on_resultExport(self):
        pass

    def on_resultImport(self):
        pass

    def setupUi(self):

        self.model = ResultTableModel()
        self.resultAdd_signal.connect(self.model.on_resultAdd)
        self.resultClear_signal.connect(self.on_resultClear)
        self.resultExport_signal.connect(self.on_resultExport)
        self.resultImport_signal.connect(self.on_resultImport)

        self.ui = ResultDisplay()
        self.ui.setModel(self.model)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        self.setLayout(layout)
        self.show()




