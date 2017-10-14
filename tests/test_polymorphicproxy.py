from PyQt5 import QtWidgets, QtCore, QtGui

import logging
import os
import systemcheck.models as models
from systemcheck.utils import get_or_create
from systemcheck.checks.models.checks import Check
from systemcheck.gui.models import GenericTreeModel
from systemcheck.models.meta.base import engine_from_config, scoped_session, sessionmaker
from systemcheck.systems.ABAP.plugins.actions.check_abap_count_table_entries import CheckAbapCountTableEntries, \
    CheckAbapCountTableEntries__params
from systemcheck.systems.ABAP.models import ActionAbapFolder
from systemcheck.gui.models import PolyMorphicFilterProxyModel
import unittest
from systemcheck_tools import populateChecksTree, populateSystemsABAPTree


class PolyMorphicFilterProxyModelTest(unittest.TestCase):

    PATH = 'TestPolyMorphicFilterProxyModel.sqlite'

    def setUp(self):
        self.logger = logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))
        self.dbconfig = {'sqlalchemy.echo': False,
                         'sqlalchemy.url': 'sqlite:///' + self.PATH, }

        if os.path.exists(self.PATH):
            os.remove(self.PATH)

        self.engine = engine_from_config(self.dbconfig)
        models.meta.base.Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind=self.engine)
        self.session = scoped_session(self.session_factory)

        self.filter=[Check, ActionAbapFolder]
        self.all = [Check, ActionAbapFolder, CheckAbapCountTableEntries, CheckAbapCountTableEntries__params]

    def tearDown(self):

        self.session.close()
        if os.path.exists(self.PATH):
            os.remove(self.PATH)


    def test_filterAcceptsRow(self):
        populateChecksTree(self.session)
        rootnode = self.session.query(Check).filter_by(parent_id=None).first()
        model = GenericTreeModel(rootnode, treenode=Check)

        filter_model=PolyMorphicFilterProxyModel(filterClasses=self.filter)
        filter_model.setSourceModel(model)

        rootindex=QtCore.QModelIndex()
        self.assertEqual(model.rowCount(rootindex), 2)
        self.assertEqual(filter_model.rowCount(rootindex), 2)
        index=model.index(1, 0, rootindex)  #Folder "Basis"
        self.assertEqual(model.rowCount(index), 1)
        self.assertEqual(model.data(index, QtCore.Qt.DisplayRole), 'Basis')
        self.assertEqual(model.rowCount(index), 1)
        index=model.index(0, 0, index)
        self.assertEqual(model.data(index, QtCore.Qt.DisplayRole), 'Post Install')
        self.assertEqual(model.rowCount(index), 1)
        index=model.index(0, 0, index)
        self.assertEqual(model.data(index, QtCore.Qt.DisplayRole), 'Clients 001 and 066 removed')

        filter_index=filter_model.index(1, 0, rootindex)
        self.assertEqual(filter_model.data(filter_index, QtCore.Qt.DisplayRole), 'Basis')
        filter_index=filter_model.index(0, 0, filter_index)
        self.assertEqual(filter_model.data(filter_index, QtCore.Qt.DisplayRole), 'Post Install')
        self.assertEqual(filter_model.rowCount(filter_index), 0)


    def test_insertRow(self):
        rootnode = get_or_create(self.session, Check, parent_id=None, name='RootNode')
        model = GenericTreeModel(rootnode, treenode=Check)
        proxymodel = PolyMorphicFilterProxyModel()
        proxymodel.setSourceModel(model)

        index = QtCore.QModelIndex()

        check=CheckAbapCountTableEntries(name = 'Clients 001 and 066 removed',
                                         description = 'If client 001 is not actively used, it can be deleted. Client 066 is no longer required in any case',
                                         )


        param001 = CheckAbapCountTableEntries__params(
                                         table_name = 'T000',
                                         table_fields = 'MANDT',
                                         expected_count = 0,
                                         operator = 'NE',
                                         where_clause = "MANDT EQ '001'"
                                         )
        param066 = CheckAbapCountTableEntries__params(
                                         table_name = 'T000',
                                         table_fields = 'MANDT',
                                         expected_count = 0,
                                         operator = 'NE',
                                         where_clause = "MANDT EQ '066'"
                                         )
        check.params.append(param001)
        check.params.append(param066)

        print('\nroot node: ')
        print(rootnode._dump())
        print('\ncheck node: ')
        print(check._dump())

        proxymodel.insertRow(position=0, parent=QtCore.QModelIndex(), nodeObject=check)

        print('\nroot node after insertRow: ')
        print(rootnode._dump())

        #proxymodel=PolyMorphicFilterProxyModel()
        #proxymodel.setSourceModel(model)
        proxyRowcount=proxymodel.rowCount(QtCore.QModelIndex())

        sourceRowcount=model.rowCount(QtCore.QModelIndex())

        for count in range(proxyRowcount):
            index = proxymodel.index(count, 0, QtCore.QModelIndex())
            sourceIndex = proxymodel.mapToSource(index)
            node = model.getNode(sourceIndex)
            print('Node {}'.format(count))
            print(node._dump())


#        self.assertTrue(proxymodel.hasChildren(index))  #Another test
        self.assertEqual(proxyRowcount, sourceRowcount)

    def test_removeRows(self):
        rootnode = get_or_create(self.session, Check, parent_id=None, name='RootNode')
        model = GenericTreeModel(rootnode, treenode=Check)
        proxymodel = PolyMorphicFilterProxyModel()
        proxymodel.setSourceModel(model)

        index = QtCore.QModelIndex()

        check=CheckAbapCountTableEntries(name = 'Clients 001 and 066 removed',
                                         description = 'If client 001 is not actively used, it can be deleted. Client 066 is no longer required in any case',
                                         )


        param001 = CheckAbapCountTableEntries__params(
                                         table_name = 'T000',
                                         table_fields = 'MANDT',
                                         expected_count = 0,
                                         operator = 'NE',
                                         where_clause = "MANDT EQ '001'"
                                         )
        param066 = CheckAbapCountTableEntries__params(
                                         table_name = 'T000',
                                         table_fields = 'MANDT',
                                         expected_count = 0,
                                         operator = 'NE',
                                         where_clause = "MANDT EQ '066'"
                                         )
        check.params.append(param001)
        check.params.append(param066)

        print('\nroot node: ')
        print(rootnode._dump())
        print('\ncheck node: ')
        print(check._dump())

        proxymodel.insertRow(position=0, parent=QtCore.QModelIndex(), nodeObject=check)


        print('\nroot node after insertRow: ')
        print(rootnode._dump())



        self.assertEqual(proxymodel.rowCount(QtCore.QModelIndex()), 1)
        proxymodel.removeRows(0, 1, index)
        self.assertEqual(proxymodel.rowCount(index), 0)