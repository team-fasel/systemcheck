__authors__     = ['Lars Fasel']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2017'
__license__     = 'GNU AGPLv3'

# maintanence information
__maintainer__  = 'Lars Fasel'
__email__       = 'systemcheck@team-fasel.com'


from systemcheck.config import CONFIG
from systemcheck.checks.models.checks import Check
import systemcheck
from systemcheck.systems import ABAP
from systemcheck.systems.ABAP.plugins import action_types
import sqlalchemy_utils
from PyQt5 import QtWidgets, QtCore, QtGui
from systemcheck.resources import icon_rc
from systemcheck import checks, gui
from collections import OrderedDict
from sqlalchemy import inspect
from typing import Union

class WidgetReference:

    def __init__(self):

        self.__widgets=OrderedDict()

    def getWidget(self, name:str)->QtWidgets.QWidget:
        """ Return the widget by name """
        return self.__widgets[name].get('widget')

    def getLabel(self, name:str)->Union[QtWidgets.QLabel, None]:
        info=self.__widgets[name].get('info')
        if info:
            label=info.get('qt_label')
            return label
        return None

    def addWidget(self, widget, name, info):
        """ Add Widget """
        self.__widgets[name]={'widget':widget, 'name':name, 'info':info}



class Form(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.widgetReference=WidgetReference()
        self.setupUi()


    def setupUi(self):
        splitter = QtWidgets.QSplitter()
        splitter.setOrientation(QtCore.Qt.Vertical)

        self.coreVboxLayout=QtWidgets.QVBoxLayout()
        #coreVboxLayout.setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.coreVboxLayout)

        self.parameterSetName_layout=QtWidgets.QFormLayout()
        parameterSetName_widget=QtWidgets.QWidget()
        parameterSetName_widget.setLayout(self.parameterSetName_layout)
        self.coreVboxLayout.addWidget(parameterSetName_widget)
        self.coreVboxLayout.addWidget(splitter)


        self.standardSelection_layout=QtWidgets.QFormLayout()
        #self.standardSelection_layout.setContentsMargins(0, 0, 0, 0)
        self.selectionCriteria_layout=QtWidgets.QFormLayout()
        #self.selectionCriteria_layout.setContentsMargins(0, 0, 0, 0)

        self.standardSelection_grpbox = QtWidgets.QGroupBox('Standard Selection')
        self.standardSelection_grpbox.setLayout(self.standardSelection_layout)


        self.selectionCriteria_grpbox = QtWidgets.QGroupBox('Selection Criteria')
        self.selectionCriteria_grpbox.setLayout(self.selectionCriteria_layout)

        self.selectionCriteria_tabw = QtWidgets.QTabWidget()

        self.selectionCriteria_documentation_tab = QtWidgets.QWidget()
        self.selectionCriteria_documentation_layout = QtWidgets.QVBoxLayout()
        self.selectionCriteria_documentation_tab.setLayout(self.selectionCriteria_documentation_layout)
        self.selectionCriteria_tabw.addTab(self.selectionCriteria_documentation_tab, 'Documentation')

        self.selectionCriteria_logonData_tab = QtWidgets.QWidget()
        self.selectionCriteria_logonData_layout = QtWidgets.QVBoxLayout()
        self.selectionCriteria_logonData_tab.setLayout(self.selectionCriteria_logonData_layout)
        self.selectionCriteria_tabw.addTab(self.selectionCriteria_logonData_tab, 'Logon Data')

        self.selectionCriteria_defaultValues_tab = QtWidgets.QWidget()
        self.selectionCriteria_defaultValues_layout = QtWidgets.QVBoxLayout()
        self.selectionCriteria_defaultValues_tab.setLayout(self.selectionCriteria_defaultValues_layout)
        self.selectionCriteria_tabw.addTab(self.selectionCriteria_defaultValues_tab, 'Default Values/Parameters')

        self.selectionCriteria_rolesProfiles_tab = QtWidgets.QWidget()
        self.selectionCriteria_rolesProfiles_layout = QtWidgets.QFormLayout()
        self.selectionCriteria_rolesProfiles_tab.setLayout(self.selectionCriteria_rolesProfiles_layout)
        self.selectionCriteria_tabw.addTab(self.selectionCriteria_rolesProfiles_tab, 'Roles/Profiles')

        self.selectionCriteria_authorizations_tab = QtWidgets.QWidget()
        self.selectionCriteria_authorizations_layout = QtWidgets.QVBoxLayout()
        self.selectionCriteria_authorizations_tab.setLayout(self.selectionCriteria_authorizations_layout)
        self.selectionCriteria_tabw.addTab(self.selectionCriteria_authorizations_tab, 'Authorizations')

        self.selectionCriteria_layout.addWidget(self.selectionCriteria_tabw)

        splitter.addWidget(self.standardSelection_grpbox)
        splitter.addWidget(self.selectionCriteria_grpbox)



    @property
    def alchemyObject(self):
        return self.__alchemyObject

    @alchemyObject.setter
    def alchemyObject(self, saObject):
        self.__alchemyObject=saObject

        self.generalModel=checks.gui.models.CheckSettingsModel(abstractItem=saObject)
        self.dataMapper = QtWidgets.QDataWidgetMapper()
        self.dataMapper.setModel(self.generalModel)
        self.widgets = OrderedDict()
        self.delegate = gui.qtalcmapper.generateQtDelegate(saObject)


        columns = self.alchemyObject._qt_columns()

        for colNr, column in enumerate(columns):
            if colNr in self.delegate.delegates.keys():
#                lblWidget = QtWidgets.QLabel(column.info.get('qt_label'))
                wid = gui.qtalcmapper.getQtWidgetForAlchemyType(column)
                self.dataMapper.addMapping(wid, colNr)
            else:
                wid=Table(self.alchemyObject, column.key)

            self.widgetReference.addWidget(wid, name=column.key, info=column.info)

        standardSelection=['IT_USER', 'IT_GROUP', 'IT_UGROUP']
        selectionCriteria_rolesProfiles=[]
        selectionCriteria_authorizations=[]
        selectionCriteria_defaultValues=[]
        selectionCriteria_logonData=[]
        selectionCriteria_documentation=[]


        param_set_name_widget=QtWidgets.QWidget()
        param_set_name_layout=QtWidgets.QFormLayout()
        param_set_name_widget.setLayout(param_set_name_layout)
        label=self.widgetReference.getLabel('param_set_name')
        widget=self.widgetReference.getWidget('param_set_name')
        widget.setStyleSheet('')
        param_set_name_layout.addRow(label, widget)
        self.coreVboxLayout.insertWidget(0, param_set_name_widget)

        for name in standardSelection:
            self.standardSelection_layout.addRow(self.widgetReference.getLabel(name),
                                                 self.widgetReference.getWidget(name))

        for name in selectionCriteria_logonData:
            self.selectionCriteria_logonData_layout

        self.dataMapper.toFirst()

    def _createWidget(self, label, widget):
        layout=QtWidgets.QHBoxLayout()
        displayWidget=QtWidgets.QWidget()
        label_widget=QtWidgets.QLabel(label)
        layout.addWidget(label_widget)
        layout.addWidget(widget)
        displayWidget.setLayout(layout)
        return displayWidget


class Table(QtWidgets.QWidget):

    def __init__(self, abstractItem = None, sectionName=None):
        super().__init__()

        self.abstractItem = abstractItem
        self.sectionName=sectionName
        self.model=TableModel(self.abstractItem, self.sectionName)
        self.setupUi()
        self.initModel()

    @property
    def abstractItem(self):
        return self.__abstractItem

    @abstractItem.setter
    def abstractItem(self, abstractItem):
        self.__abstractItem = abstractItem

    def on_insert(self):
        model=self.table.model()
        model.insertRows(position=0, rows=1)

    def on_delete(self):
        pass

    def on_trash(self):
        model=self.table.model()
        while model.rowCount():
            model.removeRows(0, 1)

    @property
    def sectionName(self):
        return self.__sectionName

    @sectionName.setter
    def sectionName(self, sectionName):
        self.__sectionName = sectionName

    def setupUi(self):
        layout=QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setIconSize(QtCore.QSize(16, 16))

        self.insert_act = QtWidgets.QAction(QtGui.QIcon(':Plus'), 'Add Item...', self)
        self.insert_act.setText('Insert a new record')
        self.insert_act.triggered.connect(self.on_insert)

        self.delete_act = QtWidgets.QAction(QtGui.QIcon(':Minus'), 'Delete Item...', self)
        self.delete_act.setText('Delete selected records')
        self.trash_act = QtWidgets.QAction(QtGui.QIcon(':Trash'), 'Delete All', self)
        self.trash_act.setText('Delete all records')
        self.trash_act.triggered.connect(self.on_trash)

        self.toolbar.addAction(self.insert_act)
        self.toolbar.addAction(self.delete_act)
        self.toolbar.addAction(self.trash_act)

        self.table = QtWidgets.QTableView()
        self.table.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        layout.addWidget(self.table)
        layout.addWidget(self.toolbar)
        self.setLayout(layout)

    def initModel(self):
        self.model = TableModel(self.abstractItem, self.sectionName)
        self.table.setModel(self.model)
        for row in range(self.model.rowCount()):
            for column in range(self.model.columnCount()):
                colType=self.model.objectClass.__qtmap__[column]
                widget=systemcheck.gui.qtalcmapper.getQtWidgetForAlchemyType(colType)
                index=self.table.model().index(row, column)
                self.table.setIndexWidget(index, widget)

        self.delegate=gui.qtalcmapper.generateQtDelegate(self.abstractItem, self.sectionName)
        self.table.setItemDelegate(self.delegate)
        self.table.resizeRowsToContents()
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)

class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, abstractItem, sectionName):
        super().__init__()

        self.abstractItem=abstractItem
        self.sectionName=sectionName

    @property
    def abstractItem(self):
        return self.__abstractItem

    @abstractItem.setter
    def abstractItem(self, abstractItem):
        self.__abstractItem = abstractItem

    @property
    def abstractSection(self):
        """ Relevant Part of the abstract item

        sqlalchemy relationships are lists. The table model only covers a specific piece of the overall abstractItem.
        The abstractSection is the actual object relevant for this model.
        """

        abstractSection=getattr(self.abstractItem, self.sectionName)
        return abstractSection

    @property
    def sectionName(self):
        return self.__sectionName

    @sectionName.setter
    def sectionName(self, sectionName):
        self.__sectionName = sectionName


    def rowCount(self, parent=QtCore.QModelIndex()):
        count=len(self.abstractSection)
        return count

    def columnCount(self, parent=QtCore.QModelIndex()):
        colCount = len(self.objectClass.__qtmap__)
        return colCount

    def data(self, index, role=QtCore.Qt.DisplayRole):

        if role==QtCore.Qt.DisplayRole:

            row = self.abstractSection[index.row()]
            column = row.__qtmap__[index.column()]
            attribute=getattr(row, column.name)
            if type(attribute) == sqlalchemy_utils.types.Choice:
                return attribute.code
            else:
                return attribute

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsSelectable

    def headerData(self, column, orientation, role=QtCore.Qt.DisplayRole):

        if orientation==QtCore.Qt.Horizontal and role==QtCore.Qt.DisplayRole:
            header=self.objectClass.__qtmap__[column].info.get('qt_label')
            return header

    def insertRows(self, position, rows=1, index=QtCore.QModelIndex()):
        """ Insert a row into the model

        :param position: position in which the row should get inserted
        :param rows: number of rows to insert
        :param index: The model index of the parent
        """

        self.beginInsertRows(index, position, position+rows-1)

        for row in range(rows):
            newRow=self.objectClass()
            self.abstractSection.insert(position+row, newRow)
            self.abstractItem._commit()

        self.endInsertRows()

        return True

    @property
    def objectClass(self):
        """ Determine the model class of the section, based of the parent


        """

        for relationship in inspect(self.abstractItem.__class__).relationships:
            if relationship.key==self.sectionName:
                return relationship.mapper.class_


    def removeRows(self, position, rows=1, index=QtCore.QModelIndex()):
        """ Remove row from model

        :param position: Position from which the removal should start
        :param rows: number of rows to delete
        :param index: the index of the parent
        """

        self.beginRemoveRows(index, position, position+rows-1)
        del self.abstractSection[position:position+rows]
        self.abstractItem._commit()
        self.endRemoveRows()

        return True

    def setData(self, index:QtCore.QModelIndex, value, role=QtCore.Qt.EditRole):

        if role!=QtCore.Qt.EditRole:
            return False

        if index.isValid() and 0 <= index.row() < len(self.abstractSection):
            row=self.abstractSection[index.row()]
            column=self.objectClass.__qtmap__[index.column()]
            setattr(row, column.name, value)
            self.dataChanged.emit(index, index)
            return True
        return False

class ActionAbapRsusr002(action_types.ActionAbapSUIM):
    """RSUSR002: Users by Complex Selection Criteria

    This plugin type retrieves user accounts similar to using SUIM with complex selection criteria. It's calling
    function module SUSR_SUIM_API_RSUSR002 which needs to be available in the system. The API to SUIM is delivered in
    OSS Note 1930238. The following Notes are required:
      - 1930238 - SUIM: API for RSUSR002
      - 2166771 - SUIM: SUSR_SUIM_API_RSUSR002 returns incorrect results
      - 1979313 - SUIM | RSUSR002: Search for executable transactions

    The selection options below depend on the version of the system. The list was retrieved using SE37 in a
    SAP NetWeaver 7.50 system

    Import:
        Standard Selection:
            IT_USER       User list
            IT_GROUP      Group for Authorization
            IT_UGROUP     User group general

        Selection Criteria:
            Documentation:
            Logon Data:
                IT_UALIAS     Selection options for Alias
                IT_UTYPE      Selection options for user type
                IT_SECPOL     Selection options for security policy
                IT_SNC        Selection options for SNC
                Selection by Locks:
                    IV_USER_LOCK  Lock status Y=locked, N=unlocked, Space = irrelevant
                    IV_PWD_LOCK   Lock status Y=locked, N=unlocked, Space = irrelevant
                    IV_LOCK       All Users with administrator- or password locks: TRUE (='X') und FALSE (=' ')
                    IV_UNLOCK     Only users without locks: TRUE (='X') und FALSE (=' ')
                IV_FDATE      Validity date from
                IV_TDATE      Validity date until
                IT_LIC_TYPE   Selection options for license types
                IT_ACCNT      Selection options for Account-Id
                IT_KOSTL      Selection options for cost center
            Default Values:
                IT_STCOD      Selection options for start menu
                IT_LANGU      Selection options for language
                IV_DCPFM      Decimal format
                IV_DATFM      Date format
                IV_TIMEFM     Time format (12-/24-Hour display)
                IT_SPLD       Output Device
                IV_TZONE      Time zone
                IV_CATTK      CATT Check indicator (TRUE (='X') und FALSE (=' '))
                IT_PARID      Selection options for Set-/Get-Paramter-Id
            Roles Profile:
                IV_TCODE      Transaktionscode
                IV_START_TX   Only executable transactions
                IT_UREF       Selection options for reference user
                IT_ACTGRPS    Selection options for role
                IT_PROF1      Selection options for profile
                IV_PROF2      Authorization profile in user master maintenance
                IV_PROF3      Authorization profile in user master maintenance
            Authorizations:
                Selection by Field Name:
                    IV_CONV1      Always convert Values (TRUE (='X') und FALSE (=' '))
                    IV_AUTH_FLD   Authorization field name
                Selection by Authorizations:
                    IV_AUTH_VAL   Authorization value
                    IT_OBJCT      Selection options for authorization objects
                Selection by Values:
                    IT_AUTH       Selection options for authorizations
                    IV_CONV       Data element zur Domäne BOOLE: TRUE (='X') und FALSE (=' ')
                    IT_VALUES     Transfer structure for selection by authorization values

    """

    FM = 'SUSR_SUIM_API_RSUSR002'
    RETURNSTRUCTURE='ET_USERS'

    def __init__(self):
        super().__init__()

        self.alchemyObjects = [ABAP.models.ActionAbapRsusr002,
                               ABAP.models.ActionAbapRsusr002__params,
                               Check,
                               ABAP.models.ActionAbapFolder]

        report_columns = CONFIG['systemtype_ABAP']['suim.reportcolumns.rsusr002'].split(',')
        header_descriptions = dict(CHECK = 'Checkbox', BNAME = 'Username', USERALIAS='User Alias',
                                                         CLASS = 'User Group', LOCKICON = 'Lockicon',
                                                         LOCKREASON = 'Lock Reason', GLTGV = 'Valid From',
                                                         GLTGB = 'Valid Until', USTYP = 'User Type',
                                                         REFUSER = 'Reference User', ACCNT = 'ACCNT',
                                                         KOSTL = 'Cost Center', NAME_TEXT = 'Name',
                                                         DEPARTMENT = 'Department', FUNCTION = 'Function',
                                                         BUILDING_C = 'Building', FLOOR_C = 'Floor', ROOMNUM_C = 'Room',
                                                         TEL_NUMBER = 'Phone Number', TEL_EXTENS = 'Phone Extension',
                                                         NAME1 = 'Name 1', NAME2 = 'Name 2', NAME3 = 'Name 3',
                                                         NAME4 = 'Name 4', POST_CODE1 = 'Zip Code', CITY1 = 'City',
                                                         STREET = 'Street', COUNTRY = 'Country', TZONE = 'Time Zone',
                                                         SECURITY_POLICY = 'Security Policy', EMAIL = 'eMail')


        for column in report_columns:
            self.actionResult.addResultColumn(column, header_descriptions.get(column) or column)

        self.parameterForm = Form()