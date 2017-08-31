from systemcheck.results import ResultHandler
from systemcheck.plugins.action_types import ActionResult
from unittest import TestCase
from collections import OrderedDict
from PyQt5 import QtCore


class TestResultsHandling(TestCase):

    def setUp(self):

        self._results=[]

        result=ActionResult()
        result.rating='pass'
        result.resultDefinition = OrderedDict(RATING='Rating',
                                              WHERE_CLAUSE='Where Clause',
                                              OPERATOR='Operator',
                                              TABLE='Table',
                                              EXPECTED='Expected',
                                              CONFIGURED='Configured')

        record = dict(RATING='pass',
                      WHERE_CLAUSE="MANDT EQ '000'",
                      TABLE='T000',
                      EXPECTED=0,
                      OPERATOR='EQ')

        result.add_result(record)
        result.check_name='Clients 000 deleted'
        result.logoninfo=dict(ashost='abap001.team-fasel.lab',
                              sysnr='00',
                              client='001',
                              user='DEVELOPER',
                              passwd='Appl1ance',
                              sid='NPL')
        result.systeminfo = 'NPL:001'

        result1=ActionResult()
        result1.rating='pass'
        result1.resultDefinition = OrderedDict(RATING='Rating',
                                              WHERE_CLAUSE='Where Clause',
                                              OPERATOR='Operator',
                                              TABLE='Table',
                                              EXPECTED='Expected',
                                              CONFIGURED='Configured')

        record = dict(RATING='pass',
                      WHERE_CLAUSE="MANDT EQ '066'",
                      TABLE='T000',
                      EXPECTED=0,
                      OPERATOR='EQ')

        result1.add_result(record)
        result1.check_name='Clients 066 deleted'
        result1.logoninfo=dict(ashost='abap001.team-fasel.lab',
                              sysnr='00',
                              client='001',
                              user='DEVELOPER',
                              passwd='Appl1ance',
                              sid='NPL')
        result1.systeminfo = 'NPL:001'

        self._results.append(result)
        self._results.append(result1)

    def test_addResult(self):

        handler = ResultHandler()
        model = handler.buildTreeModel()

        for result in self._results:
            handler.addResult(result)

        self.assertEqual(model.rowCount(QtCore.QModelIndex()), 1)