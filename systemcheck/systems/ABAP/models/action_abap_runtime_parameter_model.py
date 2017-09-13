from systemcheck.checks.models.checks import Check
from systemcheck.models.meta import Base, ChoiceType, Column, ForeignKey, Integer, QtModelMixin, String, qtRelationship, \
    relationship, RichString, generic_repr
from systemcheck.systems.ABAP.models import ActionABAPIsNotClientSpecificMixin

@generic_repr
class ActionAbapRuntimeParameter__params(QtModelMixin, Base):
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

    parameter = Column(String,
                        nullable=False,
                        qt_description='Runtime Parameter Name',
                        qt_label='Runtime Parameter Name',
                        default = 'Please Maintain'
                        )

    expected_value = Column(String,
                        nullable=True,
                        qt_description='The expected value of the parameter. Regular Expressions are initiated with regex: at the beginning',
                        qt_label='Expected Value',
                        default = 'Please Maintain'
                        )


    check = relationship("ActionAbapCountTableEntries", back_populates="params")


    __qtmap__ = [param_set_name, parameter, expected_value]

@generic_repr
class ActionAbapRuntimeParameter(Check, ActionABAPIsNotClientSpecificMixin):

    __tablename__ = 'ActionAbapRuntimeParameter'

    __table_args__ = {'extend_existing':True}

    id = Column(Integer, ForeignKey('checks_metadata.id'), primary_key=True, qt_show=False)
    params = qtRelationship('ActionAbapRuntimeParameter__params', qt_show=True, rel_class = ActionAbapRuntimeParameter__params)


    __mapper_args__ = {
        'polymorphic_identity':'ActionAbapRuntimeParameter',
    }

    __qtmap__ = [Check.name, Check.description, Check.failcriteria]

