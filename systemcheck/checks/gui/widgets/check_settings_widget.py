from PyQt5 import QtWidgets, QtCore, QtGui
from systemcheck import gui, checks
import logging
from collections import OrderedDict
from typing import Any
from pprint import pprint
from systemcheck.gui.models import SettingsTableModel
from sqlalchemy_utils.functions import get_type
from systemcheck import models
class CheckSettingsWidget(QtWidgets.QWidget):
    """ Check Settings Widget


    The Check Settings Widget handles the complete configuration of a Check. The Check Settings Widget consistes of multiple
    other widgets:

    - CheckParameterEditor
    """


    updateCheck = QtCore.pyqtSignal('PyQt_PyObject', 'PyQt_PyObject')

    def __init__(self):
        super().__init__()

        self.widgets=OrderedDict()
        self.dataMapper = QtWidgets.QDataWidgetMapper()
        self.setupUi()
        self.updateCheck.connect(self.on_upateCheck)

    def setupUi(self):
        layout=QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)
        self.settings_tabw = QtWidgets.QTabWidget()
        layout.addWidget(self.settings_tabw)


    def _clearTabWidget(self):
        while self.settings_tabw.count():
            self.settings_tabw.removeTab(0)

    def addParameterTab(self, widget):
        self.settings_tabw.addTab(widget)

    def on_upateCheck(self, alchemy_object, parameterForm):
        self._clearTabWidget()
        if parameterForm:
            raise NotImplemented
        else:
            model=SettingsTableModel(alchemy_object)
            delegate=gui.qtalcmapper.generateQtDelegate(alchemy_object)
            parameterSettingsWidget=QtWidgets.QTableView()
            parameterSettingsWidget.setAlternatingRowColors(True)
            parameterSettingsWidget.setModel(model)
            parameterSettingsWidget.setItemDelegate(delegate)
            parameterSettingsWidget.horizontalHeader().hide()
            parameterSettingsWidget.verticalHeader().hide()
            parameterSettingsWidget.resizeColumnsToContents()
            parameterSettingsWidget.resizeRowsToContents()
            parameterSettingsWidget.horizontalHeader().setStretchLastSection(True)

            for colNr, column in enumerate(alchemy_object.__qtmap__):
                # we always want to show the drop down box instead of double clicking
                if self.persistentEditor(column):
                    parameterSettingsWidget.openPersistentEditor(model.index(colNr, 1))
        self.settings_tabw.addTab(parameterSettingsWidget, 'Parameters')

    def persistentEditor(self, alcObject):
        """ Check whether a persistent Editor should be opened immediately


        :param alcObject: The SQLAlchemy column object to analyze """

        if alcObject.choices:
            return True

        alchemyType = get_type(alcObject)

        persistentEditorTypes = [models.meta.Boolean,
                                 models.meta.RichString,
                                 models.meta.LongString,
                                 ]

        for persistenEditorType in persistentEditorTypes:
            if isinstance(alchemyType, persistenEditorType):
                return True
        return False
