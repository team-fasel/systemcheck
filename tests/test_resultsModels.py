from systemcheck.plugins.action_types import ActionResult
from systemcheck.results.result_handler import Node, ResultNode, ResultTreeModel, ResultTableModel
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

        self._rootNode = Node('RootNode')


    def test_rowCount(self):

        tree=ResultTreeModel(['Result'], ['rating', 'check_name', 'systeminfo'], root=self._rootNode)
        rowcount = tree.rowCount(QtCore.QModelIndex())
        self.assertEqual(rowcount, 0)

    def test_insertResult(self):
        tree=ResultTreeModel(['Result'], ['rating', 'check_name', 'systeminfo'], root=self._rootNode)
        rowcount = tree.rowCount(QtCore.QModelIndex())
        self.assertEqual(rowcount, 0)
        for result in self._results:
            tree.insertResult(result)

        self.assertEqual(tree.rowCount(QtCore.QModelIndex()), 1)

        node=tree.getNode(QtCore.QModelIndex())
        print(node.log())


    def test_findIndexByName(self):
        tree=ResultTreeModel(['Result'], ['rating', 'check_name', 'systeminfo'], root=self._rootNode)
        rowcount = tree.rowCount(QtCore.QModelIndex())
        self.assertEqual(rowcount, 0)
        for result in self._results:
            tree.insertResult(result)

        index = tree.findIndexByName('Clients 066 deleted', parent=QtCore.QModelIndex())
        self.assertEqual(index, None)
        index = tree.findIndexByName('pass', parent=QtCore.QModelIndex())
        if index:
            node=tree.getNode(index)
            self.assertEqual(node.childCount(), 2)

        index = tree.findIndexByName('fail', parent=QtCore.QModelIndex())
        self.assertEqual(index, None)

        node=tree.getNode(QtCore.QModelIndex())
        print(node.log())

    def test_insertResult(self):
        tree=ResultTreeModel(['Result'], ['rating', 'check_name', 'systeminfo'], root=self._rootNode)
        for result in self._results:
            tree.insertResult(result)

        print(tree._rootNode.log())

class TestResultsTableModel(TestCase):

    def setUp(self):

        self._results=[]

        result=ActionResult()
        result.rating='pass'
        result.addResultColumn('RATING', 'Rating')
        result.addResultColumn('WHERE_CLAUSE', 'Where Clause')
        result.addResultColumn('OPERATOR', 'Operator')
        result.addResultColumn('TABLE', 'Table')
        result.addResultColumn('EXPECTED', 'Expected')
        result.addResultColumn('CONFIGURED', 'Configured')

        record = dict(RATING='pass',
                      WHERE_CLAUSE="MANDT EQ '000'",
                      TABLE='T000',
                      EXPECTED=0,
                      CONFIGURED=0,
                      OPERATOR='EQ')

        result.add_result(record)
        result.check_name='Clients 001 and 066 deleted'
        result.logoninfo=dict(ashost='abap001.team-fasel.lab',
                              sysnr='00',
                              client='001',
                              user='DEVELOPER',
                              passwd='Appl1ance',
                              sid='NPL')
        result.systeminfo = 'NPL:001'

        record = dict(RATING='pass',
                      WHERE_CLAUSE="MANDT EQ '066'",
                      TABLE='T000',
                      EXPECTED=0,
                      CONFIGURED=0,
                      OPERATOR='EQ')

        result.add_result(record)
        self._results.append(result)
        self._rootNode = Node('RootNode')

    def test_InitTableModel(self):

        tableModel=ResultTableModel(self._results[0])

        self.assertEqual(tableModel.rowCount(), 2)
        self.assertEqual(tableModel.columnCount(), 6)
        self.assertEqual(tableModel.headerData(0, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole), 'Rating')