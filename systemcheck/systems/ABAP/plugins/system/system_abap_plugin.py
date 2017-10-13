from systemcheck.plugins import SystemBasePlugin
from systemcheck.systems.ABAP.models import SystemAbapClient, SystemAbap, SystemAbapFolder
from systemcheck.systems.generic.models import GenericSystem, GenericSystemTreeNode
from systemcheck.systems.generic.gui.widgets import GenericSystemMainWidget
from systemcheck.systems import ABAP
from PyQt5 import QtWidgets
from collections import namedtuple


class AbapMainWidget(GenericSystemMainWidget):

    def __init__(self, systemType='ABAP', systemFilter:list = None, systemsWidget:QtWidgets.QWidget=None):
        super().__init__(systemType=systemType, systemFilter=systemFilter, systemsWidget=systemsWidget)

    def buildTaskList(self, systems, checks):
        """ Build the Task List for ABAP Systems

        :param systems: A set of Systems that were checked
        :param checks: A set of Checks that were checked

        """

        taskList = set()
        Task = namedtuple('Task', 'system check')

        if systems and checks:
            clientIndependentSystems=set()
            sids=[item.parent_node.sid for item in systems]
            for system in systems:
                if sids.count(system.parent_node.sid) == 1:
                    clientIndependentSystems.add(system)
                else:
                    clientIndependentSystems.add(system.getDefaultClient())

            for check in checks:
                if check.client_specific:
                    for system in systems:
                        taskList.add(Task(system=system, check=check))
                else:
                    for system in clientIndependentSystems:
                        taskList.add(Task(system=system, check=check))

        return taskList

class SystemABAPPlugin(SystemBasePlugin):

    def __init__(self, *args, systemType = None, **kwargs):
        super().__init__()

        self.systemType = 'ABAP'
        self.systemFilter = [SystemAbap, SystemAbapClient, SystemAbapFolder, GenericSystemTreeNode]
        self.systemsWidget = ABAP.gui.widgets.AbapSystemsWidget
        self.systemFolderObject = SystemAbapFolder
        self.systemObject = SystemAbap
        self.checkFolderObject = ABAP.models.ActionAbapFolder


    def widget(self):

        widget = AbapMainWidget(systemsWidget=self.systemsWidget)
        widget.systemType=self.systemType
        widget.systems.setFolderObject(self.systemFolderObject)
        widget.systems.setSystemObject(self.systemObject)
        widget.systemFilter=self.systemFilter

        return widget
