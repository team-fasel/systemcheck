# -*- coding: utf-8 -*-

""" Tests for the Qt Models


"""

# define authorship information
__authors__ = ['Lars Fasel']
__author__ = ','.join(__authors__)
__credits__ = []
__copyright__ = 'Copyright (c) 2017'
__license__ = 'MIT'

# maintanence information
__maintainer__ = 'Lars Fasel'
__email__ = 'systemcheck@team-fasel.com'

import os

import sqlalchemy.orm
from systemcheck import models
#import systemcheck.models as models
from systemcheck.systems.generic.models import GenericSystemTreeNode
from systemcheck.gui.models import GenericTreeModel

from systemcheck.systems.ABAP.models.abap_model import SystemABAP, SystemABAPClient, SystemABAPFolder
from systemcheck.models.meta.base import scoped_session, sessionmaker, engine_from_config
import logging
import systemcheck_tools

from PyQt5 import QtCore

from unittest import TestCase


class TestAbapTreeModel(TestCase):
    PATH = r'test_pyqt_model.sqlite'

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

        try:
            rootnode = self.session.query(GenericSystemTreeNode).filter(GenericSystemTreeNode.parent_id == None).one()
        except sqlalchemy.orm.exc.NoResultFound as err:
            self.session.add(GenericSystemTreeNode(name='RootNode'))
            self.session.commit()


    def tearDown(self):

        self.session.close()
        if os.path.exists(self.PATH):
            os.remove(self.PATH)

    def populateTree(self):
        systemcheck_tools.populateSystemsABAPTree(self.session)

    def test_rowCount(self):
        self.populateTree()
        rootnode = self.session.query(GenericSystemTreeNode).filter_by(parent_id=None).one()
        model = GenericTreeModel(rootnode)
        rootindex = model.createIndex(0, 0, rootnode)

        self.assertEqual(model.rowCount(rootindex), 4)

    def test_columnCount(self):
        rootnode = self.session.query(GenericSystemTreeNode).filter_by(parent_id=None).one()
        model = GenericTreeModel(rootnode)
        column_count = model.columnCount()
        self.assertEqual(column_count, 2)
        rootindex = model.createIndex(0, 0, rootnode)
        self.assertTrue(rootindex.isValid())
        name = model.data(rootindex, QtCore.Qt.DisplayRole)
        assert name == 'RootNode'

    def test_data(self):
        self.populateTree()
        rootnode = self.session.query(GenericSystemTreeNode).filter_by(parent_id=None).one()
        model = GenericTreeModel(rootnode)
        index = model.createIndex(0, 0, rootnode)
        self.assertTrue(index.isValid())
        name = model.data(index, QtCore.Qt.DisplayRole)
        self.assertEqual(name, 'RootNode')

    def test_setData(self):
        rootnode = self.session.query(GenericSystemTreeNode).filter_by(parent_id=None).one()
        model = GenericTreeModel(rootnode)
        index = model.createIndex(0, 0, rootnode)
        self.assertTrue(index.isValid())
        name = model.data(index, QtCore.Qt.DisplayRole)
        self.assertEqual(name, 'RootNode')
        model.setData(index, 'StillRootNode')
        name = model.data(index, QtCore.Qt.DisplayRole)
        self.assertEqual(name, 'StillRootNode')

    def test_headerData(self):
        rootnode = self.session.query(GenericSystemTreeNode).filter_by(parent_id=None).one()
        model = GenericTreeModel(rootnode)
        index = model.createIndex(0, 0, QtCore.QModelIndex())
        headerdata = model.headerData(0, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
        self.assertEqual(headerdata, 'Name')

    def test_flags(self):
        rootnode = self.session.query(GenericSystemTreeNode).filter_by(parent_id=None).one()
        model = GenericTreeModel(rootnode)
        index = model.createIndex(0, 0, rootnode)
        flags = model.flags(index)
        self.assertEqual(flags, QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable \
                         | QtCore.Qt.ItemIsUserCheckable |QtCore.Qt.ItemIsEditable)

    def test_insertRow(self):
        rootnode = self.session.query(GenericSystemTreeNode).filter_by(parent_id=None).one()
        model = GenericTreeModel(rootnode)
        index = model.createIndex(0, 0, rootnode)
        child_count_root = model.rowCount(index)
        self.assertEqual(child_count_root, 0)
        system_node = SystemABAP(name='New SID', sid='NEW')
        model.insertRow(0, index, nodeObject=system_node)
        child_count_root = model.rowCount(index)
        self.assertEqual(child_count_root, 1)  #Successfully added one new system
        self.assertTrue(model.hasChildren(index))  #Another test

        #Testing Inserting a new client
        system_index = model.index(0, 0, index)
        child_count_system = model.rowCount(system_index)
        self.assertEqual(child_count_system, 0)  #No new client exists
        self.assertFalse(model.hasChildren(system_index))  #Another test

        client_node = SystemABAPClient(client='000')
        model.insertRow(position=0, parent=system_index, nodeObject=client_node)
        child_count_system = model.rowCount(system_index)
        self.assertEqual(child_count_system, 1)  #Successfully added one new system
        self.assertTrue(model.hasChildren(system_index))  #Another test

    def test_insertRows(self):
        rootnode = self.session.query(GenericSystemTreeNode).filter_by(parent_id=None).one()
        model = GenericTreeModel(rootnode, treenode=GenericSystemTreeNode)
        index = model.createIndex(0, 0, rootnode)
        model.insertRows(0, 10, index)
        self.assertEqual(model.rowCount(index), 10)

    def test_removeRow(self):
        rootnode = self.session.query(GenericSystemTreeNode).filter_by(parent_id=None).one()
        model = GenericTreeModel(rootnode, treenode=GenericSystemTreeNode)
        index = model.createIndex(0, 0, rootnode)
        model.insertRow(0, index)
        self.assertEqual(model.rowCount(index), 1)
        model.removeRow(0, index)
        self.assertEqual(model.rowCount(index), 0)

    def test_removeRows(self):
        rootnode = self.session.query(GenericSystemTreeNode).filter_by(parent_id=None).one()
        model = GenericTreeModel(rootnode, treenode=GenericSystemTreeNode)
        index = model.createIndex(0, 0, rootnode)
        model.insertRows(0, 10, index)
        self.assertEqual(model.rowCount(index), 10)
        model.removeRows(1, 5, index)
        self.assertEqual(model.rowCount(index), 5)

    def test_parent(self):
        self.populateTree()
        rootnode = self.session.query(GenericSystemTreeNode).filter_by(parent_id=None).one()
        model = GenericTreeModel(rootnode, treenode=GenericSystemTreeNode)

        node1index = model.index(0, 0, QtCore.QModelIndex())
        node2index = model.index(0, 0, node1index)

        self.assertEqual(model.data(node1index, QtCore.Qt.DisplayRole), 'DEV')
        self.assertEqual(model.data(node2index, QtCore.Qt.DisplayRole), 'E1D')

        data_node1 = model.data(node1index, QtCore.Qt.DisplayRole)

        node1_node = node1index.internalPointer()
        self.assertEqual(node1_node.name, 'DEV')
        node2_node = node2index.internalPointer()
        self.assertEqual(node2_node.name, 'E1D')
        node2_parent_index = model.parent(node2index)
        node2_parent_node = node2_parent_index.internalPointer()
        self.assertEqual(node2_parent_node.name, 'DEV')

    def test_index(self):
        self.populateTree()
        rootnode = self.session.query(GenericSystemTreeNode).filter_by(parent_id=None).one()
        model = GenericTreeModel(rootnode, treenode=GenericSystemTreeNode)

        index = model.index(0, 0, QtCore.QModelIndex())
        node = index.internalPointer()
        self.assertEqual(node.name, 'DEV')

    def test_getNode(self):
        self.populateTree()
        rootnode = self.session.query(GenericSystemTreeNode).filter_by(parent_id=None).one()
        model = GenericTreeModel(rootnode, treenode=GenericSystemTreeNode)

        index = model.index(0, 0, QtCore.QModelIndex())
        node = model.getNode(index)

        self.assertEqual(node.name, 'DEV')

        index = model.index(99, 2, QtCore.QModelIndex())
        node = model.getNode(index)

        self.assertEqual(node.name, 'RootNode')

    def test_recursiveCheck(self):
        self.populateTree()
        rootnode = self.session.query(GenericSystemTreeNode).filter_by(parent_id=None).one()
        model = GenericTreeModel(rootnode, treenode=GenericSystemTreeNode)
        self.logger.info('setting parent index')
        parent_index = model.index(0, 0, QtCore.QModelIndex())
        self.logger.info('setting parent checked')
        model.setData(parent_index, QtCore.Qt.Checked, QtCore.Qt.CheckStateRole)
        state = model.data(parent_index, QtCore.Qt.CheckStateRole)
        self.logger.info('Validating that state is checked')
        self.assertTrue(state)

        self.logger.info('Validating that all children are checked')
        for childnr in range(model.rowCount(parent_index)):
            subindex=model.index(childnr, 0, parent_index)
            state = model.data(subindex, QtCore.Qt.CheckStateRole)
            self.assertTrue(state)

        self.logger.info('testing unchecking')
        model.setData(parent_index, QtCore.Qt.Unchecked, QtCore.Qt.CheckStateRole)
        state = model.data(parent_index, QtCore.Qt.CheckStateRole)
        self.logger.info('Validating that state is unchecked')
        self.assertFalse(state)

        self.logger.info('Validating that all children are unchecked')
        for childnr in range(model.rowCount(parent_index)):
            subindex = model.index(childnr, 0, parent_index)
            state = model.data(subindex, QtCore.Qt.CheckStateRole)
            self.assertFalse(state)

