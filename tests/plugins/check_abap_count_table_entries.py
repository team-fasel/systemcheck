from yapsy.IPlugin import IPlugin


# class CheckAbapCountTableEntries(Check):
#
#     __tablename__ = 'CheckAbapCountTableEntries'
#
#     CHOICE_OPERATION = [('MERGE', 'Merge'),
#                         ('INDIVIDUAL', 'Treat Individually')]
#
#     id = Column(Integer, ForeignKey('checks_metadata.id'), primary_key=True)
#     params = relationship('CheckAbapCountTableEntries__params')
#     operation = Column(ChoiceType(CHOICE_OPERATION),
#                        default = 'INDIVIUAL',
#                        qt_description='Merge so that only common results are presented',
#                        qt_label = 'Operator',
#                        choices=CHOICE_OPERATION)
#
#     __mapper_args__ = {
#         'polymorphic_identity':'CheckAbapCountTableEntries',
#     }
#
# class CheckAbapCountTableEntries__params(QtModelMixin, Base):
#     __tablename__ = 'CheckAbapCountTableEntries__params'
#
#     CHOICE_OPERATOR = [('EQ', 'Equal'),
#                        ('NE', 'Not Equal'),
#                        ('GT', 'Greater Than'),
#                        ('LT', 'Lower Than'),
#                        ('GE', 'Greater or Equal'),
#                        ('LE', 'Lower or Equal')
#                        ]
#
#     id = Column(Integer, primary_key=True)
#     parent_id = Column(Integer, ForeignKey('CheckAbapCountTableEntries.id'))
#     table_name = Column(String,
#                         nullable=False,
#                         qt_description='Table Name',
#                         qt_label='Table Name',
#                         qt_show=True
#                         )
#
#     table_fields = Column(String,
#                         nullable=True,
#                         qt_description='Table Fields',
#                         qt_label='Table Fields',
#                         qt_show=True
#                         )
#
#     where_clause = Column(String,
#                         nullable=True,
#                         qt_description='Where Clause',
#                         qt_label='Where Clause',
#                         qt_show=True
#                         )
#
#     expected_count = Column(Integer,
#                             nullable=False,
#                             qt_description = 'Expected Count',
#                             qt_label = 'Expected Count',
#                             qt_show = True,
#                             )
#
#     operator = Column(ChoiceType(CHOICE_OPERATOR),
#                       nullable=False,
#                       default='EQ',
#                       qt_description='Expected Count',
#                       qt_label='Expected Count',
#                       qt_show=True,
#                       )
#
#     check = relationship("CheckAbapCountTableEntries", back_populates="params")

class CheckAbapCountTableEntriesPlugin(IPlugin):



    def __init__(self, *args, **kwargs):
        super().__init__()
        self.alchemyObjects = 'Baseplugin'


    # def execute(self, connection, parameters):
    #
    #     self.pluginResult.resultDefinition = OrderedDict(RATING='Rating',
    #                                                      WHERE_CLAUSE='Where Clause',
    #                                                      OPERATOR='Operator',
    #                                                      TABLE='Table',
    #                                                      EXPECTED='Expected',
    #                                                      CONFIGURED='Configured')
    #
    #     self.connection=connection
    #
    #     for item, value in self.pluginConfig['RuntimeParameters'].items():
    #         config=self.pluginConfig['RuntimeParameters'].get(item, raw=True)
    #         data=ast.literal_eval(config)
    #
    #         record=dict(RATING='pass',
    #                     WHERE_CLAUSE=data['WHERE_CLAUSE'],
    #                     TABLE=data['TABLE'],
    #                     EXPECTED=int(data['EXPECTED']),
    #                     OPERATOR = data.get('OPERATOR'))
    #
    #         if not record['OPERATOR']:
    #             record['OPERATOR'] = 'EQ'
    #
    #         result=self.connection.download_table(record['TABLE'],
    #                                               where_clause=record['WHERE_CLAUSE'],
    #                                               tab_fields=data['COLUMNS'])
    #         if not result.fail:
    #             downloaded_data=result.data['data']
    #             record['CONFIGURED']=str(len(downloaded_data))
    #         else:
    #             record['CONFIGURED']=result.fail
    #             self.pluginResult.add_result(record)
    #             self.pluginResult.rating='error'
    #             return Result(self.pluginResult)
    #
    #         success=self.OPERATIONS[data['OPERATOR']](int(record['EXPECTED']), int(record['CONFIGURED']))
    #
    #         if not success:
    #             record['RATING']='fail'
    #             self.pluginResult.rating='fail'
    #
    #         self.pluginResult.add_result(record)
    #
    #     return Result(data=self.pluginResult)
    #


#    def alchemyObjects(self):

#        return ['CheckAbapCountTableEntries', 'CheckAbapCountTableEntries__params']