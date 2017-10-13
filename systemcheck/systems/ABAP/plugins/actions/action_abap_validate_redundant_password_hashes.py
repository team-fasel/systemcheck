from systemcheck.systems import ABAP
import systemcheck
import logging
from pprint import pformat
import re

class ActionAbapValidateRedundantPasswordHashes(systemcheck.plugins.ActionAbapCheck):
    """ Validate the scheduling of batch jobs

    """

    def __init__(self):

        super().__init__()
        self.logger=logging.getLogger(self.__class__.__name__)

        self.alchemyObjects = [ABAP.models.ActionAbapValidateRedundantPasswordHashes,
                               ABAP.models.ActionAbapFolder]

    def _buildSpoolParams(self)->dict:

        spoolParams = dict(PDEST=self.checkObject.PDEST,
                           PRNEW = 'X',
                           PAART='X_65_132')

        if self.checkObject.PRBIG:
            spoolParams['PRBIG']=self.boolmapper(self.checkObject.PRBIG)

        if self.checkObject.PRSAP:
            spoolParams['PRSAP'] = self.boolmapper(self.checkObject.PRSAP)

        if self.checkObject.PRIMM:
            spoolParams['PRIMM'] = self.boolmapper(self.checkObject.PRIMM)

        self.logger.debug('Spool Parameters: %s', pformat(spoolParams))
        return spoolParams

    def initializeResult(self):

        self.actionResult.addResultColumn('RATING', 'Rating')
        self.actionResult.addResultColumn('TABLE', 'Table')
        self.actionResult.addResultColumn('EXPECTED', 'Expected Counts')
        self.actionResult.addResultColumn('OPERATOR', 'Operator')
        self.actionResult.addResultColumn('CONFIGURED', 'Number of Users')
        self.actionResult.addResultColumn('LOGRECORD', 'Log Record')

    def retrieveData(self, **parameters):

        result = self.systemConnection.call_fm('TH_SERVER_LIST')

    def execute(self):

        # Setup Job for
        job_param = dict(JOBNAME='SystemCheck: Red. Password Hashes')
        job_stepParams=[]

        job_stepParam=dict(ABAP_PROGRAM_NAME='CLEANUP_PASSWORD_HASH_VALUES',
                          ALLPRIPAR=self._buildSpoolParams())

        if self.checkObject.SAP_USER_NAME:
            job_stepParam['SAP_USER_NAME']=self.checkObject.SAP_USER_NAME

        job_stepParams.append({'type':'ABAP',
                               'params':job_stepParam})

        result = self.systemConnection.btc_schedule_job(jobptions=job_param,
                                               stepoptions=job_stepParams)

        if result.fail:
            self.actionResult.rating='error'
            self.actionResult.errorMessage=result.fail
            return self.actionResult


        # Get Spool
        spoolinfo = result.data.get('SPOOL_ATTR')
        if len(spoolinfo)>0:
            relevant_spoolinfo=spoolinfo[0]
        else:
            self.actionResult.rating='error'
            self.actionResult.errorMessage = 'No Spool for jobname "SystemCheck: Red. Password Hashes"'
            return self.actionResult

        spoolid = relevant_spoolinfo.get('SPOOLID')

        result=self.systemConnection.btc_xbp_generic_bapi_caller('BAPI_XBP_GET_SPOOL_AS_DAT', SPOOL_REQUEST=spoolid)

        if result.fail:
            self.actionResult.rating='error'
            self.actionResult.errorMessage=result.message
            return self.actionResult

        spool=result.data['SPOOL_LIST']

        #Analyze Spool

        self.logger.debug('analyzing spool file')
        for lineNumber, spoolLine in enumerate(spool):
            if 'Checking table USR02 ...' in spoolLine['']:
                usr02Start=lineNumber
            elif 'Checking table USH02 ...' in spoolLine['']:
                ush02Start=lineNumber
            elif 'Checking table USRPWDHISTORY ...' in spoolLine['']:
                usrpwdhistoryStart=lineNumber

        counter=usr02Start+1
        withinLogRecord=True
        numUsers=None
        logRecord=None

        parsedLines=[]

        # Start working the log lines for table USR02 until USH02 begins
        for lineNumber, item in enumerate(spool):
            if lineNumber>usr02Start:
                lineText=item[''].strip()
                match=re.match('(^\d+)', lineText)
                if match or lineText.startswith('Checking table'):
                    # Line starts with a digit
                    if numUsers:
                        if usr02Start < lineNumber-1 < ush02Start:
                            parsedLines.append(['USR02', numUsers, logRecord])
                        elif ush02Start < lineNumber-1 < usrpwdhistoryStart:
                            parsedLines.append(['USH02', numUsers, logRecord])
                        elif lineNumber-1 > usrpwdhistoryStart:
                            parsedLines.append(['USRPWDHISTORY', numUsers, logRecord])

                    if not lineText.startswith('Checking table'):
                        numUsers=match.group(0)
                        matchRecord=re.match('\d+(.*)', lineText)
                        if matchRecord:
                            logRecord=matchRecord.groups()[0]
                        else:
                            logRecord=''
                else:
                    if lineNumber<len(spool)-1:
                        logRecord+=lineText
                if lineNumber==len(spool)-1:
                    parsedLines.append(['USRPWDHISTORY', numUsers, logRecord])

        self.logger.debug('Parsed Spool results: %s', pformat(parsedLines))

        for item in parsedLines:
            record=dict(RATING='pass',
                        TABLE=item[0],
                        EXPECTED=0,
                        OPERATOR='equal',
                        CONFIGURED=item[1],
                        LOGRECORD=item[2])

            record=self.rateIndividualResult(record)
            self.actionResult.addResult(record)

        self.rateOverallResult()
        return self.actionResult

