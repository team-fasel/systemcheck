from systemcheck.plugins import SystemBasePlugin
from systemcheck.systems.ABAP.models import SystemABAPClient, SystemABAP, SystemABAPFolder
from systemcheck.systems.generic.models import GenericSystemTreeNode

class SystemABAPPlugin(SystemBasePlugin):

    def __init__(self, *args, **kwargs):
        super().__init__()

        self.setAlchemyObjects([[SystemABAP, SystemABAPClient, SystemABAPFolder, GenericSystemTreeNode]])

