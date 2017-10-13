import logging
import sys
from collections import OrderedDict

from PyQt5 import QtWidgets, QtCore, QtGui
from systemcheck import models
from systemcheck.gui.qtalcmapper import generateQtDelegate, getQtWidgetForAlchemyType
from systemcheck.gui.widgets import TreeView, ParameterWidget
from systemcheck.gui.models import SettingsModel, SettingsTableModel
from systemcheck.gui.utils import message
from systemcheck.systems import generic

from sqlalchemy_utils.functions import get_type

from pprint import pprint

__authors__     = ['Lars Fasel']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2017'
__license__     = 'MIT'


def exception_hook(exctype, value, traceback):
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


class GenericSystemSettingsWidget(QtWidgets.QWidget):
    """ Configure System Settings


    """

    def __init__(self, model, currentIndex, parent=None):

        self.logger=logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))
        super().__init__(parent)
        self.model = model

        layout=QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        treeNode=self.model.getNode(currentIndex)
        self.setVisible(False)
        if treeNode:
            if treeNode.type !='FOLDER':
                self.alchemyObject = treeNode
                self.setLayout(layout)
                self.delegate=generateQtDelegate(self.alchemyObject)
                self.model=SettingsTableModel(self.alchemyObject)
                columns = self.alchemyObject._qt_columns()
                self.table = QtWidgets.QTableView()
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

        if alcObject.choices:
            return True

        alchemyType = get_type(alcObject)

        persistentEditorTypes = [models.meta.Boolean]

        for persistenEditorType in persistentEditorTypes:
            if isinstance(alchemyType, persistenEditorType):
                return True
        return False


#                self.tablew = QtWidgets.QTableWidget(len(columns), 2)
#                self.tablew.setAlternatingRowColors(True)
#                self.tablew.horizontalHeader().hide()
#                self.tablew.verticalHeader().hide()
#                self.tablew.horizontalHeader().setStretchLastSection(True)
#                layout.addWidget(self.tablew)
#                self.widgets = OrderedDict()

#                for colNr, column in enumerate(columns):
#                    if colNr in self.delegate.delegates.keys():
#                        lblWidget=QtWidgets.QTableWidgetItem(column.info.get('qt_label'))
#                        self.tablew.setItem(colNr, 0, lblWidget)
#                        index=self.model.index(0, colNr)
#                        wid=self.delegate.createEditor(parent=None, option=None, index=index)
#                        self.dataMapper.addMapping(wid, colNr)
#                        self.widgets[colNr]=wid
#                        self.tablew.setCellWidget(colNr, 1, wid)

#                self.dataMapper.toFirst()

#                self.tablew.resizeColumnsToContents()
#                self.tablew.resizeRowsToContents()


class GenericSystemWidget(QtWidgets.QWidget):
    """ The Generic Systems Widget

    The Systems Widget consists of actually 2  or more widgets

    * The TreeView that contains all the systems and displays them in a tree
    * The SystemSettingsWidget that gets geenerated everytime when a system is clicked on in the tree.


    """


    def __init__(self, model: QtCore.QAbstractItemModel=None, folderObject=None, systemObject=None):
        super().__init__()

        self.newSystem_act = QtWidgets.QAction(QtGui.QIcon(":Plus"), 'New System', self)
        self.newSystem_act.triggered.connect(self.on_new)
        self.newFolder_act = QtWidgets.QAction(QtGui.QIcon(":AddFolder"), 'New Folder', self)
        self.newFolder_act.triggered.connect(self.on_newFolder)
        self.updatePassword_act = QtWidgets.QAction(QtGui.QIcon(":Password"), 'Update Password', self)
        self.updatePassword_act.triggered.connect(self.on_updatePassword)


        self.logger = logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))
        self.setupUi()
        if model:
            self.setModel(model)

        self._rootLevelSelected = False

        self.setFolderObject(folderObject)
        self.setSystemObject(systemObject)

    def toolbar(self):
        toolbar = QtWidgets.QToolBar()
        toolbar.addActions([self.systemNew_act, self.systemNewFolder_act])
        toolbar.addSeparator()
        toolbar.addActions([self.systemDelete_act, self.systemImport_act, self.systemExport_act])

    def folderObject(self):
        """ Folder Object

        Systems are organized in Folders. Folders can be generic, but they should be system specific.
        """
        return self._folderObject

    def setFolderObject(self, folderObject):
        """ Set the Folder Object

        Sets the folder object for the system widget

        :param folderObject: A SQLAlchemy object that represents the folder

        """
        if folderObject:
            self._folderObject = folderObject
        else:
            self._folderObject = generic.models.GenericSystemTreeNode

    def systemObject(self):
        return self._systemObject

    def setSystemObject(self, systemObject):
        self._systemObject = systemObject

    def on_changePassword(self):
        pass

    def on_checkLogon(self):
        pass

    def on_delete(self):
        index = self.tree.currentIndex()

        parent=index.parent()
        if len(self.tree.selectedIndexes()) == 0:
            currentProxyIndex = self.tree.currentIndex()
            currentProxyParentIndex = currentProxyIndex.parent()
            self.system_model.removeRows(row=currentProxyIndex.row(), count=1, parent=currentProxyParentIndex)
        else:
            for index in self.tree.selectedIndexes():
                proxyPoxyParentIndex = index.parent()
                self.system_model.removeRows(row=index.row(), count=1, parent=proxyPoxyParentIndex)


    def on_disable(self):
        pass

    def on_enable(self):
        pass

    def on_export(self):
        pass

    def on_import(self):
        pass

    def on_new(self):
        systemObject=self.systemObject()
        if systemObject:
            if len(self.tree.selectedIndexes()) == 0:
                index = QtCore.QModelIndex()
            else:
                index = self.tree.currentIndex()
                index = self.system_model.mapToSource(index)

            system_item = systemObject(name='New System')

        self.system_model.sourceModel().insertRow(position=0, parent=index, nodeObject=system_item)

    def on_newFolder(self, parent:QtCore.QModelIndex):
        folderObject=self.folderObject()
        folderInstance=folderObject()
        folderInstance.name='New Folder'

        if self._rootLevelSelected:
            parent_index=QtCore.QModelIndex()
        else:
            parent_index=self.tree.currentIndex()

        self.system_model.insertRow(position=0, parent=parent_index, nodeObject=folderInstance)
        self.tree.expand(parent_index)

    def on_treeSelectionChanged(self, selected: QtCore.QModelIndex, deselected: QtCore.QModelIndex):

        splitterWidgetCount=self.splitter.count()
        if splitterWidgetCount >1:
            for index in range(1, splitterWidgetCount):
                widget=self.splitter.widget(index)
                widget.deleteLater()

        settingsw=ParameterWidget(self.system_model, selected)
        if settingsw:
            self.splitter.addWidget(settingsw)
            settingsw.show()
#        self.logger.debug(pformat(node))

    def on_updatePassword(self):


        #TODO: Refactor to make this a generic function. Nicer UI and integration into the settings widget
        pwdicon = QtGui.QIcon(":Password")
        dlg = QtWidgets.QInputDialog(self)
        dlg.setInputMode(QtWidgets.QInputDialog.TextInput)
        dlg.setTextEchoMode(QtWidgets.QLineEdit.Password)
        dlg.setWindowTitle('Update Password')
        dlg.setWindowIcon(pwdicon)
        dlg.setLabelText("Passwords are stored in the OS' secure password storage facility and not in the systemcheck database. \n\nEnter new password: ")
        dlg.resize(500, 100)
        ok = dlg.exec_()
        pwd = dlg.textValue()
        if pwd and ok:
            dlg.setTextValue('')
            dlg.setLabelText("Enter again as confirmation")
            ok2 = dlg.exec_()
            pwd2 = dlg.textValue()

            if pwd == pwd2 and ok2:
                proxy_index = self.tree.currentIndex()
                systemnode = self.system_model.getNode(proxy_index)
                systemnode.password = pwd
                message('Password Updated', windowIcon=pwdicon)
            else:
                message(windowIcon=pwdicon, text="Passwords Don't Match")

    def openContextMenu(self, position):

        menu=QtWidgets.QMenu()
        menu = self.systemSpecificContextMenu(position, menu)
        menu.exec_(self.tree.viewport().mapToGlobal(position))

    def setupUi(self):
        """ Configure the User Interface """

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        label = QtWidgets.QLabel('Systems:')
        layout.addWidget(label)
        self.splitter = QtWidgets.QSplitter()
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.tree = TreeView()
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.openContextMenu)
        self.splitter.addWidget(self.tree)
        layout.addWidget(self.splitter)

        self.treeContextMenu = QtWidgets.QMenu()

        self.addFolder_act = QtWidgets.QAction(QtGui.QIcon(':AddFolder'), 'Add Folder')
        self.deleteItem_act = QtWidgets.QAction(QtGui.QIcon(':Trash'), 'Delete')
        self.deleteItem_act.triggered.connect(self.on_delete)

        self.setLayout(layout)
        self.show()

    def setModel(self, model):
        self.system_model = model
        self.tree.setModel(model)
        self.tree.selectionModel().currentChanged.connect(self.on_treeSelectionChanged)
        self.tree.setColumnHidden(1, True)

    def systemSpecificContextMenu(self, position:QtCore.QPoint, menu:QtWidgets.QMenu):
        """ Generate the system specific context menu

        This function has to be reimplemented in the system specific tree models.

        :param position:  The coordinates of the selected tree node
        :param meny: The generic context menu

        """

        raise NotImplemented