from systemcheck.plugins import SystemBasePlugin
from systemcheck.systems.ABAP.models import SystemABAPClient, SystemABAP, SystemABAPFolder
from systemcheck.systems.generic.models import GenericSystemTreeNode
from systemcheck.systems.generic.gui.widgets import GenericSystemMainWidget
from systemcheck.systems import ABAP

class SystemABAPPlugin(SystemBasePlugin):

    TABNAME = 'ABAP'
    SYSTEMFILTER=[SystemABAP, SystemABAPClient, SystemABAPFolder, GenericSystemTreeNode]


    def __init__(self, *args, **kwargs):
        super().__init__()

        self.setAlchemyObjects([])


    def widget(self):

        systemsWidget = ABAP.gui.widgets.AbapSystemsWidget
        widget = GenericSystemMainWidget(systemsWidget=systemsWidget)
        widget.setSystemFilter(self.SYSTEMFILTER)



        return widget

