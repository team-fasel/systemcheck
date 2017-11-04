from systemcheck.checks.models.checks import Check
from systemcheck.models.meta import Base, ChoiceType, Column, ForeignKey, Integer, QtModelMixin, String, qtRelationship, \
    relationship, RichString, generic_repr, OperatorMixin, BaseMixin, TableNameMixin
from systemcheck.systems.ABAP.models import ActionAbapClientSpecificMixin
from sqlalchemy import inspect

plugin_name = 'ActionAbapManualCheck'


@generic_repr
class ActionAbapManualCheck__params(QtModelMixin, Base, BaseMixin, TableNameMixin):

    __tablename__ = plugin_name+'__params'

    __table_args__ = {'extend_existing':True}


    id = Column(Integer, primary_key=True)

    parent_id = Column(Integer, ForeignKey(plugin_name+'.id'))

    param_set_name = Column(String,
                        nullable=False,
                        qt_description='Name of the parameter set. It is easier to navigate a large list of parameter sets, if they have a descriptive name',
                        qt_label='Parameter Set Name',
                        qt_show=False,
                        default = 'Please Maintain'
                        )

    description = Column(RichString,
                        nullable=True,
                        qt_description='Detailed description of the manual activity',
                        qt_label='Manual Action',
                        )

    check = relationship("ActionAbapCountTableEntries", back_populates="params")


    __qtmap__ = [param_set_name, description]

@generic_repr
class ActionAbapManualCheck(Check, ActionAbapClientSpecificMixin):

    __tablename__ = plugin_name

    __table_args__ = {'extend_existing':True}

    id = Column(Integer, ForeignKey('checks_metadata.id'), primary_key=True, qt_show=False)


    params = qtRelationship(plugin_name + '__params',
                            qt_show=True,
                            cascade="all, delete-orphan",
                            back_populates="check")


    __mapper_args__ = {
        'polymorphic_identity':plugin_name,
    }

    __qtmap__ = [Check.name, Check.description, Check.failcriteria, Check.criticality,
                 ActionAbapClientSpecificMixin.client_specific]

