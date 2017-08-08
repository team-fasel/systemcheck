import operator
from yapsy import IPlugin
import systemcheck.session
import datetime
import logging
from collections import OrderedDict
from systemcheck.utils import Result, Fail

class ActionResult:
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

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.actionResult = ActionResult()
        self.logger = logging.getLogger("{}.{}".format(__name__, self.__class__.__name__))


class GenericActionPlugin(BasePlugin):
    """ The Foundation for all Action plugins

    """

    def __init__(self, *args, parameters=None, **kwargs):
        super().__init__()

        self.parameters = parameters
        self.alchemyObjects=[]


    def set_plugin_config(self):
        pass

    def ressolve_parameters(self):
        pass

    def system_connection(self, **logoninfo):
        """ Get a connection to the system """
        raise NotImplemented

    def execute(self, connection):
        """ The entry point for the actual plugin code"""

    def execute_action(self, system_object, parameters, *args, **kwargs):
        """ Function that gets executed to initiate the plugin execution.

        :param system_object: The sqlalchemy objet of the system that the plugin should be executed for


        """

        self.logger.debug('Starting Execution {}')
        self._system_object = system_object
        self.init_db()

        result = self.system_connection()
        if not result.fail:
            connection = result.data
        else:
            raise SystemError(result.message)

        plugin_result = self.execute(connection)
        return plugin_result

    def init_db(self):

        for object in self.alchemyObjects:
            object.__table__.create(systemcheck.session.engine)

