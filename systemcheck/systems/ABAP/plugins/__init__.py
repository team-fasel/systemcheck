# -*- coding: utf-8 -*-

""" Definition of ABAP specific Check Plugins

=
"""

# define authorship information
__authors__     = ['Lars Fasel']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2017'
__license__     = 'MIT'

import systemcheck.systems.generic.plugins
from systemcheck.utils import Result, Fail
import systemcheck.systems.ABAP.utils as abaputils
from pprint import pformat
import logging
from collections import OrderedDict
import ast


class CheckAbapFoundationPlugin(systemcheck.systems.generic.plugins.GenericCheckPlugin):
    """ ABAP Foundation Plugin
    Base class for all ABAP Plugins. """

    TYPE='ABAP'

    def __init__(self):
        super().__init__()


    def system_connection(self):
        """ Get RFC System Connection
        """
        logon_info = self._system_object.logon_info()
        result = abaputils.get_connection(logon_info)

        if not result.fail:
            self.conn = result.data

        return result


class CheckAbapPlugin(CheckAbapFoundationPlugin):
    """ Generic ABAP Plugin

    This is the basic plugin that all plugins should be based on. If you want to code your own plugin, us this as the
    parent. The plugin reduces the effort of implementing your own code.

    Your main code needs to be executed in a function "execute":

    .. code:: python

        def execute(conn, sysInfo, *args, **kwargs):


    """


    def __init__(self):
        super().__init__()


class CheckAbapCountTableEntries(CheckAbapFoundationPlugin):

    def execute(self, connection, **kwargs):

        self.pluginResult.resultDefinition = OrderedDict(RATING='Rating', WHERE_CLAUSE='Where Clause',
                                                         OPERATOR='Operator', TABLE='Table',
                                                         EXPECTED='Expected', CONFIGURED='Configured')

        self.connection=connection

        for item, value in self.pluginConfig['RuntimeParameters'].items():
            config=self.pluginConfig['RuntimeParameters'].get(item, raw=True)
            data=ast.literal_eval(config)

            record=dict(RATING='pass',
                        WHERE_CLAUSE=data['WHERE_CLAUSE'],
                        TABLE=data['TABLE'],
                        EXPECTED=int(data['EXPECTED']),
                        OPERATOR = data.get('OPERATOR'))

            if not record['OPERATOR']:
                record['OPERATOR'] = 'EQ'

            result=self.connection.download_table(record['TABLE'],
                                                  where_clause=record['WHERE_CLAUSE'],
                                                  tab_fields=data['COLUMNS'])
            if not result.fail:
                downloaded_data=result.data['data']
                record['CONFIGURED']=str(len(downloaded_data))
            else:
                record['CONFIGURED']=result.fail
                self.pluginResult.add_result(record)
                self.pluginResult.rating='error'
                return Result(self.pluginResult)

            success=self.OPERATIONS[data['OPERATOR']](int(record['EXPECTED']), int(record['CONFIGURED']))

            if not success:
                record['RATING']='fail'
                self.pluginResult.rating='fail'

            self.pluginResult.add_result(record)

        return Result(data=self.pluginResult)



