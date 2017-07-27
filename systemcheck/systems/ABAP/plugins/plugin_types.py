import ast
from collections import OrderedDict
import logging
from pprint import pformat

import systemcheck.systems.generic.plugins
from systemcheck.systems.ABAP import utils as abaputils
from systemcheck.utils import Result, Fail
from systemcheck.config import CONFIG


class CheckAbapFoundationPlugin(systemcheck.systems.generic.plugins.GenericCheckPlugin):
    """ ABAP Foundation Plugin
    Base class for all ABAP Plugins. """

    TYPE='ABAP'

    BAPI_MSG_TYPES = {'S':'Success', 'E':'Error', 'W':'Warning', 'I':'Info', 'A':'Abort'}

    def __init__(self):
        super().__init__()


    def system_connection(self):
        """ Get RFC System Connection
        """
        logon_info = self._system_object.logon_info()
        result = abaputils.get_connection(logon_info)

        if not result.fail:
            self.conn = result.data

        return result


class CheckAbapPlugin(CheckAbapFoundationPlugin):
    """ Generic ABAP Plugin

    This is the basic plugin that all plugins should be based on. If you want to code your own plugin, us this as the
    parent. The plugin reduces the effort of implementing your own code.

    Your main code needs to be executed in a function "execute":

    .. code:: python

        def execute(conn, sysInfo, *args, **kwargs):


    """


    def __init__(self):
        super().__init__()


class CheckAbapCountTableEntries(CheckAbapFoundationPlugin):
    """ A SELECT COUNT(*) for ABAP Tables


    """

    def execute(self, connection, **kwargs):

        self.pluginResult.resultDefinition = OrderedDict(RATING='Rating', WHERE_CLAUSE='Where Clause',
                                                         OPERATOR='Operator', TABLE='Table',
                                                         EXPECTED='Expected', CONFIGURED='Configured')

        self.connection=connection

        for item, value in self.pluginConfig['RuntimeParameters'].items():
            config=self.pluginConfig['RuntimeParameters'].get(item, raw=True)
            data=ast.literal_eval(config)

            record=dict(RATING='pass',
                        WHERE_CLAUSE=data['WHERE_CLAUSE'],
                        TABLE=data['TABLE'],
                        EXPECTED=int(data['EXPECTED']),
                        OPERATOR = data.get('OPERATOR'))

            if not record['OPERATOR']:
                record['OPERATOR'] = 'EQ'

            result=self.connection.download_table(record['TABLE'],
                                                  where_clause=record['WHERE_CLAUSE'],
                                                  tab_fields=data['COLUMNS'])
            if not result.fail:
                downloaded_data=result.data['data']
                record['CONFIGURED']=str(len(downloaded_data))
            else:
                record['CONFIGURED']=result.fail
                self.pluginResult.add_result(record)
                self.pluginResult.rating='error'
                return Result(self.pluginResult)

            success=self.OPERATIONS[data['OPERATOR']](int(record['EXPECTED']), int(record['CONFIGURED']))

            if not success:
                record['RATING']='fail'
                self.pluginResult.rating='fail'

            self.pluginResult.add_result(record)

        return Result(data=self.pluginResult)


class CheckAbapSUIMPlugin(CheckAbapFoundationPlugin):
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


        paramkeys={item.upper() for item in self.pluginConfig['Parameters']}
        result=connection.fm_interface(self.FM)
        if result.fail:
            self.pluginResult.rating = 'error'

        self.pluginResult.rating='info'
        fm_interface = result.data

        fmkeys={item['PARAMETER'] for item in fm_interface['PARAMS']}

        relevantParams=paramkeys & fmkeys

        fmcallparams={}

        for parameter in relevantParams:

            param_value = self.pluginConfig['Parameters'].get(parameter, raw=True)
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

            self.pluginResult.message = message
            if 'E' in msg_types or 'A' in msg_types:
                self.pluginResult.rating = 'error'
            elif 'W' in msg_types:
                self.pluginResult.rating = 'warning'

        self.pluginResult.result=fm_data.get(self.RETURNSTRUCTURE)


        if len(self.pluginResult.result)>0:
            self.pluginResult.rating = 'fail'
        else:
            self.pluginResult.rating = 'pass'

        return Result(data=self.pluginResult)

    def analyzeResults(self):
        """ Analyze the Results and apply White Lists"""
        pass



class CheckAbapRsusr002Plugin(CheckAbapSUIMPlugin):
    """RSUSR002: Users by Complex Selection Criteria

    This plugin type retrieves user accounts similar to using SUIM with complex selection criteria. It's calling
    function module SUSR_SUIM_API_RSUSR002 which needs to be available in the system. The API to SUIM is delivered in
    OSS Note 1930238. The following Notes are required:
      - 1930238 - SUIM: API for RSUSR002
      - 2166771 - SUIM: SUSR_SUIM_API_RSUSR002 returns incorrect results
      - 1979313 - SUIM | RSUSR002: Search for executable transactions

    The selection options below depend on the version of the system. The list was retrieved using SE37 in a
    SAP NetWeaver 7.50 system

    Import:
        Standard Selection:
            IT_USER       User list
            IT_GROUP      Group for Authorization
            IT_UGROUP     User group general

        Selection Criteria:
            Documentation:
            Logon Data:
                IT_UALIAS     Selection options for Alias
                IT_UTYPE      Selection options for user type
                IT_SECPOL     Selection options for security policy
                IT_SNC        Selection options for SNC
                Selection by Locks:
                    IV_USER_LOCK  Lock status Y=locked, N=unlocked, Space = irrelevant
                    IV_PWD_LOCK   Lock status Y=locked, N=unlocked, Space = irrelevant
                    IV_LOCK       All Users with administrator- or password locks: TRUE (='X') und FALSE (=' ')
                    IV_UNLOCK     Only users without locks: TRUE (='X') und FALSE (=' ')
                IV_FDATE      Validity date from
                IV_TDATE      Validity date until
                IT_LIC_TYPE   Selection options for license types
                IT_ACCNT      Selection options for Account-Id
                IT_KOSTL      Selection options for cost center
            Default Values:
                IT_STCOD      Selection options for start menu
                IT_LANGU      Selection options for language
                IV_DCPFM      Decimal format
                IV_DATFM      Date format
                IV_TIMEFM     Time format (12-/24-Hour display)
                IT_SPLD       Output Device
                IV_TZONE      Time zone
                IV_CATTK      CATT Check indicator (TRUE (='X') und FALSE (=' '))
                IT_PARID      Selection options for Set-/Get-Paramter-Id
            Roles Profile:
                IV_TCODE      Transaktionscode
                IV_START_TX   Only executable transactions
                IT_UREF       Selection options for reference user
                IT_ACTGRPS    Selection options for role
                IT_PROF1      Selection options for profile
                IV_PROF2      Authorization profile in user master maintenance
                IV_PROF3      Authorization profile in user master maintenance
            Authorizations:
                Selection by Field Name:
                    IV_CONV1      Always convert Values (TRUE (='X') und FALSE (=' '))
                    IV_AUTH_FLD   Authorization field name
                Selection by Authorizations:
                    IV_AUTH_VAL   Authorization value
                    IT_OBJCT      Selection options for authorization objects
                Selection by Values:
                    IT_AUTH       Selection options for authorizations
                    IV_CONV       Data element zur Domäne BOOLE: TRUE (='X') und FALSE (=' ')
                    IT_VALUES     Transfer structure for selection by authorization values

    """

    FM = 'SUSR_SUIM_API_RSUSR002'
    RETURNSTRUCTURE='ET_USERS'

    def __init__(self):
        super().__init__()

        report_columns = CONFIG['systemtype_ABAP']['suim.reportcolumns.rsusr002'].split(',')
        header_descriptions = dict(CHECK = 'Checkbox', BNAME = 'Username', USERALIAS='User Alias',
                                                         CLASS = 'User Group', LOCKICON = 'Lockicon',
                                                         LOCKREASON = 'Lock Reason', GLTGV = 'Valid From',
                                                         GLTGB = 'Valid Until', USTYP = 'User Type',
                                                         REFUSER = 'Reference User', ACCNT = 'ACCNT',
                                                         KOSTL = 'Cost Center', NAME_TEXT = 'Name',
                                                         DEPARTMENT = 'Department', FUNCTION = 'Function',
                                                         BUILDING_C = 'Building', FLOOR_C = 'Floor', ROOMNUM_C = 'Room',
                                                         TEL_NUMBER = 'Phone Number', TEL_EXTENS = 'Phone Extension',
                                                         NAME1 = 'Name 1', NAME2 = 'Name 2', NAME3 = 'Name 3',
                                                         NAME4 = 'Name 4', POST_CODE1 = 'Zip Code', CITY1 = 'City',
                                                         STREET = 'Street', COUNTRY = 'Country', TZONE = 'Time Zone',
                                                         SECURITY_POLICY = 'Security Policy', EMAIL = 'eMail')

        for column in report_columns:
            self.pluginResult.addResultColumn(column, header_descriptions.get(column))

class CheckAbapRsusr020Plugin(CheckAbapSUIMPlugin):
    """SUSR_SUIM_API_RSUSR020: Profiles by complex selection criteria

    The selection options below depend on the version of the system. The return structure ET_PROFS has the following
    headers: PROFN, AKTPS, PTEXT, MODDA, MODTI, MODBE, TYP, LANGU

    Import:
        Selection Criteria:
            IT_PROF      Selection options for profiles
            IT_PTEXT     Transfer structure for selection options for profile text
            IV_ACTIVE    Active profiles (TRUE (='X') und FALSE (=' '))
            IV_NO_ACT    Maintenance Version
        Additional selection criteria for profiles:
            IV_C_PROF    Composite Profile (TRUE (='X') und FALSE (=' '))
            IV_S_PROF    Single Profile (TRUE (='X') und FALSE (=' '))
            IV_G_PROF    Generated Profile (TRUE (='X') und FALSE (=' '))
            IV_MODBE     Mofidied by
            IV_VONDAT    Last change since
            IV_BISDAT    Last change up to
        Selection by contained profiles:
            IT_I_PROFS   Selection option for profiles
        Selection by authorizations:
            IT_OBJCT     Selection option for authorization objects
            IT_AUTH
        Selection by authorization values:
            IT_VALUES    Selection option for authorization values
        Selection by role:
            IT_ACTGRPS
    Export:
        ET_PROFS  Profiles
        RETURN    Return structure
    """

    FM = 'SUSR_SUIM_API_RSUSR020'
    RETURNSTRUCTURE='ET_PROFS'

    def __init__(self):
        super().__init__()

        report_columns = CONFIG['systemtype_ABAP']['suim.reportcolumns.rsusr020'].split(',')
        header_descriptions = dict(PROFN='Profile Name', AKTPS='Act./Maint. Version',
                                                         PTEXT='Profile Text', MODDA='Modification Date',
                                                         MODTI='Modification Time', MODBE='Last Change By',
                                                         TYP='Profile Type (Comp/Single)', LANGU='Language')


        for column in report_columns:
            self.pluginResult.addResultColumn(column, header_descriptions.get(column))

class CheckAbapRsusr200Plugin(CheckAbapSUIMPlugin):
    """SUSR_SUIM_API_RSUSR200: Users by


    Import:
        Selection Criteria:
            IT_PROF      Selection options for profiles
            IT_PTEXT     Transfer structure for selection options for profile text
            IV_ACTIVE    Active profiles (TRUE (='X') und FALSE (=' '))
            IV_NO_ACT    Maintenance Version
        Additional selection criteria for profiles:
            IV_C_PROF    Composite Profile (TRUE (='X') und FALSE (=' '))
            IV_S_PROF    Single Profile (TRUE (='X') und FALSE (=' '))
            IV_G_PROF    Generated Profile (TRUE (='X') und FALSE (=' '))
            IV_MODBE     Mofidied by
            IV_VONDAT    Last change since
            IV_BISDAT    Last change up to
        Selection by contained profiles:
            IT_I_PROFS   Selection option for profiles
        Selection by authorizations:
            IT_OBJCT     Selection option for authorization objects
            IT_AUTH
        Selection by authorization values:
            IT_VALUES    Selection option for authorization values
        Selection by role:
            IT_ACTGRPS
    Export:
        ET_USERS  Profiles
        RETURN    Return structure
    """

    FM = 'SUSR_SUIM_API_RSUSR200'
    RETURNSTRUCTURE='ET_USERS'

    def __init__(self):
        super().__init__()

        report_columns = CONFIG['systemtype_ABAP']['suim.reportcolumns.rsusr020'].split(',')

        header_descriptions = dict(BNAME = 'Username',
                                   CLASS = 'User Group',
                                   USTYP = 'User Type',
                                   ANAME = 'Created By',
                                   ERDAT = 'Creation Date',
                                   GLTGV = 'Valid from',
                                   GLTGB = 'Valid until',
                                   TRDAT1 = 'Date of Last Logon',
                                   LTIME = 'Last Logon Time',
                                   ICON_STATE = 'Password Status',
                                   BCDA1 = 'Date of Last Password Change',
                                   ICON_LOCKED = 'User Lock Status',
                                   LOCK_REASON = 'Reason for User Lock',
                                   LOCNT = 'Number of failed logon attempts',
                                   CODVN = 'Code Version of Password Hash',
                                   USR02FLAG = 'User Lock Status',
                                   TRDAT = 'Last Logon Date',
                                   PWDLOCKDATE = 'Setting of Password Lock',
                                   RELEASE = 'SAP Release',
                                   SECURITY_POLICY = 'Security Policy Name')


        for column in report_columns:
            self.pluginResult.addResultColumn(column, header_descriptions.get(column))

class CheckAbapRsusr070Plugin(CheckAbapSUIMPlugin):
    """SUSR_SUIM_API_RSUSR070: Roles by complex selection criteria

    The selection options below depend on the version of the system. The return structure ET_PROFS has the following
    headers: PROFN, AKTPS, PTEXT, MODDA, MODTI, MODBE, TYP, LANGU

         IT_ACTGRPS
         IT_TEXT1
         IV_LANGU
         IV_BES_LNG
         IV_S_ROLES
         IV_C_ROLES
         IV_OBSOLETE
         IV_ALL_USER
         IV__USER
         IT_USER
         IV_ALVLISTE
         IV_NO_USER
         IT_TCODE1
         IV_TCODE2
         IV_TCODE3
         IV_TCODE4
         IV_TCODE5
         IT_S_OBJNM1
         IV_S_OBJNM2
         IV_S_OBJNM3
         IV_S_OBJNM4
         IV_S_OBJNM5
         IT_PROF
         IT_OBJCT
         IT_VALUES
         IV_AUTH_FLD
         LV_AUTH_VAL
         LV_RESPO
         LV_CHANGER
         LV_CHG_SDAT
         LV_CHG_BDAT

    """

    #TODO: Need to adapt the normal SUIM interface for RSUSR070

    FM = 'SUSR_SUIM_API_RSUSR070'
    RETURNSTRUCTURE='ET_PROFS'

    def __init__(self):
        super().__init__()

        report_roles_columns = CONFIG['systemtype_ABAP']['suim.reportcolumns.rsusr070_roles'].split(',')
        report_users_columns = CONFIG['systemtype_ABAP']['suim.reportcolumns.rsusr070_users'].split(',')
        header_roles_descriptions = dict(AGR_NAME='Role Name',
                                        AGR_TYPE='Role Type',
                                        ATEXT = 'Role Description',
                                        LANGU = 'Logon Language')

        header_users_descriptions = dict(UNAME = 'User Name',
                                         NAME_TEXT = 'Full Name of User',
                                         AGR_NAME = 'Role Nane',
                                         AGR_TYPE = 'Role Type',
                                         ASSIGN_TYPE = 'ASSIGN_TYPE',
                                         ASSIGN_REF = 'ASSIGN_REF',
                                         FROM_DAT = 'Valid From',
                                         TO_DAT = 'Valid Until',
                                         AGR_TEXT = 'Role Description')



        for column in report_roles_columns:
            self.pluginResult.addResultColumn(column, header_roles_descriptions.get(column))

        for column in report_users_columns:
            self.pluginResult.addResultColumn(column, header_users_descriptions.get(column))


