from systemcheck.checks.models.checks import Check
from systemcheck.models.meta import Base, ChoiceType, Column, ForeignKey, Integer, QtModelMixin, String, qtRelationship, \
    relationship, RichString, generic_repr, OperatorMixin, BaseMixin
from systemcheck.systems.ABAP.models import ActionAbapIsNotClientSpecificMixin

@generic_repr
class ActionAbapRuntimeParameter__params(QtModelMixin, Base, OperatorMixin, BaseMixin):
    __tablename__ = 'ActionAbapRuntimeParameter__params'

    __table_args__ = {'extend_existing':True}


    id = Column(Integer, primary_key=True)

    parent_id = Column(Integer, ForeignKey('ActionAbapRuntimeParameter.id'))

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
                        )

    check = qtRelationship("ActionAbapRuntimeParameter", back_populates="params")


    __qtmap__ = [param_set_name, parameter, OperatorMixin.operator, expected_value]

@generic_repr
class ActionAbapRuntimeParameter(Check, ActionAbapIsNotClientSpecificMixin):

    __tablename__ = 'ActionAbapRuntimeParameter'

    __table_args__ = {'extend_existing':True}

    id = Column(Integer, ForeignKey('checks_metadata.id'), primary_key=True)
    params = qtRelationship('ActionAbapRuntimeParameter__params', cascade="all, delete-orphan")


    __mapper_args__ = {
        'polymorphic_identity':'ActionAbapRuntimeParameter',
    }

    __qtmap__ = [Check.name, Check.description, Check.failcriteria, Check.criticality]

