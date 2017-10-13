import systemcheck
from systemcheck.systems import ABAP
from systemcheck.checks.models import Check
from systemcheck.utils import Result, Fail, datecalc
from pprint import pformat

from systemcheck.checks.models.checks import Check
from systemcheck.models.meta import Base, ChoiceType, Column, ForeignKey, Integer, QtModelMixin, String, qtRelationship, relationship, RichString
from systemcheck.systems import ABAP
from datetime import datetime

""" 
Plugin for Validating the scheduling of Jobs
============================================ 

Relevant Notes
--------------

- 1770388 - Enhancements in the XBP interface


Description
-----------

Using the BAPI 


"""


class ActionAbapJobSchedulingValidationAction(systemcheck.plugins.ActionAbapCheck):
    """ Validate the scheduling of batch jobs


    """

    def __init__(self):
        super().__init__()
        self.alchemyObjects = [ABAP.models.ActionAbapJobSchedulingValidation,
                               ABAP.models.ActionAbapJobSchedulingValidation__params,
                               Check,
                               ABAP.models.ActionAbapFolder]

    def initializeResult(self):

        self.actionResult.addResultColumn('PARAMETERSET', 'Parameter Set Name')
        self.actionResult.addResultColumn('EXPECTED', 'Expected')
        self.actionResult.addResultColumn('OPERATOR', 'Operator')
        self.actionResult.addResultColumn('CONFIGURED', 'Configured')
        self.actionResult.addResultColumn('INTERVAL', 'Interval')
        self.actionResult.addResultColumn('INTERVAL_TYPE', 'Interval Type')
        self.actionResult.addResultColumn('ABAPNAME', 'ABAP Name')
        self.actionResult.addResultColumn('JOBNAME', 'Job Name')
        self.actionResult.addResultColumn('JOBCOUNT', 'Job Count')
        self.actionResult.addResultColumn('JOBGROUP', 'Job Group')
        self.actionResult.addResultColumn('USERNAME', 'Username')
        self.actionResult.addResultColumn('NODATE', 'No Date')
        self.actionResult.addResultColumn('WITH_PRED', 'With Pred')
        self.actionResult.addResultColumn('EVENTID', 'Event ID')
        self.actionResult.addResultColumn('EVENTARA', 'Event Param')
        self.actionResult.addResultColumn('PRELIM', 'Status Preliminary')
        self.actionResult.addResultColumn('SCHEDUL', 'Status Scheduled')
        self.actionResult.addResultColumn('READY', 'Status Ready')
        self.actionResult.addResultColumn('RUNNING', 'Status Running')
        self.actionResult.addResultColumn('FINISHED', 'Status Finished')
        self.actionResult.addResultColumn('ABORTED', 'Status Aborted')

    def retrieveData(self, **parameters):

        result = self.systemConnection.btc_xbp_job_select(**parameters)
        return result

    def execute(self):

        checkobj = self.checkObject
        for parameterSet in checkobj.params:
            record=dict(PARAMETERSET = parameterSet.param_set_name,
                        EXPECTED = parameterSet.expected_count,
                        OPERATOR = self.operators.lookup(parameterSet.operator),
                        INTERVAL = parameterSet.interval,
                        INTERVAL_TYPE = self.INTERVALS.get(parameterSet.interval_type),
                        ABAPNAME = parameterSet.abapname,
                        JOBNAME = parameterSet.sel_jobname,
                        JOBCOUNT = parameterSet.sel_jobcount,
                        JOBGROUP = parameterSet.sel_jobgroup,
                        USERNAME = parameterSet.sel_username,
                        NODATE = self.boolmapper(parameterSet.sel_no_date),
                        WITH_PRED = self.boolmapper(parameterSet.sel_with_pred),
                        EVENTID = parameterSet.sel_eventid,
                        EVENTPARA = parameterSet.sel_eventpara,
                        PRELIM =  self.boolmapper(parameterSet.sel_prelim),
                        SCHEDUL =  self.boolmapper(parameterSet.sel_schedul),
                        READY =  self.boolmapper(parameterSet.sel_ready),
                        RUNNING =  self.boolmapper(parameterSet.sel_running),
                        FINISHED =  self.boolmapper(parameterSet.sel_finished),
                        ABORTED =  self.boolmapper(parameterSet.sel_aborted),
                        )

            parameters = dict()
            if parameterSet.abapname:
                parameters['ABAPNAME']=parameterSet.abapname

            parameters['JOB_SELECT_PARAM']=dict()
            parameters['JOB_SELECT_PARAM']['JOBNAME'] = parameterSet.sel_jobname or '*'
            parameters['JOB_SELECT_PARAM']['USERNAME'] = parameterSet.sel_username or '*'

            if parameterSet.sel_jobcount:
                parameters['JOB_SELECT_PARAM']['JOBCOUNT'] = parameterSet.sel_jobcount

            if parameterSet.sel_jobgroup:
                parameters['JOB_SELECT_PARAM']['JOBGROUP'] = parameterSet.sel_jobgroup


            if parameterSet.sel_no_date:
                parameters['JOB_SELECT_PARAM']['NODATE'] = self.boolmapper(parameterSet.sel_no_date)

            if parameterSet.sel_with_pred:
                parameters['JOB_SELECT_PARAM']['WITH_PRED'] = self.boolmapper(parameterSet.sel_with_pred)

            if parameterSet.sel_eventid:
                parameters['JOB_SELECT_PARAM']['EVENTID']=parameterSet.sel_eventid

            if parameterSet.sel_eventpara:
                parameters['JOB_SELECT_PARAM']['EVENTPARA'] = parameterSet.sel_eventpara

            if parameterSet.sel_prelim:
                parameters['JOB_SELECT_PARAM']['PRELIM'] = self.boolmapper(parameterSet.sel_prelim)

            if parameterSet.sel_schedul:
                parameters['JOB_SELECT_PARAM']['SCHEDUL'] = self.boolmapper(parameterSet.sel_schedul)

            if parameterSet.sel_ready:
                parameters['JOB_SELECT_PARAM']['READY'] =  self.boolmapper(parameterSet.sel_ready)

            if parameterSet.sel_running:
                parameters['JOB_SELECT_PARAM']['RUNNING'] =  self.boolmapper(parameterSet.sel_running)

            if parameterSet.sel_finished:
                parameters['JOB_SELECT_PARAM']['FINISHED'] = self.boolmapper(parameterSet.sel_finished)

            if parameterSet.sel_aborted:
                parameters['JOB_SELECT_PARAM']['ABORTED'] = self.boolmapper(parameterSet.sel_aborted)

            result = self.systemConnection.systemtime
            if result.fail:
                record['CONFIGURED'] = result.fail
                record['RATING'] = 'error'
                self.actionResult.addResult(record)
                self.actionResult.rating = 'error'
                return Result(self.actionResult)

            if parameterSet.sel_from_date is None and \
                parameterSet.sel_from_time is None and \
                parameterSet.sel_to_date is None and \
                parameterSet.sel_to_time is None:

                self.logger.debug('No Time frame specified')
                basetime=result.data['localtime']
                self.logger.debug('basetime: %s', pformat(basetime))
                intervall = datecalc.getIntervalDate(parameterSet.interval, parameterSet.interval_type, basetime, '-')
                self.logger.debug('interval border: %s', pformat(intervall))

                parameters['JOB_SELECT_PARAM']['FROM_DATE']=intervall.strftime("%Y%m%d")
                parameters['JOB_SELECT_PARAM']['TO_DATE']=basetime.strftime("%Y%m%d")
                parameters['JOB_SELECT_PARAM']['FROM_TIME']=intervall.strftime("%H%M%S")
                parameters['JOB_SELECT_PARAM']['TO_TIME']=basetime.strftime("%H%M%S")

            self.logger.debug('Attempting Job Selection: %s', pformat(parameters))
            result=self.retrieveData(**parameters)
            if not result.fail:
                downloaded_data=result.data
                record['CONFIGURED']=len(downloaded_data['SELECTED_JOBS'])
            else:
                record['CONFIGURED']=result.fail
                record['RATING']='error'
                self.actionResult.addResult(record)
                self.actionResult.rating='error'
                return Result(self.actionResult)


            record = self.rateIndividualResult(record)
            self.actionResult.addResult(record)

        self.rateOverallResult()

        return Result(data=self.actionResult)
