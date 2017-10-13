from systemcheck.checks.models.checks import Check
from systemcheck.models.meta.orm_choices import choices
from systemcheck.models.meta import Base, ChoiceType, Column, ForeignKey, Integer, QtModelMixin, String, qtRelationship, \
    relationship, RichString, generic_repr, Boolean, RestrictionsMixin, OperatorMixin, Date, DateTime, Time
from systemcheck.systems.ABAP.models import ActionAbapIsNotClientSpecificMixin
from systemcheck.models.meta import CheckFailCriteriaOptions, InclusionChoice, OperatorChoice, ComponentChoice
from systemcheck import models

pluginName='ActionAbapJobSchedulingValidation'

@generic_repr
class ActionAbapJobSchedulingValidation(Check, ActionAbapIsNotClientSpecificMixin):

    __tablename__ = pluginName

    id = Column(Integer, ForeignKey('checks_metadata.id'), primary_key=True)
    params = relationship(pluginName+'__params', cascade="all, delete-orphan")

    __mapper_args__ = {
        'polymorphic_identity':pluginName,
    }

    __qtmap__ = [Check.name, Check.description, Check.failcriteria]

@choices
class ActionAbapJobSchedulingValidationIntervalType:
    class Meta:
        HOUR = ['H', 'Hours']
        DAY = ['D', 'Days']
        MIN = ['M', 'Minutes']
        WEEK = ['W', 'Weeks']
        YEAR = ['Y', 'Year']

@choices
class ActionAbapJobSchedulingValidationComparisonOperator:
    class Meta:
        LE = ['LE', 'lower or equal']
        LT = ['LT', 'lower than']
        EQ = ['EQ', 'equal']
        HE = ['HE', 'higher or equal']
        HT = ['HT', 'higher than']

@generic_repr
class ActionAbapJobSchedulingValidation__params(QtModelMixin, Base, OperatorMixin):
    """ Job Scheduling Validation:



    """

    __tablename__ = pluginName+'__params'

    check = relationship(pluginName, back_populates="params")

    id = Column(Integer, ForeignKey('checks_metadata.id'), primary_key=True)


    param_set_name = Column(String,
                            qt_label='Parameter Set Name',
                            qt_description='Parameter Set Description')

    expected_count = Column(Integer,
                            qt_label='Expected Executions')

    operator = Column(String,
                      qt_label='Comparison Operator',
                      choices=ActionAbapJobSchedulingValidationComparisonOperator.CHOICES,
                      default=ActionAbapJobSchedulingValidationComparisonOperator.LE)

    interval = Column(Integer,
                      qt_label='Interval',
                      qt_description='Interval, for example 3 for 3 hours')

    interval_type=Column(String,
                         qt_label='Interval Type',
                         qt_description='Interval Type',
                         choices=ActionAbapJobSchedulingValidationIntervalType.CHOICES,
                         default=ActionAbapJobSchedulingValidationIntervalType.HOUR)

    #executionclient = Column(String, qt_label='Client', qt_description='Client')
    abapname = Column(String, qt_label='ABAP Program Name', qt_description='Name of the ABAP Program')
    sel_jobname = Column(String, qt_label='Job Name', qt_description='Name of the Job')
    sel_jobcount = Column(String, qt_label='Job Count', qt_description='Internal Number of the job')
    sel_jobgroup = Column(String, qt_label='Job Group', qt_description='Job Group')
    sel_username = Column(String, qt_label='Username', qt_description='Job Scheduler')
    sel_from_date = Column(Date, qt_label='From Date', qt_description='From Date')
    sel_from_time = Column(Time, qt_label='From Time', qt_description='From Time')
    sel_to_date  = Column(Date, qt_label='To Date', qt_description='To Date')
    sel_to_time = Column(Time, qt_label='To Time', qt_description='To Time')

    sel_no_date = Column(Boolean,
                         qt_label='Without Date',
                         qt_description='No Date',
                         choices=models.meta.YesNoChoice.CHOICES)

    sel_with_pred = Column(Boolean,
                           qt_label='With Predecessor',
                           qt_description='With Predecessor',
                           choices=models.meta.YesNoChoice.CHOICES)

    sel_eventid = Column(String, qt_label='Event ID', qt_description='Event ID')
    sel_eventpara = Column(String, qt_label='Event Parameter', qt_description='Event Parameter')

    sel_prelim = Column(Boolean,
                        qt_label='Status Preliminary',
                        qt_description='Status Preliminary',
                        choices=models.meta.YesNoChoice.CHOICES)

    sel_schedul= Column(Boolean,
                        qt_label='Status Scheduled',
                        qt_description='Status Scheduled',
                        choices=models.meta.YesNoChoice.CHOICES)

    sel_ready = Column(Boolean,
                       qt_label='Status Ready',
                       qt_description='Status Ready',
                       choices=models.meta.YesNoChoice.CHOICES)

    sel_running = Column(Boolean,
                         qt_label='Status Running',
                         qt_description='Status Running',
                         choices=models.meta.YesNoChoice.CHOICES)

    sel_finished  = Column(Boolean,
                           qt_label='Status Finished',
                           qt_description='Status Finished',
                           choices=models.meta.YesNoChoice.CHOICES)

    sel_aborted  = Column(Boolean,
                          qt_label='Status Aborted',
                          qt_description='Status Aborted',
                          choices=models.meta.YesNoChoice.CHOICES)


    #TODO: At some point, add the selection options for dates and time

    __qtmap__ = [param_set_name, expected_count, operator, interval, interval_type, abapname, sel_jobname, sel_jobcount,
                 sel_jobgroup, sel_username, sel_with_pred, sel_eventid, sel_prelim, sel_schedul, sel_ready, sel_running, sel_finished, sel_aborted]
