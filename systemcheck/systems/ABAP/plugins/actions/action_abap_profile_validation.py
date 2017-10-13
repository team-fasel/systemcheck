import systemcheck
from systemcheck.systems import ABAP
from systemcheck.checks.models import Check
from systemcheck.utils import Result, Fail

from systemcheck.checks.models.checks import Check
from systemcheck.models.meta import Base, ChoiceType, Column, ForeignKey, Integer, QtModelMixin, String, qtRelationship, \
    relationship, RichString
from systemcheck.systems import ABAP
from pprint import pformat

print('importing module {}'.format(__name__))

class ProfileParameterReference:

    def __init__(self, parameters):

        self.__parameters = parameters

    def getValue(self, parameter, profile_type=None):

        result=[]

        if profile_type:
            params = self.__parameters[profile_type]

            for data in params:
                if data.get('PARNAME')==parameter:
                    result.append(data)
        else:
            for type, parameters in self.__parameters.items():
                for data in parameters:
                    if data.get('PARNAME')==parameter:
                        result.append(data)
        return result

class ActionAbapProfileValidation(systemcheck.plugins.ActionAbapCheck):
    """ Validate Runtime Parameters


    """

    def __init__(self):
        super().__init__()
        self.alchemyObjects = [ABAP.models.ActionAbapProfileValidation,
                               ABAP.models.ActionAbapProfileValidation__params,
#TODO: Reenable when developing a restriction approach
#                               ABAP.models.ActionAbapProfileValidation__params__restrictions,
#                               ABAP.models.ActionAbapProfileValidation__restrictions,
                               Check,
                               ABAP.models.ActionAbapFolder]

    def initializeResult(self):

        self.actionResult.addResultColumn('PARAMETERSET', 'Parameter Set Name')
        self.actionResult.addResultColumn('RATING', 'Rating')
        self.actionResult.addResultColumn('PROFILETYPE', 'Profile Type')
        self.actionResult.addResultColumn('PROFILENAME', 'Profile Name')
        self.actionResult.addResultColumn('PARAMETER', 'Instance')
        self.actionResult.addResultColumn('OPERATOR', 'Operator')
        self.actionResult.addResultColumn('EXPECTED', 'Expected')
        self.actionResult.addResultColumn('CONFIGURED', 'Configured')

    def retrieveData(self, **parameters):

        result = self.systemConnection.call_fm('PFL_READ_PROFILE_FROM_DB')

    def _singleProfileContent(self, profilename:str):
        """ Get the content of a single profile


        :param profilename: NAme of the profile to download """

        result = self.systemConnection.call_fm('PFL_READ_PROFILE_FROM_DB', PROFILE_NAME=profilename)

        if result.fail:
            return result

        profileData = result.data.get('DTAB')
        parameter = None
        value = None

        configuredParameters = list()

        # Append an empty row at the end of the data
        profileData.append({'PARNAME': None, 'COMNR': '0001'})

        for counter, row in enumerate(profileData):
            if row['PARNAME'] and row['COMNR'] == '9990':
                if parameter and value and profilename:
                    configuredParameters.append(dict(PVALUE=value, PARNAME=parameter, PFNAME=profilename))
                parameter = row['PARNAME']
                value = row['PVALUE']
                profilename=row['PFNAME']
            elif row['COMNR'] in ['9991', '9992', '9993', '9994', '9995', '9996', '9997', '9998', '9999']:
                value += row['PVALUE']
            elif row['COMNR'] == '0001':
                if parameter and value:
                    record=dict(PVALUE = value,
                                PARNAME = parameter,
                                PFNAME = profilename)
                    configuredParameters.append(record)
                    parameter = None
                    value = None
                    profilename = None

        return Result(data=configuredParameters)

    def _profileContents(self):
        """ Get Contents of all profiles

        :param profilename: Profile Name

        Parameter values spanning over multiple lines, are identified by column COMNR.


        """

        result=self._profileNames()
        if result.fail:
            return result

        profilenames=result.data

        self.logger.debug('Reading Profile Contents')
        self.logger.debug('Reading Default Profile from DB')

        profileContents=dict(DEFAULT=[],
                             INSTANCE=[],
                             START=[])

        for type, names in profilenames.items():
            for name in names:
                result=self._singleProfileContent(name)
                if result.fail:
                    return result

                profileContents[type].extend(result.data)

        return Result(data=profileContents)

    def _profileNames(self)->Result:
        """ Get the names of the Profiles in the database """
        self.logger.debug('reading profiles from system')
        instance_profiles = None
        start_profiles = None
        result = self.systemConnection.call_fm('PFL_GET_PROF_LIST')
        if result.fail:
            return result

        instance_profiles = set(
            [record['PFNAME'] for record in result.data['HEADER_TAB'] if record['TYPE'] == 'I'])
        start_profiles = set(
            [record['PFNAME'] for record in result.data['HEADER_TAB'] if record['TYPE'] == 'S'])
        default_profiles = set(
            [record['PFNAME'] for record in result.data['HEADER_TAB'] if record['TYPE'] == 'D'])

        result=Result(data={'DEFAULT':default_profiles, 'INSTANCE':instance_profiles, 'START':start_profiles})

        return result

    def execute(self):

        result = self._profileContents()
        if result.fail:
            self.rateOverallResult(error=True, errormessage=result.fail)
            return Result(data=self.actionResult)

        profileContents=result.data
        profileReference=ProfileParameterReference(profileContents)

        for parameterSet in self.checkObject.params:

            profiledata = profileReference.getValue(parameterSet.parameter, parameterSet.profiletype)

            if len(profiledata) == 0:
                record = dict(PARAMETERSET=parameterSet.param_set_name,
                              PARAMETER=parameterSet.parameter,
                              RATING='pass',
                              PROFILETYPE=parameterSet.profiletype,
                              OPERATOR=parameterSet.operator,
                              EXPECTED=parameterSet.expected,
                              PROFILENAME='',
                              CONFIGURED=None)
                record=self.rateIndividualResult(record)
                self.actionResult.addResult(record)
            else:
                for data in profiledata:
                    record = dict(PARAMETERSET=parameterSet.param_set_name,
                                  PARAMETER=parameterSet.parameter,
                                  RATING='pass',
                                  PROFILETYPE=parameterSet.profiletype,
                                  OPERATOR=parameterSet.operator,
                                  PROFILENAME=data.get('PFNAME'),
                                  EXPECTED=parameterSet.expected,
                                  CONFIGURED=data.get('PVALUE'))

                    record = self.rateIndividualResult(record)
                    self.actionResult.addResult(record)