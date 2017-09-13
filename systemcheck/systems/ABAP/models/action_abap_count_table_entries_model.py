from systemcheck.checks.models.checks import Check
from systemcheck.models.meta import Base, ChoiceType, Column, ForeignKey, Integer, QtModelMixin, String, qtRelationship, \
    relationship, RichString, generic_repr
from systemcheck.systems.ABAP.models import ActionABAPClientSpecificMixin

@generic_repr
class ActionAbapCountTableEntries__params(QtModelMixin, Base):
    __tablename__ = 'ActionAbapCountTableEntries__params'

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

    parent_id = Column(Integer, ForeignKey('ActionAbapCountTableEntries.id'))

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

    check = relationship("ActionAbapCountTableEntries", back_populates="params")


    __qtmap__ = [param_set_name, table_name, table_fields, where_clause, expected_count, operator]

@generic_repr
class ActionAbapCountTableEntries(Check, ActionABAPClientSpecificMixin):

    __tablename__ = 'ActionAbapCountTableEntries'

    __table_args__ = {'extend_existing':True}

    id = Column(Integer, ForeignKey('checks_metadata.id'), primary_key=True, qt_show=False)
    params = qtRelationship('ActionAbapCountTableEntries__params', qt_show=True, rel_class = ActionAbapCountTableEntries__params)


    __mapper_args__ = {
        'polymorphic_identity':'ActionAbapCountTableEntries',
    }

    __qtmap__ = [Check.name, Check.description, Check.failcriteria, ActionABAPClientSpecificMixin.client_specific]

