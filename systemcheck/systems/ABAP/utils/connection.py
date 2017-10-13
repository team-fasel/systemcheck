import pyrfc
from typing import Union
from systemcheck.utils import Result, Fail
import time
import datetime
from pprint import pformat, pprint
import logging

# -*- coding: utf-8 -*-

from typing import Union
import time, datetime
from pprint import pformat
from systemcheck.config import CONFIG
import logging

try:
    import pyrfc
except ImportError:
    print('pyRFC Import Failed. Verify pyrfc has been installed correctly')
    exit(1)

import systemcheck
#from systemcheck.config import CONFIG
from systemcheck.utils import Result, Fail
from systemcheck.systems.ABAP.utils.mock_connection import MockConnection

class Connection:
    """ Wrapper for the PyRFC Connection Class"""

    XBP_EXT_PRODUCT = CONFIG['systemtype_ABAP']['xbpinterface.XBP_EXT_PRODUCT']
    XBP_EXT_COMPANY = CONFIG['systemtype_ABAP']['xbpinterface.XBP_EXT_COMPANY']
    XBP_EXT_USER = CONFIG['systemtype_ABAP']['xbpinterface.XBP_EXT_USER']
    XPB_INTERFACE_VERS = CONFIG['systemtype_ABAP']['xbpinterface.XPB_INTERFACE_VERS']

    XBP_PARAMS = dict(EXTCOMPANY=XBP_EXT_COMPANY,
                      EXTPRODUCT=XBP_EXT_PRODUCT,
                      INTERFACE='XBP',
                      VERSION=XPB_INTERFACE_VERS)


    def __init__(self, *args, **kwargs):
        pass

    def _handle_exception(self, err):

        self.logger.exception(err)
        if isinstance(err, pyrfc.ABAPRuntimeError):
            message = 'ABAP Runtime Error'
        elif isinstance(err, pyrfc.ExternalApplicationError):
            message = 'External Application Error'
        elif isinstance(err, pyrfc.ABAPApplicationError):
            message = 'ABAP Application Error'
        elif isinstance(err, pyrfc.ExternalRuntimeError):
            message = 'External Runtime Error'
        elif isinstance(err, pyrfc.CommunicationError):
            message = 'Communication Error'
        elif isinstance(err, pyrfc.LogonError):
            message = 'Logon Error'
        elif isinstance(err, pyrfc.ExternalAuthorizationError):
            message = 'External Authorization Error:'
        elif isinstance(err, pyrfc.RFCLibError):
            message = 'RFC Library Error'
        elif isinstance(err, pyrfc.RFCError):
            message = 'RFC Error'
        else:
            raise err
        return Fail(message=message, data=err)

    def btc_schedule_job(self, jobptions:dict, stepoptions:dict, closeoptions=None, releaseoptions=None,
                         waitUntilComplete=True, timeout=600, abortOnTimeout=True):
        """ Schedule a Job for immediate release


        :param jobptions: Parameters for BAPI_XBP_JOB_OPEN
        :param stepoptions: List of Parameters for each step for BAPI_XBP_ADD_JOB_STEP
        :param closeoptions: Parameters for BAPI_JOB_CLOSE
        :param releaseoptions: Parameters for BAPI_XBP_JOB_START_ASAP

        """

        if closeoptions is None:
            closeoptions=dict()

        if releaseoptions is None:
            releaseoptions=dict()


        result=self.btc_xmi_logon()
        if result.fail:
            return result

        result = self.btc_xbp_generic_bapi_caller('BAPI_XBP_JOB_OPEN', **jobptions)
        if result.fail:
            return result

        jobcount=result.data.get('JOBCOUNT')
        for stepoption in stepoptions:
            if stepoption.get('type') == 'ABAP':
                result = self.btc_xbp_generic_bapi_caller('BAPI_XBP_JOB_ADD_ABAP_STEP',
                                                          JOBNAME=jobptions['JOBNAME'],
                                                          JOBCOUNT=jobcount,
                                                          **stepoption.get('params')
                )
                if result.fail:
                    return result
            elif stepoptions.get('type') == 'EXTERNAL':
                result = self.btc_xbp_generic_bapi_caller('BAPI_XBP_JOB_ADD_EXT_STEP',
                                                          JOBNAME=jobptions['JOBNAME'],
                                                          JOBCOUNT=jobcount,
                                                          **stepoption.get('params')
                )
                if result.fail:
                    return result

        result=self.btc_xbp_generic_bapi_caller('BAPI_XBP_JOB_CLOSE',
                                                JOBNAME=jobptions['JOBNAME'],
                                                JOBCOUNT=jobcount,
                                                **closeoptions)

        if result.fail:
            return result

        result=self.btc_xbp_generic_bapi_caller('BAPI_XBP_JOB_START_ASAP',
                                                JOBNAME=jobptions['JOBNAME'],
                                                JOBCOUNT=jobcount,
                                                **releaseoptions)

        if waitUntilComplete:
            result=self.btc_xbp_delay_until_job_completed(jobname=jobptions['JOBNAME'],
                                                   jobcount=jobcount, maxDelay=timeout, abortOnTimeout=abortOnTimeout)

        result=self.btc_xbp_generic_bapi_caller('BAPI_XBP_JOB_DEFINITION_GET',
                                                JOBNAME=jobptions['JOBNAME'],
                                                JOBCOUNT=jobcount,
                                                EXTERNAL_USER_NAME=self.XBP_EXT_USER)

        self.btc_xmi_logoff()
        return result

    def btc_xbp_delay_until_job_completed(self, jobname, jobcount, sleepTime=3, maxDelay=600, abortOnTimeout=True):
        """ Wait until job completes

        The job status is encoded using the characters below.

        'R' - active
        'I' - intercepted  <- this will be an error
        'Y' - ready
        'P' - scheduled  <- this will be an error
        'S' - released
        'A' - cancelled  <- this will be an error
        'F' - finished

        OSS Notes:
            1770388 - Enhancements in the XBP interface


        :param jobname: SAP Job Name
        :param jobcount: Job Counter
        :param useFm: If True, use function module SUBST_CHECK_BATCHJOB. Otherwise query TBTCO.
        :param sleepTime: check interval in seconds
        :param maxDelay: maximum time to wait for job to complete.
        :param abortOnTimeout: Terminate the job if a timeout occurs
        """

        jobstatus = 'X'

        t0 = time.clock()

        while time.clock() - t0 < maxDelay:
            # uses the function module BAP_XBP_JOB_STATUS_GET
            self.logger.debug('waiting until batch job {:s} ({:s}) completes using '
                              'BAPI_XBP_JOB_STATUS_GET'.format(jobname, jobcount))
            result = self.call_fm('BAPI_XBP_JOB_STATUS_GET', JOBNAME=jobname, JOBCOUNT=jobcount,
                               EXTERNAL_USER_NAME=self.XBP_EXT_USER)

            if result.fail:
                return result

            if result.data['RETURN']['TYPE'] == 'E':
                logMessage = 'BAPI_XBP_JOB_STATUS_GET for job request {:s} ({:s}): {:s}'.format(jobname,
                                                                                                jobcount,
                                                                                                result.data[
                                                                                                    'RETURN'][
                                                                                                    'MESSAGE'])
                self.logger.error(logMessage)
                return Fail(message=logMessage)

            if result.data['STATUS'] in ['I', 'P', 'A']:
                logMessage=''
                if result.data['STATUS'] == 'I':
                    logMessage = 'Job %s with count %s was intercepted'.format(jobname, jobcount)
                elif result.data['STATUS'] == 'P':
                    logMessage = 'Job %s with count %s is in scheduled state and will not run'.format(jobname, jobcount)
                elif result.data['STATUS']== 'A':
                    logMessage = 'Job %s with count %s is cancelled'.format(jobname, jobcount)

                self.logger.error(logMessage)
                return Fail(message=logMessage)

            else:
                return result

        if abortOnTimeout:
            self.logger.error('Terminating job %s with jobcount %s due to timeout', jobname, jobcount)
            bapiCallOptions=dict(JOBNAME=jobname, JOBCOUNT=jobcount)
            bapiCallOptions['EXTERNAL_USER_NAME']=self.XBP_EXT_USER
            self.btc_xbp_generic_bapi_caller('BAPI_XBP_JOB_ABORT', **bapiCallOptions)

        return Fail('Max. Job Runtime {%i} Reached. Runtime: {:6.2f}'.format(sleepTime, time.time() - t0))

    def btc_xbp_generic_bapi_caller(self, bapi, **kwargs):

        """ A Generic function to call BAPIs


        OSS Notes:
            1770388 - Enhancements in the XBP interface
        """
        self.logger.debug('Executing FM %s', bapi)
        self.btc_xmi_logon()
        result = self.fm_interface(bapi)
        if result.fail:
            return result

        fm_interface = result.data
        params = [item['PARAMETER']
                  for item in fm_interface['PARAMS']
                  if item['PARAMCLASS'] != 'E']

        self.logger.debug('Identified relevant parameters: %s', pformat(params))

        bapiCallOptions=dict()
        if 'EXTERNAL_USER_NAME' in params:
            bapiCallOptions['EXTERNAL_USER_NAME'] = self.XBP_EXT_USER

        for param in params:
            if param in kwargs:
                bapiCallOptions[param] = kwargs.get(param)

        self.logger.debug('Identified Options for BAPI: %s', pformat(bapiCallOptions))

        result = self.call_fm(bapi, **bapiCallOptions)

        if result.fail:
            return result

        if result.data['RETURN']['TYPE'] == 'E':
            self.logger.error('%s: %s', bapi, result.data['RETURN']['MESSAGE'])
            return Fail(message=bapi+': ' + result.data['RETURN']['MESSAGE'],
                        data=result.data)
        else:
            self.logger.debug('BAPI_XBP_JOB_ADD_ABAP_STEP successful')
            return result

    def btc_xbp_add_job_step(self, *args, **kwargs):
        """ Add Step to the Job

        OSS Notes:
            1770388 - Enhancements in the XBP interface

        :param jobname: Name of the background job
        :param jobcount: Unique job count number for the background job
        :param program: ABAP Program Name
        :param variant: Name of the Variant
        :param spoolParams: Spool Parameters
        :return: Result(True) if the message succeeds Fail(Message) if step fails.
        """

        bapi = 'BAPI_XBP_JOB_ADD_ABAP_STEP'

        self.logger.debug('Executing FM %s', bapi)

        result = self.fm_interface(bapi)
        if result.fail:
            return result

        fm_interface=result.data
        params = [item['PARAMETER']
                  for item in fm_interface['PARAMS']
                  if item['PARAMCLASS']!='E']

        self.logger.debug('Identified relevant parameters: %s', pformat(params))

        bapiCallOptions = dict(EXTERNAL_USER_NAME=self.XBP_EXT_USER)

        for param in params:
            if param in kwargs:
                bapiCallOptions[param]=kwargs.get(param)

        self.logger.debug('Identified Options for BAPI: %s', pformat(bapiCallOptions))

        result = self.call_fm(bapi, **bapiCallOptions)

        if result.fail:
            return result

        result=result.data

        if result['RETURN']['TYPE'] == 'E':
            self.logger.error('BAPI_XBP_JOB_ADD_ABAP_STEP:' + result['RETURN']['MESSAGE'])
            return Fail('BAPI_XBP_JOB_ADD_ABAP_STEP:' + result['RETURN']['MESSAGE'])
        else:
            self.logger.debug('BAPI_XBP_JOB_ADD_ABAP_STEP successful')
            return result

    def btc_xbp_add_ext_job_step(self, jobname, jobcount, extProgramName, extProgramParameters, sapUserName,
                           destinationHost=None):
        """ Add external program as Step to the Job

        OSS Notes:
            1770388 - Enhancements in the XBP interface

        :param extProgramName: Name of the external program
        :param extProgramParameters: Parameters for the external program
        :param sapUserName: SAP Username
        :param jobname: Name of the background job
        :param jobcount: Unique job count number for the background job
        :param program: ABAP Program Name
        :return: Result(True) if the message succeeds Fail(Message) if step fails.
        """
        fmOptions = dict(JOBNAME=jobname,
                         JOBCOUNT=jobcount,
                         EXTERNAL_USER_NAME=self.XBP_EXT_USER,
                         EXT_PROGRAM_NAME=extProgramName,
                         EXT_PROGRAM_PARAMETERS=extProgramParameters,
                         SAP_USER_NAME=sapUserName)

        if destinationHost:
            fmOptions['TARGET_HOST'] = destinationHost

        self.logger.debug('calling function module BAPI_XBP_JOB_ADD_EXT_STEP with parameters %s', pformat(fmOptions))

        result = self.call_fm('BAPI_XBP_JOB_ADD_EXT_STEP', **fmOptions)

        if result.fail:
            return result

        result=result.data

        if result['RETURN']['TYPE'] == 'E':
            self.logger.error('BAPI_XBP_JOB_ADD_EXT_STEP:' + result['RETURN']['MESSAGE'])
            return Fail('BAPI_XBP_JOB_ADD_EXT_STEP:' + result['RETURN']['MESSAGE'])
        else:
            self.logger.debug('BAPI_XBP_JOB_ADD_EXT_STEP successful')
            return Result(data=True)

    def btc_xbp_get_spool_as_dat(self, spoolRequest, firstPage=None, lastPage=None):
        """ Download spool request as .csv file

        This procedure requires function module BAPI_XBP_GET_SPOOL_AS_DAT which is delivered in the
        OSS note below:

            1515293 - Transferring spool requests as delimited tab text files

        :param spoolRequest: Spool Request Number
        :param firstPage: First page of the spool request to download
        :param lastPage: Last page of the spool request to download.
        :return: Result(data) if successful or Fail(Message) if error
        """


        self.logger.debug('starting BAPI_XBP_GET_SPOOL_AS_DAT')

        fmParameters = dict(SPOOL_REQUEST=int(spoolRequest),
                            EXTERNAL_USER_NAME=self.XBP_EXT_USER)

        if firstPage:
            fmParameters['FIRST_PAGE'] = firstPage

        if lastPage:
            fmParameters['LAST_PAGE'] = lastPage

        result = self.call_fm('BAPI_XBP_GET_SPOOL_AS_DAT', **fmParameters)

        if result.fail:
            return result

        result = result.data
        if result['RETURN']['TYPE'] == 'E':
            logMessage = 'BAPI_XBP_GET_SPOOL_AS_DAT for spool request {:s}: {:s}'.format(spoolRequest,
                                                                                         result['RETURN'][
                                                                                             'MESSAGE'])
            self.logger.error(logMessage)
            return Fail(logMessage)

        self.logger.debug('BAPI_XBP_GET_SPOOL_AS_DAT successful')
        return Result(data=result)

    def btc_xbp_job_close(self, jobname, jobcount):
        """ Closes the job definition

        OSS Notes:
            1770388 - Enhancements in the XBP interface

        :param jobname: Job Name
        :param jobcount: Unique job count number for the background job
        :return: Result(True) if successful Fail(Error Message)
        """

        self.logger.debug('starting BAPI_XBP_JOB_CLOSE')
        result = self.call_fm('BAPI_XBP_JOB_CLOSE', JOBNAME=jobname,
                           JOBCOUNT=jobcount,
                           EXTERNAL_USER_NAME=self.XBP_EXT_USER)

        if result.fail:
            return result

        result=result.data

        if result['RETURN']['TYPE'] == 'E':
            logMessage = 'BAPI_XBP_JOB_CLOSE for {:s} ({:s}: '.format(jobname, jobcount,
                                                                      result['RETURN']['MESSAGE'])
            self.logger.error(logMessage)
            return Fail(message=logMessage)
        else:
            self.logger.debug('schedule_job_immediately: BAPI_XBP_JOB_CLOSE successful')
            return Result(data=True)

    def btc_xbp_job_definition_get(self, jobname:str, jobcount:str):
        """ Retrive the definition of a specfic job using function module BAPI_XBP_JOB_DEFINITION_GET.

        :param jobname: Name of the job
        :param jobcount: Job Nubmber
        :param extUserName: External User name
        :return:
        """

        self.logger.debug('starting BAPI_XBP_JOB_DEFINITION_GET')

        fmParameters = dict(JOBNAME=jobname,
                            JOBCOUNT=jobcount,
                            EXTERNAL_USER_NAME=self.XBP_EXT_USER)

        result = self.call_fm('BAPI_XBP_JOB_DEFINITION_GET', **fmParameters)

        if result.fail:
            return result

        result=result.data
        if result['RETURN']['TYPE'] == 'E':
            logMessage = 'BAPI_XBP_JOB_DEFINITION_GET for job {} ({}) failed: {}'.format(jobname, str(jobcount), result['RETURN']['MESSAGE'])
            self.logger.error(logMessage)
            return Fail(message=logMessage)
        else:
            self.logger.debug('BAPI_XBP_JOB_DEFINITION_GET successful: ' + pformat(result))
            return Result(data=result)

    def btc_xbp_job_log_read(self, jobname, jobcount, protNew=None, lines=None, direction=None):
        """ Read the log of the specified job.

        :param protNew:
        :param lines:
        :param direction:
        :param jobname: Name of the job
        :param jobcount: Job Nubmber
        :param extUserName: External User name
        :return:
        """

        self.logger.debug('starting BAPI_XBP_JOB_JOBLOG_READ')

        fmParameters = dict(JOBNAME=jobname,
                            JOBCOUNT=jobcount,
                            EXTERNAL_USER_NAME=self.XBP_EXT_USER)

        if protNew:
            fmParameters['PROT_NEW'] = protNew

        if lines:
            fmParameters['LINES'] = lines

        if direction:
            fmParameters['DIRECTION'] = direction

        result = self.call_fm('BAPI_XBP_JOB_JOBLOG_READ', **fmParameters)

        if result.fail:
            return result

        result=result.data
        if result['RETURN']['TYPE'] == 'E':
            logMessage = 'BAPI_XBP_JOB_JOBLOG_READ for job {:s} ({:d}) failed: {:s}'.format(jobname,
                                                                                            int(jobcount),
                                                                                            result['RETURN'][
                                                                                                'MESSAGE'])
            self.logger.error(logMessage)
            return Fail(logMessage)
        else:
            self.logger.debug('BAPI_XBP_JOB_JOBLOG_READ successful: ' + pformat(result))
            return Result(result)

    def btc_xbp_job_start_immediately(self, jobname, jobcount):
        """ Starts a defined job immediately

        OSS Notes:
            1770388 - Enhancements in the XBP interface

        :param jobname: Name of the Job
        :param jobcount: Unique job count number for the background job
        :return:
        """

        self.logger.debug('starting BAPI_XBP_JOB_START_IMMEDIATELY')
        result = self.call_fm('BAPI_XBP_JOB_START_IMMEDIATELY', JOBNAME=jobname,
                           JOBCOUNT=jobcount,
                           EXTERNAL_USER_NAME=self.XBP_EXT_USER)

        if result.fail:
            return result

        result=result.data
        if result['RETURN']['TYPE'] == 'E':
            logMessage = 'BAPI_XBP_JOB_START_IMMEDIATELY for {:s} ({:s}): {:s}'.format(jobname, jobcount,
                                                                                       result['RETURN']['MESSAGE'])
            self.logger.error(logMessage)
            return Fail(message=logMessage)
        else:
            self.logger.debug('schedule_job_immediately: BAPI_XBP_JOB_START_IMMEDIATELY successful')
            return Result(data=True)

    def btc_xbp_job_open(self, jobName):
        """ Perform BAPI_XBP_JOB_OPEN

        OSS Notes:
            1770388 - Enhancements in the XBP interface

        :param jobName:Name of the background job
        :return: Either Fail(True) or Result(jobcount)
        """
        result = self.call_fm('BAPI_XBP_JOB_OPEN', JOBNAME=jobName,
                           EXTERNAL_USER_NAME=self.XBP_EXT_USER)

        if result.fail:
            return result

        result=result.data
        if result['RETURN']['TYPE'] == 'E':
            logMessage = 'BAPI_XBP_JOB_OPEN {:s}: {:s}'.format(jobName, result['RETURN']['MESSAGE'])
            self.logger.error(logMessage)
            return Fail(message=logMessage)
        else:
            jobcount = result['JOBCOUNT']
            self.logger.debug('BAPI_XBP_JOB_OPEN successful for job %s with job count %s', jobName, str(jobcount))
            return Result(data=jobcount)

    def btc_xbp_job_select(self, JOB_SELECT_PARAM, ABAPNAME=None, SUSP=None, SYSTEMID=None, SELECTION=None):
        """ Get the list of jobs based on selection criteria

        :param JOB_SELECT_PARAM: table describing the jobs to retrieve. see below.
        :param ABAPNAME: Name of an ABAP program
        :param SUSP: Get suspended jobs
        :param SYSTEMID: SID of a remote system
        :param SELECTION: specified what kind of confirmation is taken into account:
                            AL - Returns all child jobs, NG - only jobs without general conf. NC - Jobs wiithout conf.
        :return:

        jobSelectParam:

        JOBNAME - Name of the job
        JOBCOUNT - Job Number
        JOBGROUP - Job Group
        USERNAME
        FROM_DATE
        FROM_TIME
        TO_DATE
        TO_TIME
        NO_DATE
        WITH_PRED
        EVENTID
        EVENTPARM
        PRELIM
        SCHEDUL
        READY
        RUNNING
        FINISHED
        ABORTED
______________________________

        """

        self.logger.debug('selecting jobs')
        fmParameters = dict()

        result = self.btc_xmi_logon()
        if result.fail:
            return result

        fmParameters['EXTERNAL_USER_NAME']=self.XBP_EXT_USER

        fmParameters['JOB_SELECT_PARAM'] = JOB_SELECT_PARAM
        self.logger.debug('JOB_SELECT_PARAM: %s', pformat(JOB_SELECT_PARAM))

        if ABAPNAME:
            self.logger.debug('ABAPNAME: %s', pformat(ABAPNAME))
            fmParameters['ABAPNAME'] = ABAPNAME

        if SUSP:
            self.logger.debug('SUSP: %s', pformat(SUSP))
            fmParameters['SUSP'] = SUSP

        if SELECTION:
            self.logger.debug('SELECTION: %s', pformat(SELECTION))
            fmParameters['SELECTION'] = SELECTION

        if SYSTEMID:
            self.logger.debug('SYSTEMID: %s', pformat(SYSTEMID))
            fmParameters['SYSTEMID'] = SYSTEMID

        result = self.call_fm('BAPI_XBP_JOB_SELECT', **fmParameters)

        self.logger.debug(pformat(result.data))


        if result.fail:
            self.logger.error('Failed to retrieve jobs: %s', result.message)
            return result

        if result.data['RETURN']['TYPE'] == 'E':
            self.logger.error('Failed to retrieve jobs. BAPIRETURN: %s', result.data['RETURN']['MESSAGE'])
            return Fail(message=result.data['RETURN']['MESSAGE'])
        else:
            return result

    def btc_xbp_variant_change(self, abapProgramName, abapVariantName, dia:bool=False, protected:bool=False,
                               merge:bool=False,
                               append_selop:bool=False,
                               variantInfo:list=None, variantInfoL:list=None, variText:list=None):

        """ Changes an already existing variant for ABAP program


        :param abapProgramName: str Program name
        :param abapVariantName: str variant name
        :param dia: batch or dialog?
        :param protected: Variant protected or not
        :param merge: Merge with existing variant
        :param append_selop: Append Selection Option
        :param variantInfo: actual data of the variant
        :param variantInfoL: data of the variant with longnr parameters
        :param variText: Variant Texts
        :return:

        The variantInfo(L) needs to be a list of dictionaries. each row consisting of these fields:

        REPORT  Report Name
        VARIANT Variant Name
        PNAME   ABAP/4: Name of SELECT-OPTION / PARAMETER
        PKIND   ABAP: Type of selection
        POLEN   ABAP: Output length of selection condition
        PTEXT   CHAR30 for SYST
        PSIGN   ABAP: ID: I/E (include/exclude values)
        POPTION ABAP: Selection option (EQ/BT/CP/...)
        PLOW    Selection variants: Field content (LOW/HIGH)
        PHIGH   Selection variants: Field content (LOW/HIGH)

        """

        result = self.btc_xmi_logon()
        if result.fail:
            self.logger.debug('logon to XBP interface failed {:s}/{:s}'.format(self.XBP_EXT_COMPANY,
                                                                               self.XBP_EXT_PRODUCT))
            return result

        self.logger.debug('logon to XBP interface successful')
        fmParameters = dict()
        fmParameters['EXTERNAL_USER_NAME'] = self.XBP_EXT_USER
        fmParameters['ABAP_PROGRAM_NAME'] = abapProgramName
        fmParameters['ABAP_VARIANT_NAME'] = abapVariantName


        if dia:
            fmParameters['DIA'] = 'X'

        if protected:
            fmParameters['DIA'] = 'X'

        if merge:
            fmParameters['MERGE']='X'

        if append_selop:
            fmParameters['APPEND_SELOP']='X'

        if variText:
            fmParameters['VARI_TEXT']=variText

        if variantInfoL:
            fmParameters['VARIANT_INFO_L'] = variantInfoL
        elif variantInfo:
            fmParameters['VARIANT_INFO'] = variantInfo
        else:
            self.logger.error('Variant info is missing')
            return Fail('Missing Variant Information')
        result = self.call_fm('BAPI_XBP_VARIANT_CHANGE', **fmParameters)
        if result.fail:
            return result

        if result.data['RETURN']['TYPE'] != 'E':
            return Result('variant changed')
        else:
            return Fail(result.data['RETURN']['MESSAGE'])

    def btc_xbp_variant_create(self, abapProgramName, abapVariantName, abapVariantText, dia=None, protected=None,
                               variantInfo=None, variantInfoL=None):
        """ Create variant for ABAP program

        :param abapProgramName: str Program name
        :param abapVariantName: str variant name
        :param abapVariantText: str desciption for variant
        :param dia: batch or dialog?
        :param protected:
        :param extUserName: external xmi username
        :param variantInfo: actual data of the variant
        :param variantInfoL: data of the variant with longnr parameters
        :return:

        variantInfo and variantInfoL are internal tables that need to be specified as a list of dictionaries.
        each row consisting of these fields:

        REPORT  Report Name
        VARIANT Variant Name
        PNAME   ABAP/4: Name of SELECT-OPTION / PARAMETER
        PKIND   ABAP: Type of selection
        POLEN   ABAP: Output length of selection condition
        PTEXT   CHAR30 for SYST
        PSIGN   ABAP: ID: I/E (include/exclude values)
        POPTION ABAP: Selection option (EQ/BT/CP/...)
        PLOW    Selection variants: Field content (LOW/HIGH)
        PHIGH   Selection variants: Field content (LOW/HIGH)

        """

        result = self.btc_xmi_logon()
        if result.fail:
            self.logger.debug('logon to XBP interface failed {:s}/{:s}'.format(self.XBP_EXT_COMPANY,
                                                                               self.XBP_EXT_PRODUCT))
            return result

        self.logger.debug('logon to XBP interface successful')

#        result = self.btc_xbp_variant_info_get(self, abapProgramName)
#        if not result.fail:
#            variants=[record['VARIANT'] for record in result.data.get('ABAP_VARIANT_TABLE')]
#            if abapVariantName in variants:



        fmParameters = dict()
        fmParameters['ABAP_PROGRAM_NAME'] = abapProgramName
        fmParameters['ABAP_VARIANT_NAME'] = abapVariantName
        fmParameters['ABAP_VARIANT_TEXT'] = abapVariantText

        if dia:
            fmParameters['DIA'] = dia

        if protected:
            fmParameters['DIA'] = protected

        if variantInfoL:
            fmParameters['VARIANT_INFO_L'] = variantInfoL
        elif variantInfo:
            fmParameters['VARIANT_INFO'] = variantInfo
        else:
            return Fail('Missing Variant Information')
        result = self.call_fm('BAPI_XBP_VARIANT_CREATE', **fmParameters)
        if result.fail:
            return result

        if result.data['RETURN']['TYPE'] == 'E':
            return Fail(message=result.data['RETURN']['MESSAGE'])
        else:
            return Result('Variant Created')

    def btc_xbp_variant_delete(self, abapProgramName:str, abapVariantName:str):
        """ Delete variant for ABAP program

        :param abapProgramName: Program name
        :param abapVariantName: variant name
        :return:

        """

        result = self.btc_xmi_logon()
        if result.fail:
            self.logger.debug('logon to XBP interface failed {:s}/{:s}'.format(self.XBP_EXT_COMPANY,
                                                                               self.XBP_EXT_PRODUCT))
            return result

        self.logger.debug('logon to XBP interface successful')

        #        result = self.btc_xbp_variant_info_get(self, abapProgramName)
        #        if not result.fail:
        #            variants=[record['VARIANT'] for record in result.data.get('ABAP_VARIANT_TABLE')]
        #            if abapVariantName in variants:



        fmParameters = dict()
        fmParameters['ABAP_PROGRAM_NAME'] = abapProgramName
        fmParameters['ABAP_VARIANT_NAME'] = abapVariantName
        fmParameters['EXTERNAM_USER_NAME']= self.XBP_EXT_USER

        result = self.call_fm('BAPI_XBP_VARIANT_DELETE', **fmParameters)
        if result.fail:
            return result

        if result.data['RETURN']['TYPE'] == 'E':
            return Fail(message=result.data['RETURN']['MESSAGE'])
        else:
            return Result('Variant Deleted')

    def btc_xbp_variant_info_get(self, abapProgramName, moreInfo:bool=False, variantSelectionOption='A'):
        """ Get information about specific program variant.

        :param abapProgramName: str name of the ABAP program
        :param variantSelectionOption: 'A' means get all variants, 'B' means only get batch variants.
        :param moreInfo:
        :param extUserName: external user name.
        :return:
        """

        result = self.btc_xmi_logon()
        if result.fail:
            self.logger.debug('logon to XBP interface failed {:s}/{:s}'.format(self.XBP_EXT_COMPANY,
                                                                               self.XBP_EXT_PRODUCT))
            return result

        self.logger.debug('logon to XBP interface successful')

        fmParameters = dict(ABAP_PROGRAM_NAME=abapProgramName,
                            EXTERNAL_USER_NAME=self.XBP_EXT_USER)

        if variantSelectionOption in ['A', 'B']:
            fmParameters['VARIANT_SELECT_OPTION'] = variantSelectionOption

        if moreInfo:
            fmParameters['MORE_INFO'] = 'X'

        result = self.call_fm('BAPI_XBP_VARIANT_INFO_GET', **fmParameters)

        if result.data['RETURN']['TYPE']=='E':
            return Fail(result.data['RETURN']['MESSAGE'])

        return result

    def btc_xmi_logoff(self):
        """ Perform BAPI XMI Log Off

        OSS Notes:
            1770388 - Enhancements in the XBP interface

        :return:Fail(error Message
        """
        self.logger.debug('starting BAPI_XMI_LOGOFF')
        result = self.call_fm('BAPI_XMI_LOGOFF', INTERFACE='XBP')

        if result.fail:
            return result

        result=result.data
        if result['RETURN']['TYPE'] == 'E':
            if result['RETURN']['NUMBER'] != '028':
                logMessage = 'BAPI_XMI_LOGOFF: {:s}'.format(result['RETURN']['MESSAGE'])
                self.logger.error(logMessage)
                return Fail(message=logMessage)
            else:
                self.logger.debug('user was not logged on to interface')
                return Result(data=True)
        else:
            self.logger.debug('BAPI_XMI_LOGOFF successful')
            return Result(data=True)

    def btc_xmi_logon(self, interface:str='XBP'):
        """Starting BAPI XMI logon process

        OSS Notes:
            1770388 - Enhancements in the XBP interface

        :param externalCompany: Name of the external company
        :param externalProduct: Name of the external product
        :param interface: Interface to logon to
        :param version: Version of the interface
        :return: Fail(error Message) or Result(True)
        """

        self.logger.debug('starting BAPI_XMI_LOGON')
        result = self.call_fm('BAPI_XMI_LOGON', EXTCOMPANY=self.XBP_EXT_COMPANY,
                           EXTPRODUCT=self.XBP_EXT_PRODUCT,
                           INTERFACE=interface,
                           VERSION=self.XPB_INTERFACE_VERS)

        if result.fail:
            return result

        result=result.data

        if result['RETURN']['TYPE'] == 'E' and result['RETURN']['MESSAGE'] != 'Tool already logged on in interface XBP':
            logMessage = 'BAPI_XMI_LOGON: {:s}'.format(result['RETURN']['MESSAGE'])
            sid = self.sid()
            client = self.conn.get_connection_attributes().get('client')

            self.logger.error('%s Client %s: %s', sid, client, logMessage)
            return Fail(message=logMessage)
        else:
            self.logger.debug('BAPI_XMI_LOGON successful')
            result=Result(data=True)
            return result

    def call_fm(self, fm: str, **kwargs) -> Union[Result, Fail]:
        """ Call Function Module with Exception Handling"""
        self.logger.debug('Executing Function Module {}'.format(fm))

        try:
            data = self.conn.call(fm, **kwargs)
        except Exception as err:
            return(self._handle_exception(err))
        return Result(message='call to {} successful'.format(fm), data=data)

    @property
    def clients(self) -> Union[Result, Fail]:
        result = self.download_table('T000', tab_fields=['MANDT', 'MTEXT'])
        return result

    def close(self):
        """ Close the ABAP Connection """
        self.conn.close()

    def component(self, component:str)-> Result:
        """ Check whether a component is installed and retrieve the versions


        :param component: the name of the component
        """

        where_clause="COMPONENT EQ '{}'".format(component.upper())

        result=self.download_table('CVERS', where_clause=where_clause, tab_fields=['COMPONENT'])
        if result.fail:
            return result

        data=result.data.get('data')
        if len(data):
            return Result(data=data[0])
        else:
            return Result(data=[])

    def dbtype(self):
        """ Find the DB type """
        result=self.conn.call('RFC_SYSTEM_INFO')
        return result['RFCSI_EXPORT']['RFCDBSYS']

    def download_table(self, tabname: str, where_clause: str = None, tab_fields: list = None,
                       fetchsize: int = 1000) -> Union[Result, Fail]:
        '''Downloads a Table

        .. warning::

           This can be memory intensive and is also restricted to a line length of 512 characters,

        :param where_clause: Where clause to restrict result set in ABAP syntax
        :param tab_fields: list of fields
        :param fetchsize: number of records to retrieve
        :param tabname: Table name

        :return: Result(data={data: <list of dictionaries>, headers: <list of headers>}) or Fail(message=message)

        '''

        # TODO: Make more memory efficient
        # TODO: download records larger than 512 characters

        from pprint import pformat

        self.logger.debug('trying to download table ' + tabname)

        # Configure function module call
        fm_params = dict(QUERY_TABLE=tabname,
                         DELIMITER='|')

        if where_clause:
            n = 72  # max. length of one where clause input value.
            fm_params['OPTIONS'] = [{'TEXT': where_clause[i:i + n]} for i in range(0, len(where_clause), n)]

        if tab_fields:
            fm_params['FIELDS'] = [{'FIELDNAME': x} for x in tab_fields]
            self.logger.debug('specified table fields: {:s}'.format(pformat(fm_params['FIELDS'])))

        fm_params['ROWCOUNT'] = fetchsize

        self.logger.debug('RFC_READ_TABLE parameters: {:s}'.format(pformat(fm_params)))

        result = self.call_fm('RFC_READ_TABLE', NO_DATA='X', **fm_params)
        if result.fail:
            return result

        fm_tbl_fields = result.data['FIELDS']  # this will contain the table definition including field length.

        fm_tbl_headers = [x['FIELDNAME'] for x in fm_tbl_fields]
        record_size = sum([int(x['LENGTH']) for x in fm_tbl_fields])
        self.logger.debug('Record Size: {:d}'.format(record_size))

        if record_size > 512:
            message = 'requested column length of {:d} is larger than maximum possible (512)'.format(record_size)
            self.logger.error(message)
            return Fail(message=message, data=fm_tbl_fields)

        iteration = 0
        recordcounter = 1

        table_data = []

        while recordcounter > 0:
            self.logger.debug(
                'starting function module RFC_READ_TABLE with data retrieval. Iteration: {:d}'.format(iteration))
            rowskips = iteration * fetchsize
            fm_params['ROWSKIPS'] = rowskips
            result = self.call_fm('RFC_READ_TABLE', **fm_params)
            if result.fail:
                return result

            data = result.data['DATA']
            if len(data) > 0:
                self.logger.debug(
                    'generating result set from returned records. fetchsize={:d}, iteration={:d}'.format(fetchsize,
                                                                                                         iteration))
                for row in data:
                    splitRow = row['WA'].strip().split('|')
                    splitRow = [x.strip() for x in splitRow]
                    record = dict(zip(fm_tbl_headers, splitRow))
                    table_data.append(record)
            else:
                recordcounter = 0
                if iteration == 0:
                    return Result(data={'data': [], 'headers': fm_tbl_headers})
            iteration += 1
        else:
            return Result(data={'data': table_data, 'headers': fm_tbl_headers})

    def fm_interface(self, fm):
        result = self.call_fm('RFC_GET_FUNCTION_INTERFACE', FUNCNAME=fm, LANGUAGE='EN')
        return result

    def get_runtime_parameter(self, parameter):

        """ Get the value of the specified profile parameter
        :param configParameter: profile parameter to query
        :return: Result({value:... , name:parameter}) or Fail(message)
        """

        result = self.call_fm('SXPG_PROFILE_PARAMETER_GET', PARAMETER_NAME=parameter)

        if result.fail:
            return result

        response=result.data

        if response['RET']!=0:
            return Fail('Error Retrieving Value of {}'.format(parameter))


        return Result(data={'value': response['PARAMETER_VALUE'], 'name': parameter})

    @property
    def instances(self) -> Union[Result, Fail]:
        """ Returns the names of the instances as list"""
        fm_result = self.call_fm('TH_SERVER_LIST')
        if fm_result.fail:
            return fm_result

        result = [instance['NAME'] for instance in fm_result.data['LIST']]

        return Result(data=result)

    def logon(self, logon_info:dict, mock:bool=False, mockdata:dict=False)->Union[Result, Fail]:
        """ Logon to the specified system

        :param logon_info: Information required to logon to a system
        :param mock: If True, then no real pyRFC conection will be established. This is for testing.
        :param moockdata: Data that should be used for the mock testing

        """

        if logon_info is False:
            return Fail(message='Logon Info Incomplete')

        self.mock = mock
        self.logger = logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))
        result = Result(message='Connection Successful')
        if mock:
            try:
                self.conn = MockConnection(mockdata=mockdata)
            except Exception as err:
                return Fail('Mock Connection Setup Failed')
        else:
            try:
                self.logger.debug('Logon Details: %s', pformat(logon_info))
                self.conn = pyrfc.Connection(**logon_info)
            except Exception as err:
                result = self._handle_exception(err)
        return result


    def sid(self):
        result=self.conn.call('RFC_SYSTEM_INFO')
        return result['RFCSI_EXPORT']['RFCSYSID']

    @property
    def systemtime(self):
        """ Get System Timezone

        The function calls function module TH_GET_START_TIME2. A sample execution is documented below. START_TIME is
        the number of seconds since 01.01.1970 (epoch). Uptime is specified in seconds.

        TS_GMTIME is the start time in UTC, TS_LOCALTIME is the start time in the local time zone of the server.


        --------------------------------------------------------------------------------
        | Export parameters              |Value                                        |
        --------------------------------------------------------------------------------
        | START_TIME                     |1484444152                                   |
        | START_TIME_STR                 |Sun Jan 15 01:35:52 2017                     |
        | UPTIME                         |1,157                                        |
        | TS_GMTIME                      |20170115013552                               |
        | TS_LOCALTIME                   |20170115013552                               |
        --------------------------------------------------------------------------------



        """
        self.logger.debug('retrieving system time')
        result=self.call_fm('TH_GET_START_TIME2')
        if result.fail:
            self.logger.debug('Failed to retrieve system time: %s', result.message)
            return result
        uptime=int(result.data['UPTIME'])
        starttime=int(result.data['START_TIME'])
        localstarttime=datetime.datetime.strptime(result.data['TS_LOCALTIME'],'%Y%m%d%H%M%S')
        localtime=localstarttime + datetime.timedelta(seconds=uptime)
        utcstarttime=datetime.datetime.strptime(result.data['TS_GMTIME'],'%Y%m%d%H%M%S')
        utctime=localstarttime + datetime.timedelta(seconds=uptime)

        result=dict(uptime = uptime,
                    starttime = starttime,
                    localtime = localtime,
                    localstarttime = localstarttime,
                    utctime=utctime,
                    utcstarttime=utcstarttime)
        self.logger.debug('System Times: %s', pformat(result))
        return Result(data=result)

    @property
    def connection_attributes(self):
        return self.conn.get_connection_attributes()

    def user_change_own_password(self, password: str, set_prod_password: bool = True) -> Union[Result, Fail]:
        """ Change the password of the current user

        :param: password: The new password
        :param: set_prod_password: This flag marks the password as productive. That means, you won't get asked to change
                during the next logon

        :return Result() if successful or Fail() if failed.

        There are times, where you may want to logon using your username and password. But in particular when using SSO,
        you may not remember it. Logging into many systems to change your password is also tedious. This function will
        change your own password for you. """

        params = dict(PASSWORD={'BAPIPWD': password}, PASSWORDX={'BAPIPWD': 'X'}, USERNAME=self.current_username)
        if set_prod_password:
            params['PRODUCTIVE_PWD'] = 'X'

        result = self.call_bapi('BAPI_USER_CHANGE', **params)
        return result

    def user_profiles_assign(self, username: str, profiles: list, replace=True) -> Union[Result, Fail]:
        """Assign Profiles to a User

        :param: username: Name of the user
        :param: profiles: List of profiles
        :param: replace: If True, the list provided in profiles will completely replace the existing assignment.
                         Otherwise the list will be added to the existing profile assignments. """
        # TODO: implement the replace option to allow adding of a single profile instead of replacing all assigned profiles
        self.logger.info('Assigning profiles {} to user {}'.format(pformat(profiles), username))

        if replace:
            params = dict(USERNAME=username, PROFILES=profiles)
        result = self.call_bapi('BAPI_USER_PROFILES_ASSIGN', **params)

        if result.fail:
            self.logger.error('Profile Assignment Failed: ' + result.fail)

        return result


def get_connection(logon_info:dict)->Union[Result, Fail]:
    """ Establish a connection to an ABAP System


    """

    connection = Connection()
    result = connection.logon(logon_info)
    if not result.fail:
        result=Result(message='Logon Successful', data=connection)
    return result