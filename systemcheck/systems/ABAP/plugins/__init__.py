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
from systemcheck.systems.ABAP.utils import Connection
from pprint import pformat
import logging
from collections import OrderedDict
import ast


class CheckAbapFoundationPlugin(systemcheck.systems.generic.plugins.BasePlugin):
    """ ABAP Foundation Plugin
    Base class for all ABAP Plugins. """

    TYPE='ABAP'

    def __init__(self):
        super().__init__()
        self.pluginConfig['base_config']['systemtype']=self.TYPE

    def system_connection(self, logonInfo, **kwargs):
        """ Get RFC System Connection
        """
        result = Connection(**logonInfo)
        if not result.fail:
            self.logger.info('successfully connected to {}'.format(pformat(logonInfo)))

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
        self.logger.info('starting plugin {:s}'.format(self.pluginConfig['Core']['name']))


class CheckAbapCountTableEntries(CheckAbapFoundationPlugin):

    def execute(self, connection, **kwargs):

        self.pluginResult['resultRating']='pass'
        self.pluginResult['result']=[]
        self.pluginResult['tableDefinition'] = OrderedDict(RATING='Rating', WHERE_CLAUSE='Where Clause',
                                                           OPERATOR='Operator', TABLE='Table',
                                                           EXPECTED='Expected', CONFIGURED='Configured')

        totalResult=[]

        self.connection=connection

        for item, value in self.pluginConfig['RuntimeParameters']:
            config=self.pluginConfig['RuntimeParameters'].get(item, raw=True)
            data=ast.literal_eval(config)

            record=dict(RATING='pass',
                        WHERE_CLAUSE=data['WHERE_CLAUSE'],
                        TABLE=data['TABLE'],
                        EXPECTED=data['COUNT_VALUE'])

            record['OPERATOR']=data.get('COUNT_OPERATOR')

            if not record['OPERATOR']:
                record['OPERATOR'] = 'EQ'

            result=self.connection.zDownloadSapTable(record['TABLE'], whereclause=record['WHERE_CLAUSE'], tabfields=data['COLUMNS'])
            if not result.fail:
                record['CONFIGURED']=str(len(result.result['data']))
            else:
                record['CONFIGURED']=result.fail
                totalResult.append(record)
                self.pluginResult.resultRating='error'
                self.pluginResult.pluginExecutionError=True
                self.pluginResult.pluginExecutionErrorDescription=result.fail
                self.pluginResult.setTableResult(totalResult)
                return Result(self.pluginResult)

            success=self.OPERATIONS[data['COUNT_OPERATOR']](int(record['EXPECTED']), int(record['CONFIGURED']))

            if not success:
                record['RATING']='fail'
                self.pluginResult.resultRating='fail'

            totalResult.append(record)

        self.pluginResult.setTableResult(totalResult)
        return Result(self.pluginResult)



