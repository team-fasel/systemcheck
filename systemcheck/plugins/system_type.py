from systemcheck.plugins import BasePlugin
from systemcheck.systems.generic.models import GenericSystemTreeNode
from systemcheck.config import CONFIG

import logging


class SystemBasePlugin(BasePlugin):
    """ The Foundation for all System Type plugins

    """

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.logger = logging.getLogger("{}.{}".format(__name__, self.__class__.__name__))
        self.setAlchemyRoot(GenericSystemTreeNode)
