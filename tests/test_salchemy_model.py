# -*- coding: utf-8 -*-

""" Tests for the SQLAlchemy Model


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
from systemcheck.model.systems import AbapSystem, AbapClient, SystemTreeNode, Credential
from systemcheck.model.meta.base import scoped_session, sessionmaker, engine_from_config


class MonolithicTestSqlalchemyModel(unittest.TestCase):

    PATH=r'D:\Python\Projects\systemcheck\tests'

    def setUp(self):
        self.dbconfig = dict(TEST_CONFIG['systems-db'])

        self.path_to_db=os.path.join(self.PATH, self.dbconfig['dbname'])

        if os.path.exists(self.path_to_db):
            os.remove(self.path_to_db)

        if self.dbconfig.get('dbtype') == 'sqlite':
            sqliteurl = self.dbconfig['sqlalchemy.url']
            sqliteurl = sqliteurl.replace('{systemchecktestpath}', self.path_to_db)

            self.dbconfig['sqlalchemy.url'] = sqliteurl.replace('\\', '/')
        else:
            raise ValueError('Unsupported DB type in settings.ini for systems-db')

        self.engine = engine_from_config(self.dbconfig)
        model.meta.base.Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind=self.engine)
        model.meta.base.Base.metadata.create_all(self.engine)
        self.session = scoped_session(self.session_factory)

        if self.session.query(SystemTreeNode).filter(SystemTreeNode.type=='ROOT').count() == 0:
            self.session.add(SystemTreeNode(type='ROOT'))
            self.session.commit()

    def _steps(self):
        for name in sorted(dir(self)):
            if name.startswith("step"):
                yield name, getattr(self, name)

    def step_001_find_root_element(self):
        """ Validate that exactly one root object exists """

        rootcount=self.session.query(SystemTreeNode).filter(SystemTreeNode.type=='ROOT').count()
        assert rootcount==1

    def test_steps(self):
        for name, step in self._steps():
            try:
                step()
            except Exception as e:
                self.fail("{} failed ({}: {})".format(step, type(e), e))

    # pprint(result)


    def tearDown(self):

        self.session.close()
        if os.path.exists(self.path_to_db):
            os.remove(self.path_to_db)
