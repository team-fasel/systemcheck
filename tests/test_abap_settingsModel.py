
import os

import systemcheck
from systemcheck.gui.models import GenericTreeModel
from systemcheck.gui.models import SettingsModel
from systemcheck.systems.generic.models import GenericSystemTreeNode
from systemcheck.systems.ABAP.models import SystemABAP, SystemABAPClient
from systemcheck.models.meta.base import scoped_session, sessionmaker, engine_from_config
import logging
from . import tools

from PyQt5 import QtCore

from unittest import TestCase



class TestSettingsModel(TestCase):


    def setUp(self):
        self.PATH = r'TestSettingsModel.sqlite'
        self.logger = logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))

        self.dbconfig = {'sqlalchemy.echo': False, 'sqlalchemy.url': 'sqlite:///' + self.PATH}

        if os.path.exists(self.PATH):
            os.remove(self.PATH)

        self.engine = engine_from_config(self.dbconfig)
        systemcheck.models.meta.base.Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind=self.engine)
        self.session = scoped_session(self.session_factory)

        if self.session.query(GenericSystemTreeNode).filter(GenericSystemTreeNode.parent_id == None).count() == 0:
            self.session.add(GenericSystemTreeNode(name='RootNode'))
            self.session.commit()

        self.populate_tree()
        rootnode = self.session.query(GenericSystemTreeNode).filter(GenericSystemTreeNode.parent_id == None).one()
        self.model = GenericTreeModel(rootnode=rootnode, treenode=GenericSystemTreeNode)

    def tearDown(self):

        self.session.close()
        if os.path.exists(self.PATH):
            os.remove(self.PATH)

    def populate_tree(self):
        tools.populateSystemsABAPTree(self.session)

    def test_columnCount(self):
        dev_index = self.model.index(0, 0, QtCore.QModelIndex())
        system_index = self.model.index(0, 0, dev_index)
        system_tree_node = system_index.internalPointer()
        self.assertEqual(system_tree_node.sid, 'E1D')

        settings_model = SettingsModel(system_tree_node)
        column_count = settings_model.columnCount()
        self.assertEqual(column_count, 16)
        self.assertEqual(column_count, system_tree_node._qt_column_count())

    def test_data(self):
        dev_index = self.model.index(0, 0, QtCore.QModelIndex())
        system_index = self.model.index(0, 0, dev_index)
        system_tree_node = system_index.internalPointer()
        self.assertEqual(system_tree_node.sid, 'E1D')

        settings_model = SettingsModel(system_tree_node)
        for colnr, column in enumerate(system_tree_node.__qtmap__):
            index = settings_model.index(0, colnr, QtCore.QModelIndex())
            self.assertEqual(settings_model.data(index,QtCore.Qt.DisplayRole), getattr(system_tree_node, column.name))
