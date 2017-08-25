from PyQt5 import QtWidgets, QtCore, QtGui
import systemcheck
import logging
from systemcheck.gui.qtalcmapper import generateQtDelegate, getQtWidgetForAlchemyType
from collections import OrderedDict
from typing import Any
from pprint import pprint

class CheckSettingsWidget(QtWidgets.QWidget):

    updateCheck = QtCore.pyqtSignal('PyQt_PyObject')

    def __init__(self):
        super().__init__()

        self.widgets=OrderedDict()
        self.tablew = QtWidgets.QTableWidget(0, 2)
        self.dataMapper = QtWidgets.QDataWidgetMapper()
        self.setupUi()
        self.updateCheck.connect(self.on_upateCheck)

    def setupUi(self):
        layout=QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.tablew.setAlternatingRowColors(True)
        self.tablew.horizontalHeader().hide()
        self.tablew.verticalHeader().hide()
        self.tablew.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.tablew)


    def on_upateCheck(self, alchemy_object):
        self.description_model = CheckSettingsModel(alchemy_object)
        self.tablew.setRowCount(0)
        self.dataMapper = QtWidgets.QDataWidgetMapper()
        self.dataMapper.setModel(self.description_model)
        self.widgets = OrderedDict()
        self.delegate = generateQtDelegate(alchemy_object)

        columns = alchemy_object._qt_columns()

        for colNr, column in enumerate(columns):
            if colNr in self.delegate.delegates.keys():
                self.tablew.insertRow(colNr)
                lblWidget = QtWidgets.QTableWidgetItem(column.info.get('qt_label'))
                self.tablew.setItem(colNr, 0, lblWidget)

                wid = getQtWidgetForAlchemyType(column)
                self.dataMapper.addMapping(wid, colNr)
                self.widgets[colNr] = wid
                self.tablew.setCellWidget(colNr, 1, wid)

        self.dataMapper.toFirst()

        self.tablew.resizeColumnsToContents()
        self.tablew.resizeRowsToContents()

class CheckSettingsModel(QtCore.QAbstractItemModel):

    def __init__(self, abstractItem):
        super().__init__()
        self.logger = logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))
        self._abstractItem = abstractItem


    def columnCount(self, parent=None, *args, **kwargs)->int:

        return self._abstractItem._visible_column_count()

    def rowCount(self, parent=None, *args, **kwargs)->int:

        return 1

    def data(self, index: QtCore.QModelIndex, role: int)->Any:
        column = index.column()
        if not index.isValid():
            return False

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return self._abstractItem._qt_data_colnr(index.column())

    def flags(self, index:QtCore.QModelIndex)->int:
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

    def setData(self, index:QtCore.QModelIndex, value: Any, role=QtCore.Qt.EditRole)->bool:
        """ setData Method to make the model modifiable """

        if index.isValid():
            if role == QtCore.Qt.EditRole:
                self._abstractItem._qt_set_value_by_colnr(index.column(), value)

            return True
        return False

    def index(self, row:int, column:int, parent=None)->QtCore.QModelIndex:

        index = self.createIndex(0, column, QtCore.QModelIndex())

        return index

    def parent(self):
        return QtCore.QModelIndex()