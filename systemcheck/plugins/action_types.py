import operator
from yapsy import IPlugin
import systemcheck.session
import datetime
import logging
from collections import OrderedDict
from systemcheck.utils import Result, Fail
from systemcheck.plugins import BasePlugin

class ActionResult:
    """ Result of a check plugin


    All results of check plugins are represented through this object. Values should only be assigned through properties.

    resultDefinition: The result is represented by a list of dictionaries. The keys of the dictionaries are usually
    of a technical nature, short and all capital letters.



    """

    def __init__(self):

        self.__result = []
        self.timestamp = datetime.datetime.now()
        self.__logoninfo = {}
        self.__rating = 'pass'
        self.__message = False
        self.__result_definition=OrderedDict()
        self.__plugin_name = None
        self.__systeminfo = None

    def __str(self):
        string = '<PluginResult> PluginName: {}, Rating: {}'.format(self.check_name, self.rating)
        return string


    @property
    def resultDefinition(self):
        """ Povide the definition of the Results Table


        All results will get returned as table. The table definition consists of an OrderedDict as it """
        return self.__result_definition

    @resultDefinition.setter
    def resultDefinition(self, definition:OrderedDict):
        """ Define the Table that contains the results

        """
        self.__result_definition = definition


    def addResultColumn(self, technical:str, description:str):
        """ Add a Column to the definition of the result table

        :param technical: The short name of the column.
        :param description: The description of the column.
        """
        self.__result_definition[technical]=description

    @property
    def result(self):
        """ Return a Result """
        return self.__result

    @result.setter
    def result(self, data:list):
        self.__result = data

    def add_result(self, data:dict):
        """ Add a Result to the overall Result

         """
        self.__result.append(data)

    @property
    def logoninfo(self):
        """ Return the information used to log into a system


        """

        return self.__logoninfo

    @logoninfo.setter
    def logoninfo(self, logoninfo:dict):
        """ Return the information used to log into a system


        """

        self.__logoninfo=logoninfo

    @property
    def rating(self)->str:
        """ Return the rating of the Result

        The following ratings are possible:

           - pass:    The check passed
           - fail:    The check failed
           - error:   There was an error during the execution of the plugin
           - info:    Just informational
           - warning: The result finished with a Warning
        """

        return self.__rating

    @rating.setter
    def rating(self, value:str):
        """ Set the Overal rating of the result """

        self.__rating = value

    @property
    def check_name(self):
        """ Return the name of the plugin


        """

        return self.__plugin_name

    @check_name.setter
    def check_name(self, name):
        """ Set the name of the plugin


        """

        self.__plugin_name = name

    @property
    def systeminfo(self):
        """Set the System Info


        The system info is used to represent the checked system in a user interface for example. For ABAP systems, a
        system info should be set to SID, Client <client> """
        return self.__systeminfo

    @systeminfo.setter
    def systeminfo(self, systeminfo):
        """ Setter for the systeminfo

        """
        self.__systeminfo = systeminfo

    @property
    def message(self):
        """ Additional Message with further messages

        This message gets displayed upon displaying the detail results.
        """
        return self.__message

    @message.setter
    def message(self, message):
        self.__message = message


class ActionBasePlugin(BasePlugin):
    """ The Foundation for all Action plugins

    """

    def __init__(self, *args, alchemyRoot=systemcheck.checks.models.Check, parameters:list=None, **kwargs):
        super().__init__(alchemyRoot)
        self.actionResult = ActionResult()
        self.logger = logging.getLogger("{}.{}".format(__name__, self.__class__.__name__))
        self.__parameters = parameters

        self.setAlchemyRoot(systemcheck.checks.models.Check)

    def set_plugin_config(self):
        pass

    def ressolve_parameters(self):
        pass

    def system_connection(self, **logoninfo):
        """ Get a connection to the system """
        raise NotImplemented

    def execute(self, connection):
        """ The entry point for the actual plugin code"""
        pass

    def execute_action(self, system_object, parameters, *args, **kwargs):
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

