import pyrfc
from systemcheck import CONFIG
from typing import Union
from systemcheck.utils import Result, Fail
import time
import datetime
from pprint import pformat
import logging

class Connection(pyrfc.Connection):
    """ Customized PyRFC Connection Class"""

    XBP_EXT_PRODUCT = CONFIG['systemtype_abap']['xbpinterface.XBP_EXT_PRODUCT']
    XBP_EXT_COMPANY = CONFIG['systemtype_abap']['xbpinterface.XBP_EXT_COMPANY']
    XBP_EXT_USER = CONFIG['systemtype_abap']['xbpinterface.XBP_EXT_PRODUCT']
    XPB_INTERFACE_VERS = CONFIG['systemtype_abap']['xbpinterface.XBP_EXT_PRODUCT']

    XBP_PARAMS=dict(EXTCOMPANY=XBP_EXT_COMPANY,
                    EXTPRODUCT=XBP_EXT_PRODUCT,
                    INTERFACE='XBP',
                    VERSION=XPB_INTERFACE_VERS)

    logger=logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):

        try:
            super().__init__(*args, **kwargs)
        except Exception as err:
            raise err

        self.logger = logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))

    @property
    def z_instances(self)->list:
        """ Returns the names of the instances as list"""
        server_list = self.call('TH_SERVER_LIST')
        return [instance['NAME'] for instance in server_list['LIST']]

    @property
    def z_clients(self)->list:
        result=self.z_download_sap_table('T000', tab_fields=['MANDT', 'MTEXT'])
        if not result.fail:
            return result.result['data']

    def z_change_own_password(self, password: str, setProductivePassword=True)->Union[Result, Fail]:
        """ Change the password of the current user
        Execute function module BAPI_USER_CHANGE to change the password
        No verification whether the communication channels is encrypted """

        params=dict(PASSWORD={'BAPIPWD':password}, PASSWORDX={'BAPIPWD':'X'}, USERNAME=self.z_current_username)
        if setProductivePassword:
            params['PRODUCTIVE_PWD']='X'

        result=self.z_call('BAPI_USER_CHANGE', **params)
        return result

    def z_user_profiles_assign(self, username: str, profiles: list, replace=True)->Union[Result, Fail]:
        #TODO: implement the replace option to allow adding of a single profile instead of replacing all assigned profiles
        self.logger.info('Assigning profiles {} to user {}'.format(pformat(profiles), username))

        params=dict(USERNAME=username, PROFILES=profiles)
        result=self.z_call_bapi('BAPI_USER_PROFILES_ASSIGN', **params)

        if result.fail:
            self.logger.error('Profile Assignment Failed: ' + result.fail)

        return result

    def z_user_profiles_remove(self, username:str, profile_name:str)->Union[Result, Fail]:
        """ Remove a single profile from user """
        result=self.z_call_bapi('BAPI_USER_GET_DETAIL', USERNAME=username)
        if result.fail:
            return result

        data=result.data

        profiles=list([item['BAPIPROF'] for item in data['PROFILES']])
        self.logger.debug('retrieved user profiles: ' + pformat(profiles))
        if profile_name in profiles:
            profiles.remove(profile_name)
            result=self.z_user_profiles_assign(username, profiles)
        return result

    def z_user_roles_assign(self, username:str, role_name:str)->Union[Result, Fail]:
        raise NotImplemented

    def z_user_roles_remove(self, username, role_name)->Union[Result, Fail]:
        raise NotImplemented

    def z_user_create(self, **kwargs)->Union[Result, Fail]:
        """ Create a New User with SAP_ALL Profile
        Execute function module SUSR_USER_PASSWORD_PUT to change the password
        No verification whether the communication channels is encrypted at the moment

        :param userParams: Dictionary corrosponding to FM BAPI_USER_CREATE.


        The following dictionary will create a user with SNC name and password:

        userParams=dict(USERNAME='TESTUSER',
                        LOGONDATA={'USTYP':'A'},
                        PASSWORD={'BAPIPWD':'SuperSecret'},
                        SNC={'GUIFLAG':'X', 'PNAME':'p:CN=TESTUSER@REALM'}


        """

#        for key, value in kwargs.items():
#            params[key]=value


        result=self.z_call_bapi('BAPI_USER_CREATE', **kwargs)

        if not result.fail:
            result=self.z_user_profiles_assign(username=kwargs['USERNAME'], profiles=['SAP_ALL', 'SAP_NEW'])

        return result

    def z_user_get_details(self, username:str, cache_results:str=True)->Union[Result, Fail]:
        self.logger.info('Getting Details for User ' + username)

        params=dict(USERNAME=username)

        if cache_results:
            params['CACHE_RESULTS']='X'
        else:
            params['CACHE_RESULTS'] = ' '

        result=self.z_call_bapi('BAPI_USER_GET_DETAIL', **params)
        if result.fail:
            self.logger.error("Unable to get User Details: " + result.fail)
        else:
            self.logger.debug("retrieved results: " + pformat(result.result))

        return result

    @property
    def z_current_instance_name(self)->Union[Result, Fail]:
        try:
            rfc_system_info=self.call('RFC_SYSTEM_INFO')
        except Exception as err:
            return Fail(message=pformat(err))
        return Result(data=rfc_system_info['RFCSI_EXPORT']['RFCDEST'], message=rfc_system_info)

    @property
    def z_current_username(self)->Union[Result, Fail]:
        try:
            connectionAttributes=self.get_connection_attributes()
        except Exception as err:
            return Fail(message=pformat(err))

        return Result(data=connectionAttributes['user'])

    def z_job_schedule_immediately(self, jobname:str, program:str, variant:str=None, wait_for_completion:bool=True, spoolparams:dict=None,
                                   return_spool:bool=False)->Union[Result, Fail]:
        """
        Schedules a job in SAP with immediate start using the XBP interface. The process is like follows:
            - zBapiXmiLogon(BAPI_XMI_LOGON): logon to the external batch management system
            - zBapiXboJobOpen(BAPI_XBP_JOB_OPEN): Create a new job
            - zBapiXbpJobAddAbapStep(BAPI_XBP_JOB_ADD_ABAP_STEP): Add a ABAP job step
            - zBapiXbpJobClose(BAPI_XBP_JOB_CLOSE): Close the job definition. The job is now in status Scheduled
            - zBapiXbpJobstartImmediately(BAPI_XBP_JOB_START_IMMEDIATELY): Start the job immediately

        :param jobname: Name of the SAP Job
        :param program: ABAP Program Name
        :param variant: the variant that should be used to execute the report
        :param wait_for_completion: wait until job completes.
        :param spoolparams: Parameters describing the spool output. Check XBP documentation
        :return:
        """

        self.logger.info('scheduling batch job {:s} with program {:s}'.format(jobname, program))

        result=self.z_bapi_xmi_logon()

        if result.fail:
            return result

        self.logger.debug('logon to XBP interface successful')
        result=self.z_bapi_xbp_job_open(jobname)
        if result.fail:
            self.logger.debug('Job open Failed')
            return result

        jobcount=result.data

        self.logger.debug('Job open successful: jobcount for job {:s} is {:s}'.format(jobname, jobcount))

        result=self.z_bapi_xbp_add_job_step(jobname, jobcount, program, variant=variant)
        if result.fail:
            self.logger.error('Adding Job Step Failed for job {:s} ({:s})'.format(jobname, jobcount))
            return result

        self.logger.debug('Adding Job Step succeeded for job {:s} ({:s})'.format(jobname, jobcount))
        result=self.z_bapi_xbp_job_close(jobname, jobcount)
        if result.fail:
            self.logger.error('Closing job definition failed for job {:s} ({:s})'.format(jobname, jobcount))
            return result

        result=self.z_bapi_xbp_job_start_immediately(jobname, jobcount)
        if result.fail:
            self.logger.error('starting job {:s} ({:s}) immediately failed'.format(jobname, jobcount))
            return result

        self.logger.debug('job {:s} ({:s}) started immediately'.format(jobname, jobcount))

        if wait_for_completion:
            self.logger.debug('wating for job {:s} ({:s}) to complete'.format(jobname, jobcount))
            result=self._z_delay_until_job_completes(jobname, jobcount, self.XBP_EXT_PRODUCT)
            if result.fail:
                self.logger.error('job {:s} ({:s}) failed'.format(jobname, jobcount))
                return result

        self.logger.info('job {} finished successfully'.format(jobname))
        jobDefinition=self.z_bapi_xbp_job_definition_get(jobname, jobcount)

        if not jobDefinition.fail:
            return Result ({'data':jobDefinition.result})

    def z_parameter_current_value(self, config_parameter):
        """ Get the value of the specified profile parameter
        :param config_parameter: profile parameter to query
        :return: Result({value:... , name:parameter}) or Fail(message)
        """

        result=self.z_call_fm('SXPG_PROFILE_PARAMETER_GET', PARAMETER_NAME=config_parameter)

        if result.fail:
            return result

        returncode=result.data.get('RET')
        if returncode!=0:
            return Fail(message='Return Code != 0')

        return Result(data={'value' : result.data['PARAMETER_VALUE'],
                       'name' : config_parameter})

    def z_fm_import_interface(self, funcname, inactive_version=' ', with_enhancements='X', ignore_switches=' '):
        """
        Retrieve the import interface of a function module

        :param funcname: Name of the function module
        :param inactive_version: Read the inactive version of the function module.
        :param with_enhancements: Value 'X': Enhancement Parameters will be provided
        :param ignore_switches: Value 'X': Switches are ignored

        """

        result = self.z_call_fm('FUNCTION_IMPORT_INTERFACE', FUNCNAME=funcname, INACTIVE_VERSION=inactive_version,
                           WITH_ENHANCEMENTS=with_enhancements, IGNORE_SWITCHES=ignore_switches)

        return result

    def z_structure_info(self, **kwargs):
        result=self.z_call('DDIF_FIELDINFO_GET', **kwargs)
        return result

    @property
    def z_system_time(self)->Union(Result, Fail):
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

        result=self.z_call_fm('TH_GET_START_TIME2')
        if result.fail:
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

        return Result(data=result)

    def z_variant_exists(self, program, variant):
        """ Checks whether variant exists
        :param program: Name of the program
        :param variant: Variant name
        :return: True if variant exists, otherwise False
        """

        self.logger.debug('checking existence of variant {:s} for program {:s}'.format(variant, program))

        result=self.z_bapi_xbp_variant_info_get(abap_program_name=program)

        if result.fail:
            return result

        variantInfo=result.data

        variantNames=[record['VARIANT'] for record in variantInfo['ABAP_VARIANT_TABLE']]

        if variant in variantNames:
            return Result(data=True)
        else:
            return Result(data=False)

    def z_download_sap_table(self,
                             tabname:str,
                             where_clause:str=None,
                             tab_fields:list=None,
                             fetchsize:int=1000)->Union[Result, Fail]:
        '''Downloads an SAP table and returns the results as list of dictionaries.

        This can be very memory intensive!!!

        :param where_clause: Where clause to restrict result set in ABAP syntax
        :param tab_fields: list of fields
        :param fetchsize: number of records to retrieve
        :param tabname: Table name

        :return: Result(data={data: <list of dictionaries>, headers: <list of headers>}) or Fail(message)

        '''

        from pprint import pformat

        self.logger.debug('trying to download table '+tabname)


        #Configure function module call
        fm_params = dict(QUERY_TABLE = tabname,
                          DELIMITER='|')

        if where_clause:
            n = 72                    # max. length of one where clause input value.
            fm_params['OPTIONS']=[{'TEXT': where_clause[i:i + n]} for i in range(0, len(where_clause), n)]


        if tab_fields:
            fm_params['FIELDS'] = [{'FIELDNAME' : x} for x in tab_fields]
            self.logger.debug('specified table fields: {:s}'.format(pformat(fm_params['FIELDS'])))

        fm_params['ROWCOUNT'] = fetchsize

        self.logger.debug('RFC_READ_TABLE parameters: {:s}'.format(pformat(fm_params)))

        result = self.z_call_fm('RFC_READ_TABLE', NO_DATA='X', **fm_params)
        if result.fail:
            return result

        fm_tbl_fields = result.data['FIELDS']   #this will contain the table definition including field length.

        fm_tbl_headers = [x['FIELDNAME'] for x in fm_tbl_fields]
        record_size = sum([int(x['LENGTH']) for x in fm_tbl_fields])
        self.logger.debug('Record Size: {:d}'.format(record_size))

        if record_size > 512:
            message='requested column length of {:d} is larger than maximum possible (512)'.format(record_size)
            self.logger.error(message)
            return Fail(message=message, data=fm_tbl_fields)

        iteration=0
        recordcounter=1

        table_data=[]

        while recordcounter > 0:
            self.logger.debug('starting function module RFC_READ_TABLE with data retrieval. Iteration: {:d}'.format(iteration))
            rowskips=iteration*fetchsize
            fm_params['ROWSKIPS']=rowskips
            result = self.z_call_fm('RFC_READ_TABLE', **fm_params)
            if result.fail:
                return result

            data = result.data['DATA']
            if len(data) > 0:
                self.logger.debug('generating result set from returned records. fetchsize={:d}, iteration={:d}'.format(fetchsize, iteration))
                for row in data:
                    splitRow=row['WA'].strip().split('|')
                    splitRow=[x.strip() for x in splitRow]
                    record=dict(zip(fm_tbl_headers, splitRow))
                    table_data.append(record)
            else:
                recordcounter = 0
                if iteration == 0:
                    return Result(data={'data' : [], 'headers' : fm_tbl_headers})
            iteration += 1
        else:
            return Result(data={'data' : table_data, 'headers': fm_tbl_headers})

    def _z_delay_until_job_completes(self, jobname, jobcount, use_fm=True, sleep_time=3, max_delay=600):
        """
        Checks whether a job is still running and waits until it completes.

        The job status is encoded using the characters below.

        'R' - active
        'I' - intercepted
        'Y' - ready
        'P' - scheduled
        'S' - released
        'A' - cancelled
        'F' - finished

        OSS Notes:
            1770388 - Enhancements in the XBP interface


        :param externalUserName: External username for Scheduling
        :param jobname: SAP Job Name
        :param jobcount: Job Counter
        :param use_fm: If True, use function module SUBST_CHECK_BATCHJOB. Otherwise query TBTCO.
        :param sleep_time: check interval in seconds
        :param max_delay: maximum time to wait for job to complete.
        """

        jobstatus = 'X'

        t0 = time.clock()

        while time.clock()-t0 < max_delay:
            if use_fm:
                self.logger.debug('waiting until batch job {:s} ({:s}) completes using '
                                  'BAPI_XBP_JOB_STATUS_GET'.format(jobname, jobcount))
                result=self.z_call_bapi('BAPI_XBP_JOB_STATUS_GET', jobname=jobname, jobcount=jobcount,
                                   EXTERNAL_USER_NAME=self.XBP_EXT_USER)
                if result.fail:
                    log_message='BAPI_XBP_JOB_STATUS_GET for job request {:s} ({:s}): {:s}'.format(jobname, jobcount, result.message)
                    self.logger.error(log_message)
                    return Fail(log_message)
                else:
                    status=result.data['STATUS']
            else:
                self.logger.debug('waiting until batch job {:s} ({:s}) completes using '
                                  'RFC_READ_TABLE and TBTCO'.format(jobname, jobcount))
                where_clause="jobname EQ '%s' AND jobcount EQ '%s'" % (jobname, jobcount)
                result=self.z_download_sap_table('TBTCO', where_clause=where_clause, tab_fields=['STATUS'])
                if not result.fail:
                    status=result.data['data'][0]['STATUS']
                else:
                    return Fail(message='unable to download table TBTCO', data=result.data)

            if status != 'R':
                if status=='P':
                    self.logger.debug('Error: job {:s} ({:s}) is not released'.format(jobname, jobcount))
                    return Fail(message='Job {:s} ({:s}) has not been released')
                elif status=='A':
                    self.logger.debug('Error: job {:s} ({:s}) failed'.format(jobname, jobcount))
                    return Fail(message='Job {:s} ({:s}) failed')
                elif status=='F':
                    self.logger.debug('Success: job {:s} ({:s}) completed'.format(jobname, jobcount))
                    return Result(message=True)
                elif status=='S':
                    self.logger.debug('Warning: job {:s} ({:s}) in status "RELEASED" '
                                      '(missing btc processes?)'.format(jobname, jobcount))
                elif status=='Y':
                    self.logger.debug('Warning: job {:s} ({:s}) in status "READY" '
                                      '(missing btc processes?)'.format(jobname, jobcount))
                elif status=='I':
                    self.logger.debug('Warning: job {:s} ({:s}) in status "INTERCEPTED"'.format(jobname, jobcount))
            else:
                self.logger.debug('job {:s} ({:s}) running since {:6.2f} seconds'.format(jobname, jobcount,
                                                                                          time.clock()-t0))
            time.sleep(sleep_time)
        return Fail(message='Max. Job Runtime {:i} Reached. Runtime: {:6.2f}'.format(sleep_time, time.time() - t0))

    def z_bapi_xmi_logoff(self)->Union[Result, Fail]:
        """ Perform BAPI XMI Log Off

        OSS Notes:
            1770388 - Enhancements in the XBP interface

        :return:Fail(error Message
        """

        self.logger.debug('starting BAPI_XMI_LOGOFF')
        result = self.z_call_bapi('BAPI_XMI_LOGOFF', INTERFACE='XBP')

        if result.fail:
            if result.data['RETURN']['NUMBER'] != '028':
                logMessage='BAPI_XMI_LOGOFF: {:s}'.format(result.data['RETURN']['MESSAGE'])
                self.logger.error(logMessage)
                return result
            else:
                self.logger.debug('user was not logged on to interface')
                return Result(data=True)
        else:
            self.logger.debug('BAPI_XMI_LOGOFF successful')
            return Result(data=True)

    def z_bapi_xmi_logon(self)->Union[Result, Fail]:
        """Starting BAPI XBP logon process

        OSS Notes:
            1770388 - Enhancements in the XBP interface

        :param ext_company: Name of the external company
        :param ext_product: Name of the external product
        :param interface: Interface to logon to
        :param version: Version of the interface
        :return: Fail(error Message) or Result(True)
        """

        self.logger.debug('starting BAPI_XMI_LOGON')
        result = self.z_call_bapi('BAPI_XMI_LOGON', EXTCOMPANY=self.XBP_EXT_COMPANY, EXTPRODUCT=self.XBP_EXT_PRODUCT,
                                  INTERFACE='XBP', VERSION=self.XPB_INTERFACE_VERS)

        if result.fail and result.message != 'Tool already logged on in interface XBP':
            log_message = '{}:{} - BAPI_XMI_LOGON: {}'.format(self.get_connection_attributes()['sysId'],
                                                             self.get_connection_attributes()['client'],
                                                             result.message)
            self.logger.error(log_message)
            return result
        else:
            self.logger.debug('BAPI_XMI_LOGON successful')
            return Result()

    def z_bapi_xbp_add_job_step(self, jobname:str, jobcount:str, program:str, variant:str=None,
                                spool_params:dict=None)->Union[Result, Fail]:
        """ Add Step to the Job

        OSS Notes:
            1770388 - Enhancements in the XBP interface

        :param jobname: Name of the background job
        :param jobcount: Unique job count number for the background job
        :param program: ABAP Program Name
        :param variant: Name of the Variant
        :param spool_params: Spool Parameters
        :return: Result(True) if the message succeeds Fail(Message) if step fails.
        """
        bapi_options=dict(JOBNAME=jobname,
                       JOBCOUNT=jobcount,
                       EXTERNAL_USER_NAME=self.XBP_EXT_USER,
                       ABAP_PROGRAM_NAME=program)

        if variant:
            bapi_options['ABAP_VARIANT_NAME']=variant

        if spool_params:
            bapi_options['ALLPRIPAR']=spool_params

        result = self.z_call_bapi('BAPI_XBP_JOB_ADD_ABAP_STEP', **bapi_options)

        if result.fail:
            self.logger.error('BAPI_XBP_JOB_ADD_ABAP_STEP:' + result.message)
            return result
        else:
            self.logger.debug('BAPI_XBP_JOB_ADD_ABAP_STEP successful')
            return result

    def z_bapi_xbp_add_ext_step(self,
                                jobname:str,
                                jobcount:str,
                                ext_program_name:str,
                                ext_program_parameters:str,
                                sap_user_name:str,
                                ext_user_name=None,
                                destination_host:str=None)->Union[Result, Fail]:
        """ Add external program as Step to the Job

        OSS Notes:
            1770388 - Enhancements in the XBP interface

        :param ext_program_name: Name of the external program
        :param ext_program_parameters: Parameters for the external program
        :param sap_user_name: SAP Username
        :param jobname: Name of the background job
        :param jobcount: Unique job count number for the background job
        :param ext_user_name: Username that was used for the XMI logon
        :param program: ABAP Program Name
        :return: Result(True) if the message succeeds Fail(Message) if step fails.
        """
        fm_options=dict(jobname=jobname,
                       jobcount=jobcount,
                       EXTERNAL_USER_NAME=ext_user_name,
                       EXT_PROGRAM_NAME=ext_program_name,
                       EXT_PROGRAM_PARAMETERS=ext_program_parameters,
                       SAP_USER_NAME=sap_user_name)

        if destination_host is None:
            attributes=self.get_connection_attributes()
            fm_options['TARGET_HOST']=attributes['partnerHost']
        else:
            fm_options['TARGET_HOST']=destination_host

        self.logger.debug('calling function module BAPI_XBP_JOB_ADD_EXT_STEP with parameters {:s}'.format(pformat(fm_options)))
        result = self.z_call_bapi('BAPI_XBP_JOB_ADD_EXT_STEP', **fm_options)

        if result.fail:
            self.logger.error('BAPI_XBP_JOB_ADD_EXT_STEP:' + result.message)
            return result
        else:
            self.logger.debug('BAPI_XBP_JOB_ADD_EXT_STEP successful')
            return Result()

    def z_bapi_xbp_get_spool_as_dat(self,
                                    spool_request:int,
                                    firstPage:str=None,
                                    lastPage:str=None)->Union[Result, Fail]:
        """ Download spool request as .csv file

        This procedure requires function module BAPI_XBP_GET_SPOOL_AS_DAT which is delivered in the
        OSS note below:

            1515293 - Transferring spool requests as delimited tab text files

        :param spool_request: Spool Request Number
        :param extUserName: Username used by external scheduler
        :param firstPage: First page of the spool request to download
        :param lastPage: Last page of the spool request to download.
        :return: Result(data) if successful or Fail(Message) if error
        """

        self.logger.debug('starting BAPI_XBP_GET_SPOOL_AS_DAT')

        bapi_parameters=dict(SPOOL_REQUEST=int(spool_request),
                          EXTERNAL_USER_NAME=self.XBP_EXT_USER)

        if firstPage:
            bapi_parameters['FIRST_PAGE']=firstPage

        if lastPage:
            bapi_parameters['LAST_PAGE']=lastPage

        result = self.z_call_bapi('BAPI_XBP_GET_SPOOL_AS_DAT', **bapi_parameters)

        if result.fail:
            logMessage='BAPI_XBP_GET_SPOOL_AS_DAT for spool request {:s}: {:s}'.format(spool_request, result.message)
            self.logger.error(logMessage)
            return result

        self.logger.debug('BAPI_XBP_GET_SPOOL_AS_DAT successful')
        return result

    def z_bapi_xbp_job_close(self, jobname, jobcount, extUserName=None):
        """ Closes the job definition

        OSS Notes:
            1770388 - Enhancements in the XBP interface

        :param jobname: Job Name
        :param jobcount: Unique job count number for the background job
        :return: Result(True) if successful Fail(Error Message)
        """

        if not extUserName:
            extUserName=self._XBP_EXT_PRODUCT

        self.logger.debug('starting BAPI_XBP_JOB_CLOSE')
        result = self.call('BAPI_XBP_JOB_CLOSE', jobname=jobname,
                           jobcount=jobcount,
                           EXTERNAL_USER_NAME=extUserName)

        if result['RETURN']['TYPE'] == 'E':
            logMessage='BAPI_XBP_JOB_CLOSE for {:s} ({:s}: '.format(jobname, jobcount, result['RETURN']['MESSAGE'])
            self.logger.error(logMessage)
            return Fail(logMessage)
        else:
            self.logger.debug('schedule_job_immediately: BAPI_XBP_JOB_CLOSE successful')
            return Result(True)

    def z_bapi_xbp_job_definition_get(self, jobname:str, jobcount:str)->Union[Result, Fail]:
        """ Retrive the definition of a specfic job using function module BAPI_XBP_JOB_DEFINITION_GET.
        :param jobname: Name of the job
        :param jobcount: Job Nubmber
        :return:
        """

        self.logger.debug('starting BAPI_XBP_JOB_DEFINITION_GET')

        bapi_parameters=dict(jobname=jobname,
                          jobcount=jobcount,
                          EXTERNAL_USER_NAME=self.XBP_EXT_USER)

        result = self.z_call_bapi('BAPI_XBP_JOB_DEFINITION_GET', **bapi_parameters)

        if result.fail:
            message='BAPI_XBP_JOB_DEFINITION_GET for job {:s} ({:d}) failed: {:s}'.format(jobname,
                                                                                             int(jobcount),
                                                                                             result.message)
            self.logger.error(message)
            return result
        self.logger.debug('BAPI_XBP_JOB_DEFINITION_GET successful')
        return result

    def z_bapi_xbp_job_joblog_read(self, jobname:str, jobcount:str, prot_new:str=None, lines:int=None, direction=None):
        """ Read the log of the specified job.
        :param prot_new:
        :param lines:
        :param direction:
        :param jobname: Name of the job
        :param jobcount: Job Nubmber
        :param extUserName: External User name
        :return:
        """

        self.logger.debug('starting BAPI_XBP_JOB_JOBLOG_READ')

        bapi_parameters=dict(JOBNAME=jobname,
                          jobcount=jobcount,
                          EXTERNAL_USER_NAME=self.XBP_EXT_USER)

        if prot_new:
            bapi_parameters['PROT_NEW']=prot_new

        if lines:
            bapi_parameters['LINES']=lines

        if direction:
            bapi_parameters['DIRECTION']=direction

        result = self.call('BAPI_XBP_JOB_JOBLOG_READ', **bapi_parameters)

        if result.fail:
            logMessage='BAPI_XBP_JOB_JOBLOG_READ for job {:s} ({:d}) failed: {:s}'.format(jobname,
                                                                                          int(jobcount),
                                                                                          result.message)
            self.logger.error(logMessage)
            return result
        self.logger.debug('BAPI_XBP_JOB_JOBLOG_READ successful')
        return result

    def z_bapi_xbp_job_start_immediately(self, jobname:str, jobcount:str)->Union[Result, Fail]:
        """ Starts a defined job immediately

        OSS Notes:
            1770388 - Enhancements in the XBP interface

        :param jobname: Name of the Job
        :param jobcount: Unique job count number for the background job
        :return:
        """

        self.logger.debug('starting BAPI_XBP_JOB_START_IMMEDIATELY')
        result = self.z_call_bapi('BAPI_XBP_JOB_START_IMMEDIATELY', jobname=jobname,
                           jobcount=jobcount,
                           EXTERNAL_USER_NAME=self.XBP_EXT_USER)
        if result.fail:
            logMessage='BAPI_XBP_JOB_START_IMMEDIATELY for {:s} ({:s}): {:s}'.format(jobname, jobcount,
                                                                                     result.message)
            self.logger.error(logMessage)
            return result
        else:
            self.logger.debug('BAPI_XBP_JOB_START_IMMEDIATELY successful')
            return result

    def z_bapi_xbp_job_open(self, jobname:str)->Union[Result, Fail]:
        """ Perform BAPI_XBP_JOB_OPEN

        OSS Notes:
            1770388 - Enhancements in the XBP interface

        :param jobname:Name of the background job
        :return: Either Fail(True) or Result(jobcount)
        """
        result = self.z_call_bapi('BAPI_XBP_JOB_OPEN', jobname=jobname,
                                  EXTERNAL_USER_NAME=self.XBP_EXT_USER)

        if result.fail:
            logMessage='BAPI_XBP_JOB_OPEN {:s}: {:s}'.format(jobname, result.message)
            self.logger.error(logMessage)
            return result

        else:
            jobcount = result.data['jobcount']
            self.logger.debug('BAPI_XBP_JOB_OPEN successful for job {:s} with job count {:s}'.format(jobname, jobcount))
            return Result(data=jobcount)

    def z_bapi_xbp_job_select(self,
                              job_select_param:list,
                              abapname:str=None,
                              susp:str=None,
                              systemid:str=None,
                              selection:str=None):

        """ Get the list of jobs based on selection criteria
        :param job_select_param: table describing the jobs to retrieve. see below.
        :param abapname: Name of an ABAP program
        :param susp: Get suspended jobs
        :param systemid: SID of a remote system
        :param selection: specified what kind of confirmation is taken into account:
                            AL - Returns all child jobs, NG - only jobs without general conf. NC - Jobs without conf.
        :return:

        job_select_aram:

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

        fm_params=dict()

        fm_params['EXTERNAL_USER_NAME']=self.XBP_EXT_USER
        result = self.z_bapi_xmi_logon()

        if result.fail:
            return result

        fm_params['JOB_SELECT_PARAM']=job_select_param

        if abapname:
            fm_params['ABAPNAME']=abapname

        if susp:
            fm_params['SUSP']=susp

        if selection:
            fm_params['SELECTION']=selection

        if systemid:
            fm_params['SYSTEMID']=systemid


        result=self.z_call_bapi('BAPI_XBP_JOB_SELECT', **fm_params)

        if result.fail:
            self.logger.debug('bapi_xpb_job_select failed: {:s}'.format(pformat(result.message)))

        return result

    def z_bapi_xbp_variant_change(self, abap_program_name:str, abap_variant_name:str, abap_variant_text:str, dia=None, protected:bool=None,
                                  ext_user_name=None, variant_info=None, variant_info_l=None):
        """ Changes an already existing variant for ABAP program
        :param abap_program_name: str Program name
        :param abap_variant_name: str variant name
        :param abap_variant_text: str desciption for variant
        :param dia: batch or dialog?
        :param protected:
        :param ext_user_name: external xmi username
        :param variant_info: actual data of the variant
        :param variant_info_l: data of the variant with longnr parameters
        :return:

        The variantInfoL needs to be a list of dictionaries. each row consisting of these fields:

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

        result = self.z_bapi_xmi_logon(ext_company=self._XBP_EXT_COMPANY, ext_product=self._XBP_EXT_PRODUCT)
        if result.fail:
            self.logger.debug('logon to XBP interface failed {:s}/{:s}'.format(self._XBP_EXT_COMPANY,
                                                                               self._XBP_EXT_PRODUCT))
            return result

        self.logger.debug('logon to XBP interface successful')

        result=self.z_variant_exists(self, abap_program_name, abap_variant_name)
        if not result.fail:
            if result.result['data']:

                fmParameters=dict()
                if not ext_user_name:
                    fmParameters['EXTERNAL_USER_NAME'] = self._XBP_EXT_PRODUCT
                else:
                    fmParameters['EXTERNAL_USER_NAME']=ext_user_name

                fmParameters['ABAP_PROGRAM_NAME']=abap_program_name
                fmParameters['ABAP_VARIANT_NAME']=abap_variant_name
                fmParameters['ABAP_VARIANT_TEXT']=abap_variant_text

                if dia:
                    fmParameters['DIA']=dia

                if protected:
                    fmParameters['DIA']=protected

                if variant_info_l:
                    fmParameters['VARIANT_INFO_L']=variant_info_l
                elif variant_info:
                    fmParameters['VARIANT_INFO']=variant_info
                else:
                    return Fail('Missing Variant Information')
                result=self.call('BAPI_XBP_VARIANT_CHANGE', **fmParameters)
                if result['RETURN']['TYPE'] !='E':
                    return Result('variant created')
                else:
                    return Fail(result['RETURN']['MESSAGE'])
        else:
            result=self.z_bapi_xbp_variant_create(abap_program_name=abap_program_name, abap_variant_name=abap_variant_name,
                                                  abap_variant_text=abap_variant_text, dia=dia, protected=protected, ext_user_name=ext_user_name,
                                                  variant_info=variant_info, variant_info_l=variant_info_l)

            return result

    def z_bapi_xbp_variant_create(self, abap_program_name, abap_variant_name, abap_variant_text, dia=None, protected=None,
                                  ext_user_name=None, variant_info=None, variant_info_l=None):
        """ Create variant for ABAP program
        :param abap_program_name: str Program name
        :param abap_variant_name: str variant name
        :param abap_variant_text: str desciption for variant
        :param dia: batch or dialog?
        :param protected:
        :param ext_user_name: external xmi username
        :param variant_info: actual data of the variant
        :param variant_info_l: data of the variant with longnr parameters
        :return:

        The variantInfoL needs to be a list of dictionaries. each row consisting of these fields:

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

        result = self.z_bapi_xmi_logon(ext_company=self._XBP_EXT_COMPANY, ext_product=self._XBP_EXT_PRODUCT)
        if result.fail:
            self.logger.debug('logon to XBP interface failed {:s}/{:s}'.format(self._XBP_EXT_COMPANY,
                                                                               self._XBP_EXT_PRODUCT))
            return result

        self.logger.debug('logon to XBP interface successful')

        result=self.z_variant_exists(self, abap_program_name, abap_variant_name)
        if not result.fail:
            if not result.result['data']:

                fmParameters=dict()
                if not ext_user_name:
                    fmParameters['EXTERNAL_USER_NAME'] = self._XBP_EXT_PRODUCT
                else:
                    fmParameters['EXTERNAL_USER_NAME']=ext_user_name

                fmParameters['ABAP_PROGRAM_NAME']=abap_program_name
                fmParameters['ABAP_VARIANT_NAME']=abap_variant_name
                fmParameters['ABAP_VARIANT_TEXT']=abap_variant_text

                if dia:
                    fmParameters['DIA']=dia

                if protected:
                    fmParameters['DIA']=protected

                if variant_info_l:
                    fmParameters['VARIANT_INFO_L']=variant_info_l
                elif variant_info:
                    fmParameters['VARIANT_INFO']=variant_info
                else:
                    return Fail('Missing Variant Information')
                result=self.call('BAPI_XBP_VARIANT_CREATE', **fmParameters)
                if result['RETURN']['TYPE']=='E':
                    return Fail(result['RETURN']['MESSAGE'])
                else:
                    return Result('Variant Created')

            else:
                result=self.z_bapi_xbp_variant_create(abap_program_name=abap_program_name, abap_variant_name=abap_variant_name,
                                                      abap_variant_text=abap_variant_text, dia=dia, protected=protected, ext_user_name=ext_user_name,
                                                      variant_info=variant_info, variant_info_l=variant_info_l)
                return result

    def z_bapi_xbp_variant_info_get(self,
                                    abap_program_name:str,
                                    more_info:str=None,
                                    variant_select_option:str='A')->Union(Result, Fail):

        """ Get information about specific program variant.
        :param abap_program_name: str name of the ABAP program
        :param variant_select_option: 'A' means get all variants, 'B' means only get batch variants.
        :param more_info:
        :param extUserName: external user name.
        :return:
        """

        result=self.z_bapi_xmi_logon()
        if result.fail:
            self.logger.debug('logon to XBP interface failed {:s}/{:s}'.format(self._XBP_EXT_COMPANY,
                                                                               self._XBP_EXT_PRODUCT))
            return result

        self.logger.debug('logon to XBP interface successful')

        bapi_parameters=dict(ABAP_PROGRAM_NAME=abap_program_name)

        if variant_select_option in ['A', 'B']:
            bapi_parameters['VARIANT_SELECT_OPTION']=variant_select_option

        bapi_parameters['EXTERNAL_USER_NAME']=self._XBP_EXT_PRODUCT

        if more_info== 'X':
            bapi_parameters['MORE_INFO']='X'

        result=self.call('BAPI_XBP_VARIANT_INFO_GET', **bapi_parameters)

        return result

    def z_call_fm(self, fm:str, **kwargs):
        """ Call Function Module with Exception Handling"""
        message='Executing Function Module {}'.format(fm)
        try:
            data=self.call(fm, **kwargs)
        except pyrfc.ABAPRuntimeError as err:
            string = 'ABAP Runtime Error: ' + pformat(err)
            self.logger.debug(string)
            return Fail(message=string)
        except pyrfc.ExternalApplicationError as err:
            string = 'External Application Error: ' + pformat(err)
            self.logger.debug(string)
            return Fail(message=string)
        except pyrfc.ABAPApplicationError as err:
            string = 'ABAP Application Error: ' + pformat(err)
            self.logger.debug(string)
            return Fail(message=string)
        except pyrfc.ExternalRuntimeError as err:
            string = 'External Runtime Error: ' + pformat(err)
            self.logger.debug(string)
            return Fail(message=string)
        except pyrfc.CommunicationError as err:
            string = 'Communication Error: ' + pformat(err)
            self.logger.debug(string)
            return Fail(message=string)
        except pyrfc.LogonError as err:
            string = 'Logon Error: ' + pformat(err)
            self.logger.debug(string)
            return Fail(message=string)
        except pyrfc.ExternalAuthorizationError as err:
            string = 'External Authorization Error: ' +  pformat(err)
            self.logger.debug(string)
            return Fail(message=string)
        except pyrfc.RFCLibError as err:
            string = 'RFC Library Error: ' + pformat(err)
            self.logger.debug(string)
            return Fail(message=string)
        except pyrfc.RFCError as err:
            string = 'RFC Error: ' + pformat(err)
            self.logger.debug(string)
            return Fail(message=string)
        except Exception as err:
            string = 'non PyRFC Exception: ' + pformat(err)
            self.logger.debug(string)
            return Fail(message=string)
        return Result(data=data)

    def z_call_bapi(self, bapi:str, **kwargs):
        """ Call Function Module with Exception Handling"""
        self.logger.debug('Executing BAPI {}'.format(bapi))
        result=self.z_call_fm(bapi, **kwargs)

        if result.fail:
            return result

        response=result.data

        bapireturn=response.get('RETURN')
        if bapireturn is None:
            return Fail(message = 'RETURN structure missing from response, is {} not a BAPI?'.format(bapi),
                          data=response)

        for record in bapireturn:
            if record['TYPE']=='E':
                return Fail(message=record['MESSAGE'], data=response)

        return result

