import ast
from collections import OrderedDict

from systemcheck.checks.models.checks import Check
from systemcheck.systems.ABAP.models import CheckABAPFolder
from systemcheck.models.meta import Base, ChoiceType, Column, ForeignKey, Integer, QtModelMixin, String, qtRelationship, relationship, RichString
from systemcheck.systems.ABAP.plugins.action_types import CheckAbapFoundationAction
from systemcheck.utils import Result


class CheckAbapCountTableEntries__params(QtModelMixin, Base):
    __tablename__ = 'CheckAbapCountTableEntries__params'

    __table_args__ = {'extend_existing':True}



#        ('Equal', 'EQ'),
#        ('Not Equal', 'NE'),
#        ('Greater Than', 'GT'),
#        ('Lower Than', 'LT'),
#        ('Greater or Equal', 'GE'),
#        ('Lower or Equal', 'LE')
#

    CHOICE_OPERATOR = [
        ('EQ', 'Equal'),
        ('NE', 'Not Equal'),
        ('GT', 'Greater Than'),
        ('LT', 'Lower Than'),
        ('GE', 'Greater or Equal'),
        ('LE', 'Lower or Equal')
                       ]

    id = Column(Integer, primary_key=True)

    parent_id = Column(Integer, ForeignKey('CheckAbapCountTableEntries.id'))

    param_set_name = Column(String,
                        nullable=False,
                        qt_description='Name of the parameter set. It is easier to navigate a large list of parameter sets, if they have a descriptive name',
                        qt_label='Parameter Set Name',
                        qt_show=False,
                        default = 'Please Maintain'
                        )

    table_name = Column(String,
                        nullable=False,
                        qt_description='Table Name',
                        qt_label='Table Name',
                        qt_show=False,
                        default = 'Please Maintain'
                        )

    table_fields = Column(String,
                        nullable=True,
                        qt_description='Table Fields, separated by a ";"',
                        qt_label='Table Fields',
                        qt_show=False
                        )

    where_clause = Column(String,
                        nullable=True,
                        qt_description='Where Clause',
                        qt_label='Where Clause',
                        qt_show=False
                        )

    expected_count = Column(Integer,
                            nullable=False,
                            qt_description = 'Expected Count',
                            qt_label = 'Expected Count',
                            qt_show = False,
                            default=0
                            )

    operator = Column(ChoiceType(CHOICE_OPERATOR),
                      nullable=True,
                      default='EQ',
                      qt_description='Comparison Operator',
                      qt_label='Comparison Operator',
                      qt_show=False,
                      choices=CHOICE_OPERATOR
                      )

    check = relationship("CheckAbapCountTableEntries", back_populates="params")


    __qtmap__ = [param_set_name, table_name, table_fields, where_clause, expected_count, operator]


class CheckAbapCountTableEntries(Check):

    __tablename__ = 'CheckAbapCountTableEntries'

    __table_args__ = {'extend_existing':True}

    CHOICE_OPERATION = [('FAIL_IF_ANY_FAILS', 'Fail if a single parameter set fails'),
                        ('FAIL_IF_ALL_FAIL', 'Fail if all parameter sets fail')]


    id = Column(Integer, ForeignKey('checks_metadata.id'), primary_key=True, qt_show=False)
    params = qtRelationship('CheckAbapCountTableEntries__params', qt_show=True, rel_class = CheckAbapCountTableEntries__params)
    operation = Column(ChoiceType(CHOICE_OPERATION),
                       default = 'FAIL_IF_ANY_FAILS',
                       qt_description='Defines when a check is considered as failed. ',
                       qt_label = 'Fail Criteria',
                       choices=CHOICE_OPERATION,
                       qt_show=True)

    __mapper_args__ = {
        'polymorphic_identity':'CheckAbapCountTableEntries',
    }

    __qtmap__ = [Check.name, Check.description, operation]


class CheckAbapCountTableEntriesAction(CheckAbapFoundationAction):
    """ A SELECT COUNT(*) for ABAP Tables


    """

    def __init__(self):
        super().__init__()

        self.setAlchemyObjects([CheckAbapCountTableEntries, CheckAbapCountTableEntries__params, Check, CheckABAPFolder])

    def execute(self, connection, parameters):

        self.pluginResult.resultDefinition = OrderedDict(RATING='Rating',
                                                         WHERE_CLAUSE='Where Clause',
                                                         OPERATOR='Operator',
                                                         TABLE='Table',
                                                         EXPECTED='Expected',
                                                         CONFIGURED='Configured')

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

