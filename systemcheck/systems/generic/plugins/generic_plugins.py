import operator
from yapsy import IPlugin
from systemcheck import CONFIG
import logging
from collections import defaultdict

class PluginResult:
    """ The Common API for any plugin result """

    def __init__(self):

        self._plugin_data=dict()

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

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("{}.{}".format(__name__, self.__class__.__name__))


    def system_connection(self, **logoninfo):
        """ Get a connection to the system """

        raise NotImplemented

