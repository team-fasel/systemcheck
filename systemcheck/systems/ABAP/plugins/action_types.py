import ast
from collections import OrderedDict
import logging
from pprint import pformat

from systemcheck.systems.generic import actions as generic_actions
from systemcheck.systems.ABAP import utils as abaputils
from systemcheck.utils import Result, Fail
from systemcheck.config import CONFIG


class CheckAbapFoundationAction(generic_actions.GenericActionPlugin):
    """ ABAP Foundation Plugin
    Base class for all ABAP Plugins. """

    TYPE='ABAP'

    BAPI_MSG_TYPES = {'S':'Success', 'E':'Error', 'W':'Warning', 'I':'Info', 'A':'Abort'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def system_connection(self):
        """ Get RFC System Connection
        """
        logon_info = self._system_object.logon_info()
        result = abaputils.get_connection(logon_info)

        if not result.fail:
            self.conn = result.data

        return result


class CheckAbapAction(CheckAbapFoundationAction):
    """ Generic ABAP Plugin

    This is the basic plugin that all plugins should be based on. If you want to code your own plugin, us this as the
    parent. The plugin reduces the effort of implementing your own code.

    Your main code needs to be executed in a function "execute":

    .. code:: python

        def execute(conn, sysInfo, *args, **kwargs):


    """


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class CheckAbapSUIMAction(CheckAbapFoundationAction):
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
