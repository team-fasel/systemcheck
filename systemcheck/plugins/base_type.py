import operator
from yapsy import IPlugin
from yapsy.PluginManager import PluginManagerSingleton
from typing import Any

#from systemcheck.utils import get_or_create
from systemcheck.session import SESSION
from systemcheck.config import CONFIG
import systemcheck
from systemcheck.models.meta import Operators
from systemcheck.utils import get_absolute_systemcheck_path
import re


class BasePlugin(IPlugin.IPlugin):
    """ The Base Plugin

    All Plugins are children of this plugin. A Hierarchy is required to enable effective filtering in the yapsy
    plugin manager.


    """


    INTERVALS = {'D':'Days', 'H': 'Hours', 'M':'Minutes', 'S':'Seconds', 'W':'Weeks', 'Y':'Years'}

    TYPE = None

    def __init__(self, *args, **kwargs):
        """ Initialization for Base Plugin


        :param alchemyRoot: The SQLAlchemy Object that defines the root node
        :param alchemyObjects: A list of Objects that are relevant for the particular plugin
        """
        super().__init__()
        self.operators = Operators()
        self.systemType = None
        self.category = None


    @property
    def alchemyObjects(self):
        return self.__alchemyObjects

    @alchemyObjects.setter
    def alchemyObjects(self, alchemyObjects:list):
        if len(alchemyObjects)==0:
            self.__alchemyObjects = []
        else:
            self.__alchemyObjects = alchemyObjects

    @property
    def alchemyRoot(self):
        return self.__alchemyRoot

    @alchemyRoot.setter
    def alchemyRoot(self, alchemyRoot:Any):
        self.__alchemyRoot=alchemyRoot

    @property
    def rootNode(self):
        if self.__alchemyRoot:
            rootnode = systemcheck.utils.get_or_create(SESSION, self.__alchemyRoot, parent_id=None, name='RootNode')
            return rootnode
        return None

    @property
    def category(self):
        return self.__category

    @category.setter
    def category(self, category:str):
        self.__category = category

    @property
    def systemType(self):
        return self.__systemtype

    @systemType.setter
    def systemType(self, systemtype:str):
        self.__systemtype = systemtype