import systemcheck
from systemcheck.systems import ABAP
from systemcheck.checks.models import Check
from systemcheck.utils import Result, Fail


from systemcheck.checks.models.checks import Check
from systemcheck.models.meta import Base, ChoiceType, Column, ForeignKey, Integer, QtModelMixin, String, qtRelationship, relationship, RichString
from systemcheck.systems import ABAP
from pprint import pformat

print('importing module {}'.format(__name__))

class ActionAbapRuntimeParameter(systemcheck.plugins.ActionAbapCheck):
    """ Validate Runtime Parameters


    """

    def __init__(self):
        super().__init__()
        self.alchemyObjects = [ABAP.models.ActionAbapRuntimeParameter,
                               ABAP.models.ActionAbapRuntimeParameter__params,
                               ABAP.models.ActionAbapFolder]

        self.initializeResult()

    def initializeResult(self):

        self.actionResult.addResultColumn('PARAMETERSET', 'Parameter Set Name')
        self.actionResult.addResultColumn('RATING', 'Rating')
        self.actionResult.addResultColumn('PARAMETER', 'Where Clause')
        self.actionResult.addResultColumn('INSTANCE', 'Instance')
        self.actionResult.addResultColumn('EXPECTED', 'Expected')
        self.actionResult.addResultColumn('OPERATOR', 'Operator')
        self.actionResult.addResultColumn('CONFIGURED', 'Configured')

    def retrieveData(self, **parameters):

        result=self.systemConnection.call_fm('TH_SERVER_LIST')
        

    def _adaptLogonInfo(self, instanceData:dict)->dict:
        """ Generate Logon Data to an individual instance"""
        self.logger.debug('retrieved instance data: '+ pformat(instanceData))
        logonInfo=self.systemObject.logon_info()
        if 'mshost' in logonInfo:
            logonInfo.pop('mshost', 0)
            logonInfo.pop('msserv', 0)
            logonInfo.pop('group', 0)

            logonInfo['ashost']=instanceData['HOSTADDR_V4_STR']
            logonInfo['sysnr']=instanceData['NAME'][-2:]

        return logonInfo


    def execute(self):

        checkobj = self.checkObject

        result = self.systemConnection.call_fm('TH_SERVER_LIST')
        if not result.fail:
            instances=result.data
        else:
            self.rateOverallResult(error=True, errormessage=result.fail)
            return Result(data=self.actionResult)

        for parameterSet in checkobj.params:

            for instance in instances['LIST_IPV6']:
                record = dict(RATING='pass',
                              PARAMETERSET=parameterSet.param_set_name,
                              PARAMETER=parameterSet.parameter,
                              EXPECTED=parameterSet.expected_value,
                              INSTANCE=instance['NAME'],
                              OPERATOR=self.operators.lookup(parameterSet.operator))
                logonInfo=self._adaptLogonInfo(instance)
                result=ABAP.utils.get_connection(logonInfo)
                if result.fail:
                    record['RATING']='error'
                    record['CONFIGURED']=result.fail
                    self.actionResult.addResult(record)
                else:
                    connection=result.data
                    result=connection.get_runtime_parameter(record['PARAMETER'])
                    if result.fail:
                        record['RATING'] = 'error'
                        record['CONFIGURED']=result.fail
                        self.actionResult.addResult(record)
                    else:
                        response=result.data
                        record['CONFIGURED']=response['value']
                        record = self.rateIndividualResult(record)
                        self.actionResult.addResult(record)
                    connection.close()
        self.rateOverallResult()

