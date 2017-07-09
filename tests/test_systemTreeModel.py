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

import systemcheck.model as model
from systemcheck.gui.models import SystemTreeModel
from systemcheck.model.systems import AbapSystem, AbapClient, SystemTreeNode, Credential
from systemcheck.model.meta.base import scoped_session, sessionmaker, engine_from_config
import logging

from PyQt5 import QtCore

from unittest import TestCase


class TestSystemTreeModel(TestCase):
    PATH = r'D:\Python\Projects\systemcheck\tests\test_pyqt_model.sqlite'
    logger = logging.getLogger(__name__)

    def setUp(self):
        self.dbconfig = {'sqlalchemy.echo': False,
                         'sqlalchemy.url': 'sqlite:///' + self.PATH, }

        if os.path.exists(self.PATH):
            os.remove(self.PATH)

        self.engine = engine_from_config(self.dbconfig)
        model.meta.base.Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind=self.engine)
        self.session = scoped_session(self.session_factory)

        if self.session.query(SystemTreeNode).filter(SystemTreeNode.type == 'ROOT').count() == 0:
            self.session.add(SystemTreeNode(type='ROOT', name='RootNode'))
            self.session.commit()

    def tearDown(self):

        self.session.close()
        if os.path.exists(self.PATH):
            os.remove(self.PATH)

    def populateTree(self):
        rootnode = self.session.query(SystemTreeNode).filter_by(type='ROOT').first()

        dev_folder = SystemTreeNode(type='FOLDER', name='DEV', parent=rootnode)
        qas_folder = SystemTreeNode(type='FOLDER', name='QAS', parent=rootnode)
        prd_folder = SystemTreeNode(type='FOLDER', name='PRD', parent=rootnode)
        sbx_folder = SystemTreeNode(type='FOLDER', name='SBX', parent=rootnode)

        e1d_node = SystemTreeNode(type='FOLDER', parent=dev_folder, name='E1D')
        e1s_node = SystemTreeNode(type='FOLDER', parent=sbx_folder, name='E1S')
        self.session.commit()

    def test_rowCount(self):
        self.populateTree()
        rootnode = self.session.query(SystemTreeNode).filter_by(type='ROOT').first()
        model = SystemTreeModel(rootnode)
        rootindex = model.createIndex(0, 0, rootnode)

        self.assertEqual(model.rowCount(rootindex), 4)

    def test_columnCount(self):
        rootnode = self.session.query(SystemTreeNode).filter_by(type='ROOT').first()
        model=SystemTreeModel(rootnode)
        column_count=model.columnCount()
        self.assertEqual(column_count, 2)
        rootindex=model.createIndex(0, 0, rootnode)
        self.assertTrue(rootindex.isValid())
        type = model.data(rootindex, QtCore.Qt.DisplayRole)
        assert type == 'ROOT'
        index=model.createIndex(0, 1, rootnode)
        name = model.data(index, QtCore.Qt.DisplayRole)
        assert name == 'RootNode'

    def test_data(self):
        self.populateTree()
        rootnode = self.session.query(SystemTreeNode).filter_by(type='ROOT').first()
        model = SystemTreeModel(rootnode)
        index=model.createIndex(0, 0, rootnode)
        self.assertTrue(index.isValid())
        type = model.data(index, QtCore.Qt.DisplayRole)
        self.assertEqual(type, 'ROOT')
        index=model.createIndex(0, 1, rootnode)
        name = model.data(index, QtCore.Qt.DisplayRole)
        self.assertEqual(name, 'RootNode')

    def test_setData(self):
        rootnode = self.session.query(SystemTreeNode).filter_by(type='ROOT').first()
        model = SystemTreeModel(rootnode)
        index=model.createIndex(0, 0, rootnode)
        self.assertTrue(index.isValid())
        type = model.data(index, QtCore.Qt.DisplayRole)
        self.assertEqual(type, 'ROOT')
        index=model.createIndex(0, 1, rootnode)
        name = model.data(index, QtCore.Qt.DisplayRole)
        self.assertEqual(name, 'RootNode')
        model.setData(index, 'StillRootNode')
        name = model.data(index, QtCore.Qt.DisplayRole)
        self.assertEqual(name, 'StillRootNode')

    def test_headerData(self):
        rootnode = self.session.query(SystemTreeNode).filter_by(type='ROOT').first()
        model = SystemTreeModel(rootnode)
        index=model.createIndex(0, 0, QtCore.QModelIndex())
        headerdata=model.headerData(0, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
        self.assertEqual(headerdata, 'Type')
        headerdata = model.headerData(1, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
        self.assertEqual(headerdata, 'Name')

    def test_flags(self):
        rootnode = self.session.query(SystemTreeNode).filter_by(type='ROOT').first()
        model = SystemTreeModel(rootnode)
        index = model.createIndex(0, 0, rootnode)
        flags = model.flags(index)
        self.assertEqual(flags, QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

    def test_insertRow(self):
        rootnode = self.session.query(SystemTreeNode).filter_by(type='ROOT').first()
        model = SystemTreeModel(rootnode)
        index = model.createIndex(0, 0, rootnode)
        model.insertRow(0, index)
        self.assertTrue(model.hasChildren(index))

    def test_insertRows(self):
        rootnode = self.session.query(SystemTreeNode).filter_by(type='ROOT').first()
        model = SystemTreeModel(rootnode)
        index = model.createIndex(0, 0, rootnode)
        model.insertRows(0, 10, index)
        self.assertEqual(model.rowCount(index), 10)

    def test_removeRow(self):
        rootnode = self.session.query(SystemTreeNode).filter_by(type='ROOT').first()
        model = SystemTreeModel(rootnode)
        index = model.createIndex(0, 0, rootnode)
        model.insertRow(0, index)
        self.assertEqual(model.rowCount(index), 1)
        model.removeRow(0, index)
        self.assertEqual(model.rowCount(index), 0)

    def test_removeRows(self):
        rootnode = self.session.query(SystemTreeNode).filter_by(type='ROOT').first()
        model = SystemTreeModel(rootnode)
        index = model.createIndex(0, 0, rootnode)
        model.insertRows(0, 10, index)
        self.assertEqual(model.rowCount(index), 10)
        model.removeRows(1, 5, index)
        self.assertEqual(model.rowCount(index), 5)

    def test_parent(self):
        self.populateTree()
        rootnode = self.session.query(SystemTreeNode).filter_by(type='ROOT').first()
        model = SystemTreeModel(rootnode)

        node1index = model.index(0, 1, QtCore.QModelIndex())
        node2index = model.index(0, 1, node1index)

        self.assertEqual(model.data(node1index, QtCore.Qt.DisplayRole), 'DEV')
        self.assertEqual(model.data(node2index, QtCore.Qt.DisplayRole), 'E1D')

        data_node1 = model.data(node1index, QtCore.Qt.DisplayRole)

        node1_node = node1index.internalPointer()
        self.assertEqual(node1_node.type, 'FOLDER')
        self.assertEqual(node1_node.name, 'DEV')
        node2_node = node2index.internalPointer()
        self.assertEqual(node2_node.type, 'FOLDER')
        self.assertEqual(node2_node.name, 'E1D')
        node2_parent_index = model.parent(node2index)
        node2_parent_node = node2_parent_index.internalPointer()
        self.assertEqual(node2_parent_node.type, 'FOLDER')
        self.assertEqual(node2_parent_node.name, 'DEV')

    def test_index(self):
        self.populateTree()
        rootnode = self.session.query(SystemTreeNode).filter_by(type='ROOT').first()
        model = SystemTreeModel(rootnode)

        index = model.index(0, 0, QtCore.QModelIndex())
        node = index.internalPointer()
        self.assertEqual(node.type, 'FOLDER')
        self.assertEqual(node.name, 'DEV')

    def test_getNode(self):
        self.populateTree()
        rootnode = self.session.query(SystemTreeNode).filter_by(type='ROOT').first()
        model = SystemTreeModel(rootnode)

        index = model.index(0, 0, QtCore.QModelIndex())
        node = model.getNode(index)

        self.assertEqual(node.type, 'FOLDER')
        self.assertEqual(node.name, 'DEV')

        index = model.index(99,2, QtCore.QModelIndex())
        node = model.getNode(index)

        self.assertEqual(node.type, 'ROOT')
        self.assertEqual(node.name, 'RootNode')

