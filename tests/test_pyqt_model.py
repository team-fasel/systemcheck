# -*- coding: utf-8 -*-

""" Tests for the Qt Models


"""

# define authorship information
__authors__     = ['Lars Fasel']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2017'
__license__     = 'MIT'

# maintanence information
__maintainer__  = 'Lars Fasel'
__email__       = 'systemcheck@team-fasel.com'

import unittest
import shutil
from pprint import pprint
import os

from config_for_test import TEST_CONFIG

import systemcheck.model as model
from systemcheck.gui.models import SystemTreeModel
from systemcheck.model.systems import AbapSystem, AbapClient, SystemTreeNode, Credential
from systemcheck.model.meta.base import scoped_session, sessionmaker, engine_from_config
import logging


from PyQt5 import QtWidgets, QtCore

class TestPyQtModel(unittest.TestCase):

    PATH=r'D:\Python\Projects\systemcheck\tests\test_pyqt_model.sqlite'
    logger=logging.getLogger(__name__)
    def setUp(self):
        self.dbconfig = {'sqlalchemy.echo' : True,
                         'sqlalchemy.url' : 'sqlite:///'+self.PATH,}


        if os.path.exists(self.PATH):
            os.remove(self.PATH)

        self.engine = engine_from_config(self.dbconfig)
        model.meta.base.Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind=self.engine)
        self.session = scoped_session(self.session_factory)

        if self.session.query(SystemTreeNode).filter(SystemTreeNode.type=='ROOT').count() == 0:
            self.session.add(SystemTreeNode(type='ROOT', name='RootNode'))
            self.session.commit()


    def test_001_instaniate_model(self):
        rootnode=rootnode = self.session.query(SystemTreeNode).filter_by(type='ROOT').first()
        model=SystemTreeModel(rootnode)

    def test_002_validate_root(self):
        rootnode=rootnode = self.session.query(SystemTreeNode).filter_by(type='ROOT').first()
        model=SystemTreeModel(rootnode)
        column_count=model.columnCount()
        self.logger.info("Column Count: {}".format(column_count))
        assert column_count == 2
        self.logger.info("Attempting to access root node through index")
        index=model.createIndex(0, 0, rootnode)
        assert index.isValid()
        type = model.data(index, QtCore.Qt.DisplayRole)
        assert type == 'ROOT'
        index=model.createIndex(0, 1, rootnode)
        name = model.data(index, QtCore.Qt.DisplayRole)
        assert name == 'RootNode'






#    def test_steps(self):
#        for name, step in self._steps():
#            try:
#                print('starting step')
#                step()
#            except Exception as e:
#                self.fail("{} failed ({}: {})".format(step, type(e), e))


    def tearDown(self):

        self.session.close()
        if os.path.exists(self.PATH):
            os.remove(self.PATH)
