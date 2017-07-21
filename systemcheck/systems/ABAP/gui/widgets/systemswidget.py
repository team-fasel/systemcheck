from systemcheck.systems.generic.gui.widgets import SystemsWidget, SettingsWidget
from PyQt5 import QtWidgets, QtGui, QtCore
from systemcheck.resources import icon_rc
from systemcheck.systems.ABAP.models import AbapClient, AbapSystem
from systemcheck.systems.generic.model import GenericTreeNode



class AbapSystemsWidget(SystemsWidget):

    def __init__(self, model: QtCore.QAbstractItemModel = None):
        super().__init__(model)

        self.addSystem_act = QtWidgets.QAction(QtGui.QIcon(":Plus"), 'Add ABAP System', self)
        self.addSystem_act.triggered.connect(self.addSystem)

        self.addClient_act = QtWidgets.QAction(QtGui.QIcon(":Plus"), 'Add ABAP Client', self)
        self.addClient_act.triggered.connect(self.addClient)

    def addClient(self):
        pass

    def addSystem(self):
        index = self.tree.currentIndex()

        system_item = AbapSystem()
        tree_node = GenericTreeNode(name='New ABAP System', type=system_item.RELNAME)
        setattr(tree_node, tree_node.type, system_item)
        self.model.insertRow(position=0, parent=index, nodeObject=tree_node)

    def systemSpecificContextMenu(self, position, menu):
        index = self.tree.indexAt(position)
        node = index.internalPointer()

        if node is None:
            menu.addAction(self.addSystem_act)
        else:
            if node.type == 'FOLDER':
                menu.addAction(self.addSystem_act)
            elif node.type == 'ABAP':
                menu.addAction(self.addClient_act)

        return menu

    def generateSettingsWidgetXX(self, selected:QtCore.QModelIndex):
        """ Generate the widget that allows configuration of systems

        The settings widget is generated dynamically based on the SQLAlchemy object behind the selected tree node.

        """
        systemnode = None
        treenode = selected.internalPointer()
        if treenode.type != 'FOLDER':
            system_node = getattr(treenode, treenode.type)
        if system_node:
            settingsw=SettingsWidget(self.model, selected)
            return settingsw