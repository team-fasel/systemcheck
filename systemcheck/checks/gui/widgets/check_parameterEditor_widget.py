from PyQt5 import QtWidgets, QtCore, QtGui
import systemcheck
import logging
#from systemcheck.gui.qtalcmapper import generateQtDelegate, getQtWidgetForAlchemyType
#from systemcheck import checks
from systemcheck.checks.gui.widgets import CheckSettingsWidget
from collections import OrderedDict
from typing import Any
from pprint import pprint
from systemcheck.resources import icon_rc



class CheckParameterEditorWidget(CheckSettingsWidget):
    """ Configure System Settings


    """

    #TODO: Drag and Drop for Parameter sets


    updateCheck = QtCore.pyqtSignal('PyQt_PyObject', 'PyQt_PyObject')

    def __init__(self):
        self.logger=logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))
        super().__init__()

    def setupUi(self):

        layout=QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.addParamSet_act = QtWidgets.QAction(QtGui.QIcon(":Plus"), 'Add Parameter Set', self)
        self.addParamSet_act.triggered.connect(self.on_addParamSet)
        self.insertParamSet_act = QtWidgets.QAction(QtGui.QIcon(":Plus"), 'Insert Parameter Set', self)
        self.insertParamSet_act.triggered.connect(self.on_insertParamSet)
        self.deleteParamSet_act = QtWidgets.QAction(QtGui.QIcon(":Trash"), 'Delete Parameter Set', self)
        self.deleteParamSet_act.triggered.connect(self.on_deleteParamSet)

        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.addAction(self.addParamSet_act)
        self.toolbar.addAction(self.deleteParamSet_act)


        self.setLayout(layout)

        self.parameter_layout = QtWidgets.QVBoxLayout()
        self.parameter_layout.setContentsMargins(0, 0, 0, 0)

        self.parameterSets_table = QtWidgets.QTableView()
        self.parameterSets_table.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.parameterSets_table.setSelectionMode(QtWidgets.QTableView.SingleSelection)

        self.parameter_layout.addWidget(self.parameterSets_table)
        self.parameter_layout.addWidget(self.toolbar)

        iterimWidget=QtWidgets.QWidget()
        iterimWidget.setLayout(self.parameter_layout)

        self.parameters_splitter = QtWidgets.QSplitter()
        self.parameters_splitter.addWidget(iterimWidget)

        self.parameterSettings_widget = CheckSettingsWidget()
        self.parameters_splitter.addWidget(self.parameterSettings_widget)
        layout.addWidget(self.parameters_splitter)

    def on_parameter_selectionChanged(self):
        """ Update Widget with selected Parameter Set

        Gets executed when a parameter set is selected
        """
        current = self.parameterSets_table.currentIndex()
        object = self.alchemy_object.params[current.row()]
        self.parameterSettings_widget.updateCheck.emit(object, self.parameterForm)
        self.parameterSettings_widget.setVisible(True)

    def on_upateCheck(self, alchemy_object, parameter_form):
        """ Update Generic Check Parameter Widget with selected Check


        """


        self.parameterForm=parameter_form
        self.alchemy_object=alchemy_object
        self.parameterSettings_widget.setVisible(False)
        self.parameterTable_model = CheckParameterTableModel(alchemy_object)
        self.parameterSets_table.setModel(self.parameterTable_model)
        self.parameterSets_table.selectionModel().selectionChanged.connect(self.on_parameter_selectionChanged)
        self.parameterSets_table.horizontalHeader().setStretchLastSection(True)
        self.parameterSets_table.resizeColumnsToContents()
        self.parameterSets_table.resizeRowsToContents()

    def on_addParamSet(self):
        """ Add a new Parameter Set """
        self.parameterTable_model.insertRows(self.parameterTable_model.rowCount())

    def on_insertParamSet(self):
        current = self.parameter_table.currentIndex()
        if current.isValid():
            self.parameterTable_model.insertRows(current.row())

    def on_deleteParamSet(self):
        current = self.parameterSets_table.currentIndex()
        if current.isValid():
            self.parameterTable_model.removeRows(current.row())

class CheckParameterTableModel(QtCore.QAbstractTableModel):

    def __init__(self, checknode=None, parent=None):
        super(CheckParameterTableModel, self).__init__(parent)
        self.__headings = []
        self.__checknode=checknode

    def alchemyObject(self):
        return self.__checknode

    def rowCount(self, index:QtCore.QModelIndex=QtCore.QModelIndex()):
        """ Returns the number of rows the model holds. """
        nrows = self.__checknode
        return self.__checknode._parameter_count()

    def columnCount(self, index:QtCore.QModelIndex=QtCore.QModelIndex()):
        """ Returns the number of columns the model holds. """
        return 1


    def data(self, index, role:int=QtCore.Qt.DisplayRole):
        """ Depending on the index and role given, return data. If not
            returning data, return None (PySide equivalent of QT's
            "invalid QVariant").
        """
        if not index.isValid():
            return None

        rowNr=index.row()
        colNr=index.column()

        if not 0 <= rowNr < len(self.__checknode.params):
            return None

        if role == QtCore.Qt.DisplayRole:
            param = self.__checknode.params[rowNr]
            column = param.__qtmap__[colNr]

            value = getattr(param, column.name)
            return value

        return None

    def headerData(self, section, orientation:int, role:int=QtCore.Qt.DisplayRole):
        """ Set the headers to be displayed. """
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return 'Parameter Set'

        return None

    def insertRows(self, position:int, rows:int=1, index:QtCore.QModelIndex=QtCore.QModelIndex()):
        """ Insert a row into the model. """
        self.beginInsertRows(QtCore.QModelIndex(), position, position + rows - 1)

        check_alc_object = type(self.__checknode)
        objectClass = check_alc_object.params.property.mapper.class_


        for row in range(rows):
            if objectClass:
                object = objectClass(param_set_name='< New >')
                self.__checknode.params.insert(position + row, object)

        self.endInsertRows()
        return True

    def removeRows(self, position, rows=1, index:QtCore.QModelIndex=QtCore.QModelIndex()):
        """ Remove a row from the model. """
        self.beginRemoveRows(QtCore.QModelIndex(), position, position + rows - 1)

        del self.__checknode.params[position:position + rows]
        self.__checknode._commit()

        self.endRemoveRows()
        return True

    def setData(self, index, value, role=QtCore.Qt.EditRole):

        if index.isValid():
            if role == QtCore.Qt.EditRole:
                rowNr=index.row()
                colNr=index.column()

                param = self.__checknode.params[rowNr]
                param._qt_set_value_by_colnr(colnr=colNr, value=value)


    def flags(self, index):
        """ Set the item flags at the given index. Seems like we're
            implementing this function just to see how it's done, as we
            manually adjust each tableView to have NoEditTriggers.
        """
        if index.isValid():
            return QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled

