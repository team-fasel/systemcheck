import operator
from yapsy import IPlugin
from systemcheck.config import CONFIG
import datetime
import logging
from collections import OrderedDict
from systemcheck.utils import Result, Fail

class PluginResult:
    """ Result of a check plugin


    All results of check plugins are represented through this object. Values should only be assigned through properties.

    resultDefinition: The result is represented by a list of dictionaries. The keys of the dictionaries are usually
    of a technical nature, short and all capital letters.



    """

    def __init__(self):

        self._result = []
        self.timestamp = datetime.datetime.now()
        self._logoninfo = {}
        self._rating = 'pass'
        self._message = False
        self._result_definition=OrderedDict()
        self._plugin_name = None
        self._systeminfo = None

    def __str(self):
        string = '<PluginResult> PluginName: {}, Rating: {}'.format(self.plugin_name, self.rating)
        return string


    @property
    def resultDefinition(self):
        """ Povide the definition of the Results Table


        All results will get returned as table. The table definition consists of an OrderedDict as it """
        return self._result_definition

    @resultDefinition.setter
    def resultDefinition(self, definition:OrderedDict):
        """ Define the Table that contains the results

        """
        self._tableDefinition = definition


    def addResultColumn(self, technical:str, description:str):
        """ Add a Column to the definition of the result table

        :param technical: The short name of the column.
        :param description: The description of the column.
        """
        self._result_definition[technical]=description

    @property
    def result(self):
        """ Return a Result """
        return self._result

    @result.setter
    def result(self, data:list):
        self._result = data

    def add_result(self, data:dict):
        """ Add a Result to the overall Result

         """
        self._result.append(data)

    @property
    def logoninfo(self):
        """ Return the information used to log into a system


        """

        return self._logoninfo

    @logoninfo.setter
    def logoninfo(self, logoninfo:dict):
        """ Return the information used to log into a system


        """

        self._logoninfo=logoninfo

    @property
    def rating(self)->str:
        """ Return the rating of the Result

        The following ratings are possible:

           - pass:    The check passed
           - fail:    The check failed
           - error:   There was an error during the execution of the plugin
           - warning: The result finished with a Warning
        """

    @rating.setter
    def rating(self, value:str):
        """ Set the Overal rating of the result """

        self._rating = value

    @property
    def plugin_name(self):
        """ Return the name of the plugin


        """

        return self._plugin_name

    @plugin_name.setter
    def plugin_name(self, name):
        """ Set the name of the plugin


        """

        self._plugin_name = name

    @property
    def systeminfo(self):
        """Set the System Info


        The system info is used to represent the checked system in a user interface for example. For ABAP systems, a
        system info should be set to SID, Client <client> """
        return self._systeminfo

    @systeminfo.setter
    def systeminfo(self, systeminfo):
        """ Setter for the systeminfo

        """
        self._systeminfo = systeminfo

    @property
    def message(self):
        """ Additional Message with further messages

        This message gets displayed upon displaying the detail results.
        """
        return self._message

    @message.setter
    def message(self, message):
        self._message = message

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
        self.pluginResult = PluginResult()
        self.logger = logging.getLogger("{}.{}".format(__name__, self.__class__.__name__))


class GenericCheckPlugin(BasePlugin):
    """ The Foundation for all check plugins

    """


    def set_plugin_config(self, Core:dict,
                          Documentation:dict,
                          Parameters:dict,
                          RuntimeParameters:dict,
#                          Path:dict
                          ):
        """ Set Plugin Config

        The yapsy plugin manager executed this method to configure the plugin based on the configuration files


        :param Core: The 'Core' section of PluginInfo.details
        :param Documentation: The 'Documentation section of PluginInfo.details
        :param Parameters: The standard parameters as defined in the plugin's info file
        :param RuntimeParameters: The updated parameters including custom config if it exists
        :param Path: The path as available in PluginInfo.path"""

        self.pluginConfig = dict(Core = Core, Documentation = Documentation, Parameters=Parameters, RuntimeParameters=RuntimeParameters, Path = None)
        self.logger = logging.getLogger('systemcheck.plugins.CheckPlugin.{}.{}'.format(self.TYPE, self.pluginConfig['Core']['Name']))

    def system_connection(self, **logoninfo):
        """ Get a connection to the system """
        raise NotImplemented

    def execute(self, connection):
        """ The entry point for the actual plugin code"""

    def execute_plugin(self, system_object, config_object, *args, **kwargs):
        """ Function that gets executed to initiate the plugin execution.

        :param system_object: The sqlalchemy objet of the system that the plugin should be executed for


        """

        self.logger.debug('Starting Execution {}')
        self._system_object = system_object

        result = self.system_connection()
        if not result.fail:
            connection = result.data
        else:
            raise SystemError(result.message)

        plugin_result = self.execute(connection)
        return plugin_result

