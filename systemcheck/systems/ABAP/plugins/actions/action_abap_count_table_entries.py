import systemcheck
from systemcheck.systems import ABAP
from systemcheck.checks.models import Check
from systemcheck.utils import Result, Fail


from systemcheck.checks.models.checks import Check
from systemcheck.models.meta import Base, ChoiceType, Column, ForeignKey, Integer, QtModelMixin, String, qtRelationship, relationship, RichString
from systemcheck.systems import ABAP
from pprint import pformat

print('importing module {}'.format(__name__))

class ActionAbapCountTableEntriesAction(systemcheck.plugins.ActionAbapCheck):
    """ A SELECT COUNT(*) for ABAP Tables


    """

    def __init__(self):
        super().__init__()
        self.alchemyObjects = [ABAP.models.ActionAbapCountTableEntries,
                               ABAP.models.ActionAbapCountTableEntries__params,
                               Check,
                               ABAP.models.ActionAbapFolder]

    def initializeResult(self):

        self.actionResult.addResultColumn('PARAMETERSET', 'Parameter Set Name')
        self.actionResult.addResultColumn('RATING', 'Rating')
        self.actionResult.addResultColumn('WHERE_CLAUSE', 'Where Clause')
        self.actionResult.addResultColumn('TABLE', 'Table')
        self.actionResult.addResultColumn('EXPECTED', 'Expected')
        self.actionResult.addResultColumn('OPERATOR', 'Operator')
        self.actionResult.addResultColumn('CONFIGURED', 'Configured')

    def retrieveData(self, **parameters):

        result = self.systemConnection.download_table(**parameters)
        return result



    def execute(self):

        checkobj = self.checkObject
        for id, parameterSet in enumerate(checkobj.params):
            self.logger.debug('Parameter Set {}, Options: {}'.format(id, pformat(parameterSet.__repr__)))
            record=dict(RATING='pass',
                        WHERE_CLAUSE=parameterSet.where_clause,
                        TABLE=parameterSet.table_name,
                        EXPECTED=parameterSet.expected_count,
                        OPERATOR=self.operators.lookup(parameterSet.operator),
                        PARAMETERSET = parameterSet.param_set_name)

            tab_fields=parameterSet.table_fields.split(';')

            result=self.retrieveData(tabname=record['TABLE'],
                                     where_clause=record['WHERE_CLAUSE'],
                                     tab_fields=tab_fields)
            if not result.fail:
                downloaded_data=result.data['data']
                record['CONFIGURED']=len(downloaded_data)
            else:
                record['CONFIGURED']=result.fail
                record['RATING']='error'
                self.actionResult.add_result(record)
                self.actionResult.rating='error'
                return Result(self.actionResult)


            record = self.rateIndividualResult(record)
            self.actionResult.addResult(record)

        self.rateOverallResult()

        return Result(data=self.actionResult)
