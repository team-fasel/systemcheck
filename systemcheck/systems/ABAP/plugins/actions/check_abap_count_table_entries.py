import ast
from collections import OrderedDict

from systemcheck.checks.models.checks import Check
from systemcheck.models.meta import Base, ChoiceType, Column, ForeignKey, Integer, QtModelMixin, String, relationship
from systemcheck.systems.ABAP.plugins.action_types import CheckAbapFoundationAction
from systemcheck.utils import Result


class CheckAbapCountTableEntries(Check):

    __tablename__ = 'CheckAbapCountTableEntries'

    __table_args__ = {'extend_existing':True}

    CHOICE_OPERATION = [('MERGE', 'Merge'),
                        ('INDIVIDUAL', 'Treat Individually')]


    id = Column(Integer, ForeignKey('checks_metadata.id'), primary_key=True, qt_show=False)
    params = relationship('CheckAbapCountTableEntries__params')
    operation = Column(ChoiceType(CHOICE_OPERATION),
                       default = 'INDIVIUAL',
                       qt_description='Merge so that only common results are presented',
                       qt_label = 'Operator',
                       choices=CHOICE_OPERATION,
                       qt_show=False)

    __mapper_args__ = {
        'polymorphic_identity':'CheckAbapCountTableEntries',
    }

class CheckAbapCountTableEntries__params(QtModelMixin, Base):
    __tablename__ = 'CheckAbapCountTableEntries__params'

    __table_args__ = {'extend_existing':True}


    CHOICE_OPERATOR = [('EQ', 'Equal'),
                       ('NE', 'Not Equal'),
                       ('GT', 'Greater Than'),
                       ('LT', 'Lower Than'),
                       ('GE', 'Greater or Equal'),
                       ('LE', 'Lower or Equal')
                       ]

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('CheckAbapCountTableEntries.id'))
    table_name = Column(String,
                        nullable=False,
                        qt_description='Table Name',
                        qt_label='Table Name',
                        qt_show=False
                        )

    table_fields = Column(String,
                        nullable=True,
                        qt_description='Table Fields',
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
                            )

    operator = Column(ChoiceType(CHOICE_OPERATOR),
                      nullable=False,
                      default='EQ',
                      qt_description='Expected Count',
                      qt_label='Expected Count',
                      qt_show=False,
                      )

    check = relationship("CheckAbapCountTableEntries", back_populates="params")

class CheckAbapCountTableEntriesAction(CheckAbapFoundationAction):
    """ A SELECT COUNT(*) for ABAP Tables


    """

    def __init__(self):
        super().__init__()
        self.alchemyObjects=[CheckAbapCountTableEntries, CheckAbapCountTableEntries__params]

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

