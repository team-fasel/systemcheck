from systemcheck.systems.generic.gui.widgets import GenericSystemWidget, GenericSystemSettingsWidget
from PyQt5 import QtWidgets, QtGui, QtCore
from systemcheck.resources import icon_rc
from systemcheck.systems import ABAP
from systemcheck.systems import generic
#from systemcheck.systems.ABAP.models import SystemAbapClient, SystemAbap
#from systemcheck.systems.generic.models import GenericSystemTreeNode
from systemcheck.gui import utils as guiutils
import traceback



class AbapSystemsWidget(GenericSystemWidget):
    """ ABAP Specific System Widget """

    def __init__(self, model: QtCore.QAbstractItemModel = None):
        super().__init__()



        self.newClient_act = QtWidgets.QAction(QtGui.QIcon(":Plus"), 'New ABAP Client', self)
        self.newClient_act.triggered.connect(self.newClient)

        if model:
            self.setModel(model)


    def newClient(self):
        index = self.tree.currentIndex()
        source_index = self.system_model.mapToSource(index)
        source_model=self.system_model.sourceModel()
        clientItem = ABAP.models.SystemAbapClient(client='xxx')
        source_model.insertRow(position=0, parent=source_index, nodeObject=clientItem)


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
        node = self.system_model.getNode(index)

        if node is None:
            menu.addAction(self.newFolder_act)
            menu.addAction(self.newSystem_act)
            menu.addAction(self.deleteItem_act)
            self._rootLevelSelected=True
        else:
            self._rootLevelSelected=False
            if isinstance(node, ABAP.models.SystemAbap):
                menu.addAction(self.newClient_act)
                menu.addAction(self.deleteItem_act)
            elif isinstance(node, ABAP.models.SystemAbapClient):
                menu.addAction(self.updatePassword_act)
                menu.addAction(self.deleteItem_act)
            elif isinstance(node, generic.models.GenericSystemTreeNode):
                menu.addAction(self.newFolder_act)
                menu.addAction(self.newSystem_act)
                menu.addAction(self.deleteItem_act)


        return menu

    def generateSettingsWidget(self, selected:QtCore.QModelIndex):
        """ Generate the widget that allows configuration of systems

        The settings widget is generated dynamically based on the SQLAlchemy object behind the selected tree node.

        """
        system_node = False
        treenode = selected.internalPointer()
        if treenode is not None:
            if treenode.parent_id is not None:
                system_node = getattr(treenode, treenode.type)
            if system_node:
                settingsw=GenericSystemSettingsWidget(self.system_model, selected)
                return settingsw
        return False
