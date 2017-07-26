from systemcheck.systems.generic.gui.widgets import SystemsWidget, SettingsWidget
from PyQt5 import QtWidgets, QtGui, QtCore
from systemcheck.resources import icon_rc
from systemcheck.systems.ABAP.models import AbapClient, AbapSystem, AbapTreeNode
from systemcheck.systems.generic.model import GenericTreeNode
import systemcheck.gui.utils as guiutils
import traceback



class AbapSystemsWidget(SystemsWidget):

    def __init__(self, model: QtCore.QAbstractItemModel = None):
        super().__init__(model)

        self.addSystem_act = QtWidgets.QAction(QtGui.QIcon(":Plus"), 'Add ABAP System', self)
        self.addSystem_act.triggered.connect(self.addSystem)

        self.addClient_act = QtWidgets.QAction(QtGui.QIcon(":Plus"), 'Add ABAP Client', self)
        self.addClient_act.triggered.connect(self.addClient)

        self.updatePassword_act = QtWidgets.QAction(QtGui.QIcon(":Password"), 'Update Password', self)
        self.updatePassword_act.triggered.connect(self.updatePassword)


    def addClient(self):
        index = self.tree.currentIndex()
        clientItem = AbapClient(client='xxx')
        try:
            tree_node = AbapTreeNode(name='New ABAP Client', type=clientItem.RELNAME)
        except Exception as err:
            traceback.print_exc(err)
        setattr(tree_node, tree_node.type, clientItem)
        self.model.insertRow(position=0, parent=index, nodeObject=tree_node)

    def addSystem(self):
        if len(self.tree.selectedIndexes()) == 0:
            index = QtCore.QModelIndex()
        else:
            index = self.tree.currentIndex()

        system_item = AbapSystem()
        try:
            tree_node = AbapTreeNode(name='New ABAP System', type=system_item.RELNAME)
        except Exception as err:
            traceback.print_exc(err)
        setattr(tree_node, tree_node.type, system_item)
        self.model.insertRow(position=0, parent=index, nodeObject=tree_node)

    def updatePassword(self):
        """ Update the password for a client


        """

        #TODO: Refactor to make this a generic function. Nicer UI and integrat into the settings widget
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
                index = self.tree.currentIndex()
                node = index.internalPointer()
                if node.type == 'abap_client':
                    systemnode=node._system_node()
                    systemnode.password = pwd
                    guiutils.message('Password Updated', windowIcon=pwdicon)
            else:
                guiutils.message(windowIcon=pwdicon, text="Passwords Don't Match")



    def systemSpecificContextMenu(self, position, menu):
        index = self.tree.indexAt(position)
        node = index.internalPointer()

        if node is None:
            menu.addAction(self.addFolder_act)
            menu.addAction(self.addSubFolder_act)
            menu.addAction(self.addSystem_act)
            menu.addAction(self.deleteItem_act)
        else:
            if node.type == 'FOLDER':
                menu.addAction(self.addFolder_act)
                menu.addAction(self.addSystem_act)
                menu.addAction(self.deleteItem_act)
            elif node.type == 'abap_system':
                menu.addAction(self.addClient_act)
                menu.addAction(self.deleteItem_act)
            elif node.type == 'abap_client':
                menu.addAction(self.updatePassword_act)
                menu.addAction(self.deleteItem_act)
        return menu

    def generateSettingsWidget(self, selected:QtCore.QModelIndex):
        """ Generate the widget that allows configuration of systems

        The settings widget is generated dynamically based on the SQLAlchemy object behind the selected tree node.

        """
        system_node = False
        treenode = selected.internalPointer()
        if treenode is not None:
            if treenode.type != 'FOLDER':
                system_node = getattr(treenode, treenode.type)
            if system_node:
                settingsw=SettingsWidget(self.model, selected)
                return settingsw

        return False
