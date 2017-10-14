import logging
from PyQt5 import QtWidgets, QtCore
from systemcheck.gui.qtalcmapper import generateQtDelegate
from systemcheck.gui.models import SettingsTableModel
from sqlalchemy_utils.functions import get_type
from systemcheck import models


class ParameterWidget(QtWidgets.QWidget):
    """ A Simple Model/View based Parameter Widget


    """

    updateParameters = QtCore.pyqtSignal('PyQt_PyObject', 'PyQt_PyObject')

    def __init__(self, model:QtCore.QAbstractItemModel=None, currentIndex:QtCore.QModelIndex=None, parent=None):
        """ Parameter Initt

        :param model: A QAbstractItemModel
        :param currentIndex: Current Index"""

        super().__init__(parent)
        self.logger=logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))

        self.updateParameters.connect(self.on_updateParameters)

        if model and currentIndex:
            self.updateParameters.emit(model, currentIndex)

    def on_updateParameters(self, model, currentIndex):
        self.model = model

        layout=QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        treeNode=self.model.getNode(currentIndex)
        self.setVisible(False)
        if treeNode:
            self.alchemyObject = treeNode
            self.setLayout(layout)
            self.delegate=generateQtDelegate(self.alchemyObject)
            self.model=SettingsTableModel(self.alchemyObject)
            columns = self.alchemyObject._qt_columns()
            self.table = QtWidgets.QTableView()
            self.table.setWordWrap(True)
            self.table.setAlternatingRowColors(True)
            self.table.setModel(self.model)
            self.table.setItemDelegate(self.delegate)
            self.delegate.itemView=self.table
            self.table.horizontalHeader().hide()
            self.table.verticalHeader().hide()
            self.table.horizontalHeader().setStretchLastSection(True)

            for colNr, column in enumerate(columns):
                #we always want to show the drop down box instead of double clicking
                if self.persistentEditor(column):
                    self.table.openPersistentEditor(self.model.index(colNr, 1))

            layout.addWidget(self.table)
            self.table.resizeRowsToContents()
            self.table.resizeColumnsToContents()

    def persistentEditor(self, alcObject):
        """ Check whether a persistent Editor should be opened immediately


        :param alcObject: The SQLAlchemy column object to analyze """

#        if alcObject.choices:
#            return True

        alchemyType = get_type(alcObject)

        persistentEditorTypes = [models.meta.Boolean,
                                 models.meta.RichString,
#                                 models.meta.Integer,
#                                 models.meta.String,
#                                 models.meta.LongString,
                                 ]

        for persistenEditorType in persistentEditorTypes:
            if isinstance(alchemyType, persistenEditorType):
                return True
        return False
