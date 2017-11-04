import systemcheck
from systemcheck import exceptions
from .base_type import BasePlugin
from .system_type import SystemBasePlugin
from .manager import SysCheckPM
from systemcheck import checks, systems
import logging
import datetime
from collections import OrderedDict
from typing import Union
from pprint import pformat


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
        self.__errorMessage = None

    def __str(self):
        string = '<PluginResult> PluginName: {}, Rating: {}'.format(self.checkName, self.rating)
        return string

    def addResult(self, data:dict):
        """ Add a Result to the overall Result

         """
        self.__result.append(data)


    def addResultColumn(self, technical:str, description:str):
        """ Add a Column to the definition of the result table

        :param technical: The short name of the column.
        :param description: The description of the column.
        """
        self.__result_definition[technical]=description

    @property
    def checkName(self):
        """ Return the name of the plugin


        """

        return self.__plugin_name

    @checkName.setter
    def checkName(self, name):
        """ Set the name of the plugin


        """

        self.__plugin_name = name

    @property
    def errorMessage(self):
        return self.__errorMessage

    @errorMessage.setter
    def errorMessage(self, value):
        self.__errorMessage=value

    @property
    def logonInfo(self):
        """ Return the information used to log into a system


        """
        return self.__logoninfo

    @logonInfo.setter
    def logonInfo(self, logoninfo:dict):
        """ Return the information used to log into a system


        """

        self.__logoninfo=logoninfo

    @property
    def message(self):
        """ Additional Message with further messages

        This message gets displayed upon displaying the detail results.
        """
        return self.__message

    @message.setter
    def message(self, message):
        self.__message = message

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
    def result(self):
        """ Return a Result """
        return self.__result

    @result.setter
    def result(self, data:list):
        self.__result = data

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

class ActionBasePlugin(BasePlugin):
    """ The Foundation for all Action plugins

    """

    def __init__(self, *args, alchemyRoot=checks.models.Check, **kwargs):
        super().__init__()
        self.alchemyRoot=alchemyRoot

        self.parameterForm= None
        self.systemConnection = None
        self.logger = logging.getLogger("{}.{}".format(__name__, self.__class__.__name__))
        self.actionResult = ActionResult()

    def evaluateWhitelist(self):
        """ Certain Checks """
        raise NotImplemented

    def execute(self):
        """ The entry point for the actual plugin code"""
        raise NotImplemented

    def executeAction(self, systemObject, checkObject, *args, **kwargs):
        """ Function that gets executed to initiate the plugin execution.

        :param system_object: The sqlalchemy objet of the system that the plugin should be executed for


        """
        self.systemObject=systemObject
        self.checkObject=checkObject
        result = systemcheck.systems.ABAP.utils.get_connection(self.systemObject.logon_info())

        self.actionResult.logonInfo=self.systemObject.logon_info()
        self.actionResult.checkName=self.checkObject.name
        self.actionResult.systeminfo=self.systemInfo()

        if not result.fail:
            self.systemConnection = result.data
            self.execute()
        else:
            self.actionResult.rating='error'
            self.actionResult.errorMessage=result.message
            return self.actionResult

        self.systemConnection.close()
        self.rateOverallResult()
        return self.actionResult

    def initializeResult(self):
        """ Initialize the Result

        Add Columns to the Result Data Structure """



        raise systemcheck.exceptions.NotImplemented

    def rateIndividualResult(self, result:dict)->dict:
        """ Rate Individual Result

        A check can consist of multiple sets of paramters. Each set is validated individually.

        The direction of the comparison should match the direction in the display of the results. For example, if this
        parameter is set in the system:

        max_password_length = 10

        we expect that the minimum setting of that parameter is 8.

        then we have two options to compare the configured values:

        1: we want to verify that whatever we specified as expected is lower than what is configured to establish that
           the the configured value is larger:


        - we want to verify that the configured value is larger than the expected value.

            +------------------+----------------------+-----------------+
            | Value 1          | Operator             | Value 2         |
            +------------------+----------------------+-----------------+
            | EXPECTED (8)     | Lower or equal (>=)  | CONFIGURED (10) |
            | CONFIGURED (10)  | Higher or equal (>=) | CONFIGURED (10) |
            +------------------+----------------------+-----------------+

        Both representations are correct.

        """
        self.logger.debug('Rating individual result: %s', pformat(result))
        operator = result.get('OPERATOR')
        upper = result.get('UPPER')

        definitionList = list(self.actionResult.resultDefinition.keys())

        if definitionList.index('EXPECTED') > definitionList.index('CONFIGURED'):
            self.logger.debug('Configured occurs before Expected. That means, it is value1')
            value1 = result.get('CONFIGURED')
            value2 = result.get('EXPECTED')
        else:
            self.logger.debug('Configured occurs before Expected. That means, it is value1')
            value1 = result.get('EXPECTED')
            value2 = result.get('CONFIGURED')


        result['RATING']='pass'

        try:
            if self.operators.operation(value1=value1, operation_name=operator, value2=value2, value3=upper):
                result['RATING']='pass'
            else:
                result['RATING']='fail'
        except Exception as err:
                result['RATING']='error'
                self.actionResult.addResultColumn('ERROR', 'Error Message')
                result['ERROR'] = pformat(err)
        return result

    def rateOverallResult(self, error=False, errormessage=None):
        """ Rate Overall Result

        :param error: If the entire check has an error state, independent of the parameter sets, error should be set to True.
        :param errormessage: A message describing the error

        The rating of the individual results


        """

        self.actionResult.rating = 'pass'

        ratings = [item.get('RATING') for item in self.actionResult.result]

        if error or 'error' in ratings:
            self.actionResult.rating='error'
            self.actionResult.message='Unexpected Error during Execution. See detail results'
        else:
            if self.checkObject.failcriteria == checks.models.CheckFailCriteriaOptions.NO_RATING:
                self.actionResult.rating='info'
            elif self.checkObject.failcriteria ==  checks.models.CheckFailCriteriaOptions.FAIL_IF_ANY_FAILS:
                if 'fail' in ratings:
                    self.actionResult.rating='fail'
            elif self.checkObject.failcriteria == checks.models.CheckFailCriteriaOptions.FAIL_IF_ALL_FAIL:
                resultCount=len(self.actionResult.result)
                failCount=ratings.count('fail')
                if resultCount == failCount:
                    self.actionResult.rating='fail'


    def retrieveData(self):
        """ Retrieve the Data for the Check

        """
        raise NotImplemented

    def systemInfo(self):
        """ Return the system's Info string """
        raise systemcheck.exceptions.NotImplemented

    @property
    def systemConnection(self):
        return self.__systemConnection

    @systemConnection.setter
    def systemConnection(self, connection):
        self.__systemConnection=connection

    @property
    def parameterForm(self):
        return self.__parameterform

    @parameterForm.setter
    def parameterForm(self, form):

        self.__parameterform = form

    def validateRelevance(self):
        raise NotImplemented

class ActionAbapFoundation(ActionBasePlugin):
    """ ABAP Foundation Plugin
    Base class for all ABAP Plugins. """

    BAPI_MSG_TYPES = {'S':'Success', 'E':'Error', 'W':'Warning', 'I':'Info', 'A':'Abort'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.systemType='ABAP'

    def boolmapper(self, value:Union[bool, str], to_abap:bool=True):
        """ Map Pyton Boolean value to ABAP Flags

        :param value: The value that should be mapped
        :param to_abap: Returns the ABAP represenation of the boolean value
        """

        if to_abap:
            if isinstance(value, bool):
                if value:
                    return 'X'
                else:
                    return ' '
            else:
                return value
        else:
            if isinstance(value, str):
                if value=='X':
                    return True
                else:
                    return False
            else:
                return value


class ActionAbapCheck(ActionAbapFoundation):
    """ Generic ABAP Plugin

    This is the basic plugin that all plugins should be based on. If you want to code your own plugin, us this as the
    parent. The plugin reduces the effort of implementing your own code.

    Your main code needs to be executed in a function "execute":

    .. code:: python

        def execute(conn, sysInfo, *args, **kwargs):


    """


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.category='check'

    def systemInfo(self):

        info = '{}, Client {}'.format(self.systemObject.parent_node.sid, self.systemObject.client)
        return info

class ActionAbapSUIM(ActionAbapCheck):
    """ SUIM API Plugin
    The SUIM API exposes the report that make up transaction SUIM via RFC. The API consists of several function modules:

    - SUSR_SUIM_API_RSUSR002: Users by complex selection criteria
    - SUSR_SUIM_API_RSUSR008_009_NEW: Users with critical combinations of auhthorizations
    - SUSR_SUIM_API_RSUSR020: Profiles by complex selection criteria
    - SUSR_SUIM_API_RSUSR050_AUTH: Authorization Comparison
    - SUSR_SUIM_API_RSUSR050_PROF: Profile Comparison
    - SUSR_SUIM_API_RSUSR050_ROLE: Role Comparison
    - SUSR_SUIM_API_RSUSR050_USER: User Comparison
    - SUSR_SUIM_API_RSUSR070: Roles by complex search criteria
    - SUSR_SUIM_API_RSUSR100N: Change documents for users
    - SUSR_SUIM_API_RSUSR200: Users according to logon date and password change

    The API to SUIM is delivered in OSS Note 1930238. The following Notes are required as a minimum:
      - 1930238 - SUIM: API for RSUSR002
      - 2166771 - SUIM: SUSR_SUIM_API_RSUSR002 returns incorrect results
      - 1979313 - SUIM | RSUSR002: Search for executable transactions

    The selection options of the individual function modules are document in the corresponding plugin classes.
    However, they depend on the version of the ABAP system and potentially the notes that were implemented.

    What all SUIM function modules have in common is the standard of the naming convention of the parameters:

    - IT_*: Import Table - List of dictionaries
    - IV_*: Import Value - a normal value, pyrfc should handle those
    - ET_*: Export Table - List of dictionaries
    - EV_*: Export Value - a normal value, pyrfc should handle those

    Imported tables have to be specified as a list of dictionaries.

    """

    FM=None
    RETURNSTRUCTURE=None

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))


    def execute(self, connection, **kwargs):

        """ Verifies the system parameters according to config file.

        :param credentials: profile parameter to be checked.

        """


        paramkeys={item.upper() for item in self.actionResult['Parameters']}
        result=connection.fm_interface(self.FM)
        if result.fail:
            self.actionResult.rating = 'error'

        self.actionResult.rating='info'
        fm_interface = result.data

        fmkeys={item['PARAMETER'] for item in fm_interface['PARAMS']}

        relevantParams=paramkeys & fmkeys

        fmcallparams={}

        for parameter in relevantParams:

            param_value = self.actionResult['Parameters'].get(parameter, raw=True)
            if param_value=='':
                param_value = ' '

            fmcallparams[parameter]=param_value

        self.logger.debug('parameters for SUIM API Call: %s', pformat(fmcallparams))

        result = connection.call_fm(self.FM, **fmcallparams)

        if result.fail:
            raise SystemError

        fm_data=result.data

        message = 'The plugin showed some additional results: \n'

        #Analyzing the return structure
        return_data = fm_data.get('RETURN')
        if len(return_data) >0:
            msg_types = [item['TYPE'] for item in return_data]
            for rec in return_data:
                message += '{}: {}\n'.format(self.BAPI_MSG_TYPES[rec.get('TYPE')], rec['MESSAGE'])

            self.actionResult.message = message
            if 'E' in msg_types or 'A' in msg_types:
                self.actionResult.rating = 'error'
            elif 'W' in msg_types:
                self.actionResult.rating = 'warning'

        self.actionResult.result=fm_data.get(self.RETURNSTRUCTURE)


        if len(self.actionResult.result)>0:
            self.actionResult.rating = 'fail'
        else:
            self.actionResult.rating = 'pass'

        return Result(data=self.actionResult)

    def analyzeResults(self):
        """ Analyze the Results and apply White Lists"""
        pass


categories = {'ActionAbapSUIM':ActionAbapSUIM,
              'ActionAbapCheck': ActionAbapCheck,
              'system':SystemBasePlugin}
