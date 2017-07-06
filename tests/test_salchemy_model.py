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
from systemcheck import SESSION
from systemcheck.model.systems import AbapSystem, AbapClient, SystemTreeNode, Credential
from systemcheck.model.meta.base import scoped_session, sessionmaker, engine_from_config
import sqlalchemy_utils


class MonolithicTestSqlalchemyModel(unittest.TestCase):

    PATH=r'D:\Python\Projects\systemcheck\tests\test_systems.sqlite'

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

    def _steps(self):
        for name in sorted(dir(self)):
            if name.startswith("step"):
                yield name, getattr(self, name)

    def step_001_find_root_element(self):
        """ Validate that exactly one root object exists """
        print('step_001: Finding Root Element')
        rootcount=self.session.query(SystemTreeNode).filter(SystemTreeNode.type=='ROOT').count()
        assert rootcount==1

    def step_002_populate_tree(self):
        print('step_002: Populating Tree')

        rootnode = self.session.query(SystemTreeNode).filter_by(type='ROOT').first()

        dev_folder = SystemTreeNode(type='FOLDER', name='DEV', parent=rootnode)
        qas_folder = SystemTreeNode(type='FOLDER', name='QAS', parent=rootnode)
        prd_folder = SystemTreeNode(type='FOLDER', name='PRD', parent=rootnode)
        sbx_folder = SystemTreeNode(type='FOLDER', name='SBX', parent=rootnode)

        e1d_node = SystemTreeNode(type='ABAP', parent=dev_folder, name='E1D')
        e1d_abap = AbapSystem(sid='E1D', tier='Dev', rail='N',
                              description='ECC Development System',
                              enabled=True,
                              snc_partnername="Fill SNC Name Here",
                              snc_qop=9,
                              use_snc=True,
                              default_client='100',
                              ms_hostname='sape1d.team-fasel.lab',
                              ms_sysnr='00',
                              ms_logongroup='PUBLIC')

        e1d_node.abap_system = e1d_abap

        e1s_node = SystemTreeNode(type='ABAP', parent=sbx_folder, name='E1S')
        e1s_abap = AbapSystem(sid='E1S', tier='Sandbox', rail='N',
                              description='ECC Sandbox System',
                              enabled=True,
                              snc_partnername="Fill SNC Name Here",
                              snc_qop=9,
                              use_snc=True,
                              default_client='100',
                              ms_hostname='sape1s.team-fasel.lab',
                              ms_sysnr='00',
                              ms_logongroup='PUBLIC')
        e1s_node.abap_system = e1s_abap

        self.session.commit()

    def step_003_validate_model_count_root_children(self):
        print('step_003: validating model')
        rootnode=self.session.query(SystemTreeNode).filter_by(type='ROOT').first()
        childCount = rootnode._child_count()
        assert childCount == 4

    def step_004_validate_child_names(self):
        print('step_004: validating child labels')
        rootnode=self.session.query(SystemTreeNode).filter_by(type='ROOT').first()
        child=rootnode._child(0)
        assert child.name == 'DEV'
        child=rootnode._child(1)
        assert child.name == 'QAS'
        child=rootnode._child(2)
        assert child.name == 'PRD'
        child=rootnode._child(3)
        assert child.name == 'SBX'

    def step_005_validate_visible_columns(self):
        print('step_005a: Validating Visible Column Count')
        rootnode = self.session.query(SystemTreeNode).filter_by(type='ROOT').first()
        assert rootnode._visible_column_count() == 2

    def test_steps(self):
        for name, step in self._steps():
            try:
                print('starting step')
                step()
            except Exception as e:
                self.fail("{} failed ({}: {})".format(step, type(e), e))

    # pprint(result)


    def tearDown(self):

        self.session.close()
        if os.path.exists(self.PATH):
            os.remove(self.PATH)
