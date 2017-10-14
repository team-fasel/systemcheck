from systemcheck.plugins import BasePlugin
from systemcheck.systems.generic.models import GenericSystem, GenericSystemTreeNode
from systemcheck.config import CONFIG
from systemcheck import utils
import systemcheck
from yapsy.PluginManager import PluginManager


import logging


class SystemBasePlugin(BasePlugin):
    """ The Foundation for all System Type plugins

    """

    def __init__(self, *args, **kwargs):
        super().__init__()

        self.__checksFilter = None
        self.__systemFilter = None
        self.__systemType = None

        self.category='system'

        self.logger = logging.getLogger("{}.{}".format(__name__, self.__class__.__name__))
        self.alchemyRoot = GenericSystemTreeNode

    @property
    def checksFilter(self) -> set:

        checksFilterList = set()
        category = 'check_' + self.systemType
        pm = systemcheck.plugins.SysCheckPM()
        for plugin in pm.getPluginsOfCategory(category_name=category):
            for object in plugin.plugin_object.alchemyObjects:
                checksFilterList.add(object)

        return checksFilterList


    @property
    def systemFilter(self)->list:
        return self.__systemFilter

    @systemFilter.setter
    def systemFilter(self, systemFilter:list):
        self.__systemFilter = systemFilter

    @property
    def systemType(self)->str:
        return self.__systemType

    @systemType.setter
    def systemType(self, systemType:str):
        self.__systemType = systemType


