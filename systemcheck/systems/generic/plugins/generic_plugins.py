import operator
from yapsy import IPlugin
from systemcheck.config import CONFIG
import datetime
import logging
from collections import OrderedDict


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
        self.plugin_result = dict()
        self.plugin_result['tabledefinition'] = OrderedDict()
        self.logger = logging.getLogger("{}.{}".format(__name__, self.__class__.__name__))

    def set_plugin_config(self, Core:dict,
                          Documentation:dict,
                          Parameters:dict,
                          RuntimeParameters:dict,
                          Path:dict):
        """ Set Plugin Config

        The yapsy plugin manager executed this method to configure the plugin based on the configuration files


        :param Core: The 'Core' section of PluginInfo.details
        :param Documentation: The 'Documentation section of PluginInfo.details
        :param Parameters: The standard parameters as defined in the plugin's info file
        :param RuntimeParameters: The updated parameters including custom config if it exists
        :param Path: The path as available in PluginInfo.path"""

        self.pluginConfig = dict(Core = Core, Documentation = Documentation, Parameters=Parameters, RuntimeParameters=RuntimeParameters, Path = Path)
        self.logger = logging.getLogger('systemcheck.plugins.CheckPlugin.{}.{}'.format(self.TYPE, self.pluginConfig['Core']['Name']))

    def system_connection(self, **logoninfo):
        """ Get a connection to the system """
        raise NotImplemented

