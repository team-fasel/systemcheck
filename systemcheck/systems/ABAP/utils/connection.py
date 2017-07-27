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


    def logon(self, logon_info:dict, mock:bool=False, mockdata:dict=False)->Union[Result, Fail]:
        """ Logon to the specified system

        :param logon_info: Information required to logon to a system
        :param mock: If True, then no real pyRFC conection will be established. This is for testing.
        :param moockdata: Data that should be used for the mock testing

        """
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
                self.conn = pyrfc.Connection(**logon_info)
            except Exception as err:
                result = self._handle_exception(err)
        return result

    @property
    def instances(self) -> Union[Result, Fail]:
        """ Returns the names of the instances as list"""
        fm_result = self.call_fm('TH_SERVER_LIST')
        if fm_result.fail:
            return fm_result

        result = [instance['NAME'] for instance in fm_result.data['LIST']]

        return Result(data=result)

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

    @property
    def clients(self) -> Union[Result, Fail]:
        result = self.download_table('T000', tab_fields=['MANDT', 'MTEXT'])
        return result

    def call_fm(self, fm: str, **kwargs) -> Union[Result, Fail]:
        """ Call Function Module with Exception Handling"""
        self.logger.debug('Executing Function Module {}'.format(fm))

        try:
            data = self.conn.call(fm, **kwargs)
        except Exception as err:
            return(self._handle_exception(err))
        return Result(message='call to {} successful'.format(fm), data=data)

    def call_bapi(self, bapi: str, acceptable: list = None, **kwargs) -> Union[Result, Fail]:
        """ Call BAPI with Error Handling

        :param: bapi: Name of the BAPI
        :param: acceptable: a list of BAPIRET2 structures that are error conditions, but should not raise an error.

        """
        self.logger.debug('Executing BAPI {}'.format(bapi))
        result = self.call_fm(bapi, **kwargs)

        if result.fail:
            return result

        response = result.data

        bapireturn = response.get('RETURN')
        if bapireturn is None:
            return Fail(message='RETURN structure missing from response, is {} not a BAPI?'.format(bapi),
                        data=response)

        for record in bapireturn:
            if record['TYPE'] == 'E' or record['TYPE'] == 'A':
                return Fail(message=record['MESSAGE'], data=response)

        return result

    def close(self):
        self.conn.close()

    def download_table(self,
                       tabname: str,
                       where_clause: str = None,
                       tab_fields: list = None,
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