from PyQt5 import QtWidgets, QtCore, QtGui
import systemcheck
import logging
from systemcheck.gui.qtalcmapper import generateQtDelegate, getQtWidgetForAlchemyType
#from systemcheck.checks.gui.models import
from collections import OrderedDict
from systemcheck.gui.utils import ComboBoxModel, comboBox
from typing import Any
from pprint import pprint
from sqlalchemy import inspect
from systemcheck.resources import icon_rc

class ComboBoxItemDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, parent, choices):
        super().__init__(parent)
        self.choices=choices

    def createEditor(self, parent, option, index):
        if index.column() != 0:
            return QtWidgets.QStyledItemDelegate.createEditor(parent, option, index)


        editor=QtWidgets.QComboBox()
        editor.addItems(self.choices)
        editor.setCurrentIndex(0)
        editor.installEventFilter(self)
        return editor

    def setEditorData(self, editor, index):
        value=index.data

    def setModelData(self, QWidget, QAbstractItemModel, QModelIndex):
        pass



class CheckRestrictionsEditorWidget(QtWidgets.QWidget):
    """ Configure System Settings


    """

    #TODO: Drag and Drop for Parameter sets


    updateRestrictions = QtCore.pyqtSignal('PyQt_PyObject', 'PyQt_PyObject')

    def __init__(self):
        super().__init__()
        self.logger=logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))
        self.setupUi()

    def setupUi(self):

#        layout=QtWidgets.QVBoxLayout()
#        layout.setContentsMargins(0, 0, 0, 0)

        self.addRestriction_act = QtWidgets.QAction(QtGui.QIcon(":Plus"), 'Add Restriction', self)
        self.addRestriction_act.triggered.connect(self.on_addRestriction)
        self.removeRestriction_act = QtWidgets.QAction(QtGui.QIcon(":Minus"), 'Remove Restriction', self)
        self.removeRestriction_act.triggered.connect(self.on_removeRestriction)
        self.deleteRestriction_act = QtWidgets.QAction(QtGui.QIcon(":Trash"), 'Delete Restriction', self)
        self.deleteRestriction_act.triggered.connect(self.on_deleteRestrictions)

        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.addAction(self.addRestriction_act)
        self.toolbar.addAction(self.removeRestriction_act)
        self.toolbar.addAction(self.deleteRestriction_act)


        self.restrictions_layout = QtWidgets.QVBoxLayout()
        self.restrictions_layout.setContentsMargins(0, 0, 0, 0)

        self.restrictions_table = QtWidgets.QTableView()
        self.restrictions_table.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.restrictions_table.setSelectionMode(QtWidgets.QTableView.SingleSelection)

        self.restrictions_layout.addWidget(self.restrictions_table)
        self.restrictions_layout.addWidget(self.toolbar)
        self.setLayout(self.restrictions_layout)


    def on_upateRestrictions(self, alchemy_object, parameterForm):
        if parameterForm:
            self.generateForm(parameterForm)
            if alchemy_object:
                self.parameterForm.alchemyObject = alchemy_object
        else:
            if alchemy_object:
                self.restrictions_model=systemcheck.checks.gui.models.CheckRestrictionModel(checknode=alchemy_object,
                                                                                        parent=None)
                self.restrictions_table.setModel(self.restrictions_model)
                self.restrictions_table.resizeRowsToContents()
                self.restrictions_table.resizeColumnsToContents()
                self.restrictions_table.horizontalHeader().setStretchLastSection(True)

                nodeclass=inspect(type(alchemy_object)).relationships['restrictions'].mapper.class_
                node=nodeclass()
                delegate=generateQtDelegate(node)

                for colnr, column in enumerate(node.__qtmap__):
                    self.restrictions_table.setItemDelegateForColumn(colnr, delegate)


    def on_addRestriction(self):
        """ Add a new Parameter Set """
        rows=self.restrictions_model.rowCount()
        self.restrictions_model.insertRows(rows)


    def on_clearRestrictions(self):
        pass

    def on_deleteRestrictions(self):
        pass

    def on_removeRestriction(self):
        current = self.restrictions_table.currentIndex()
        if current.isValid():
            self.parameterTable_model.removeRows(current.row())
