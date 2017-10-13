from systemcheck.checks.models.checks import Check
from systemcheck.models.meta.orm_choices import choices
from systemcheck.models.meta import Base, ChoiceType, Column, ForeignKey, Integer, QtModelMixin, String, qtRelationship, \
    relationship, RichString, generic_repr, Boolean, RestrictionsMixin, OperatorMixin
from systemcheck.systems.ABAP.models import ActionAbapIsNotClientSpecificMixin
from systemcheck.models.meta import CheckFailCriteriaOptions, InclusionChoice, OperatorChoice, ComponentChoice


pluginName='ActionAbapProfileValidation'

@generic_repr
class ActionAbapProfileValidation(Check, ActionAbapIsNotClientSpecificMixin):

    __tablename__ = pluginName

    id = Column(Integer, ForeignKey('checks_metadata.id'), primary_key=True)
    params = relationship(pluginName+'__params', cascade="all, delete-orphan")
# TODO: Reenable when developing a restriction approach
#    restrictions = relationship(pluginName+'__restrictions', cascade="all, delete-orphan")

    __mapper_args__ = {
        'polymorphic_identity':pluginName,
    }

    __qtmap__ = [Check.name, Check.description, Check.failcriteria]

@choices
class AbapProfileChoice:
    class Meta:
        DEFAULT = ['DEFAULT', 'Default Profile']
        INSTANCE = ['INSTANCE', 'Instance Profile']
        START = ['START', 'Start Profile']


@generic_repr
class ActionAbapProfileValidation__params(QtModelMixin, Base, OperatorMixin):
    """ Configuration for the profile validation :



    """

    __tablename__ = pluginName+'__params'

    check = relationship(pluginName, back_populates="params")
# TODO: Reenable when developing a restriction approach
#    restrictions = relationship(pluginName+'__params__restrictions')

    id = Column(Integer, ForeignKey('checks_metadata.id'), primary_key=True)


    param_set_name = Column(String,
                            qt_label='Parameter Set Name',
                            qt_description='Parameter Set Description')

    parameter = Column(String,
                       qt_label='Parameter',
                       qt_description='Profile Parameter')

    profiletype = Column(Integer,
                         qt_label='Profile',
                         choices=AbapProfileChoice.CHOICES,
                         default=AbapProfileChoice.DEFAULT)

    expected=Column(String,
                    qt_label='Expected')

    __qtmap__ = [param_set_name, parameter, profiletype, OperatorMixin.operator, expected]


#TODO: Reenable when developing a restriction approach
# @generic_repr
# class ActionAbapProfileValidation__restrictions(QtModelMixin, Base, RestrictionsMixin):
#     """ Restrictions on Check Level :
#
#
#
#     """
#
#     __tablename__ = pluginName+'__restrictions'
#
#     check = qtRelationship(pluginName, back_populates="restrictions")
#
#     id = Column(Integer, primary_key=True)
#     parent_id = Column(Integer, ForeignKey(pluginName+'.id'))
#
#     __qtmap__ = [RestrictionsMixin.inclusion,
#                  RestrictionsMixin.component,
#                  RestrictionsMixin.component_name,
#                  RestrictionsMixin.operator,
#                  RestrictionsMixin.low,
#                  RestrictionsMixin.high]
#
# @generic_repr
# class ActionAbapProfileValidation__params__restrictions(QtModelMixin, Base, RestrictionsMixin):
#     """ Restrictions on parameter set level :
#
#
#
#     """
#
#     __tablename__ = pluginName + '__params__restrictions'
#
#     paramset = qtRelationship(pluginName + "__params", back_populates="restrictions")
#
#     id = Column(Integer, primary_key=True)
#     parent_id = Column(Integer, ForeignKey(pluginName + '__params.id'))


