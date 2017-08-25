import operator
from yapsy import IPlugin
from typing import Any
from systemcheck.utils import get_or_create
from systemcheck.session import SESSION

class BasePlugin(IPlugin.IPlugin):
    """ The Base Plugin

    All Plugins are children of this plugin. A Hierarchy is required to enable effective filtering in the yapsy
    plugin manager.


    """
    OPERATORS = {'EQ':'=', 'NE':'!=', 'GT':'>', 'LT':'<', 'LE':'<=', 'GE':'>=',
                 '=':'=', '!=':'!=','>':'>','<':'<','>=':'>=','<=':'<='}   # Adding the actual symbols for more flexibility

    OPERATIONS = {'EQ': operator.eq,
                  'NE': operator.ne,
                  'GT': operator.gt,
                  'LT': operator.lt,
                  'GE': operator.ge,
                  'LE': operator.le,
                  '=': operator.eq,
                  '!=': operator.ne,
                  '>': operator.gt,
                  '<': operator.lt,
                  '>=': operator.ge,
                  '<=': operator.le}

    INTERVALS = {'D':'Days', 'H': 'Hours', 'M':'Minutes', 'S':'Seconds', 'W':'Weeks', 'Y':'Years'}

    TYPE = None

    def __init__(self, *args, alchemyObjects:list=None, alchemyRoot:Any=None,  **kwargs):
        """ Initialization for Base Plugin


        :param alchemyRoot: The SQLAlchemy Object that defines the root node
        :param alchemyObjects: A list of Objects that are relevant for the particular plugin
        """


        super().__init__()

        if alchemyObjects is None:
            self.__alchemyObjects = []

        else:
            self.__alchemyObjects = alchemyObjects

        self.__alchemyRoot = alchemyRoot


    def alchemyObjects(self):
        return self.__alchemyObjects

    def alchemyRoot(self):
        return self.__alchemyRoot

    def rootNode(self):
        if self.__alchemyRoot:
            rootnode = get_or_create(SESSION, self.__alchemyRoot, parent_id=None, name='RootNode')
            return rootnode
        return None

    def setAlchemyObjects(self, alchemyObjects:list):
        self.__alchemyObjects = alchemyObjects

    def setAlchemyRoot(self, alchemyRoot:Any):
        self.__alchemyRoot=alchemyRoot

