from systemcheck.plugins import SystemBasePlugin
from systemcheck.systems.generic.models import GenericSystemTreeNode

class GenericSystemPlugin(SystemBasePlugin):

    def __init__(self, *args, **kwargs):
        super().__init__()

    def alchemyObjects(self):
        return [GenericSystemTreeNode]

    def alchemyRootObject(self):
        return GenericSystemTreeNode