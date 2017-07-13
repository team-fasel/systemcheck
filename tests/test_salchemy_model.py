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


import systemcheck.model as model
from systemcheck import SESSION
from systemcheck.model.systems import AbapSystem, SystemTreeNode, Credential
from systemcheck.model.meta.base import scoped_session, sessionmaker, engine_from_config
import sqlalchemy_utils
import logging


class MonolithicTestSqlalchemyModel(unittest.TestCase):

    #TODO: clean up and align with PyCharm testing integration

    PATH=r'D:\Python\Projects\systemcheck\tests\test_systems.sqlite'

    def setUp(self):
        self.dbconfig = {'sqlalchemy.echo' : False,
                         'sqlalchemy.url' : 'sqlite:///'+self.PATH,}

        self.logger=logging.getLogger(__name__)
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

    def populate_tree(self):
        rootnode = self.session.query(SystemTreeNode).filter_by(type='ROOT').first()

        dev_folder = SystemTreeNode(type='FOLDER', name='DEV', parent_node=rootnode)
        qas_folder = SystemTreeNode(type='FOLDER', name='QAS', parent_node=rootnode)
        prd_folder = SystemTreeNode(type='FOLDER', name='PRD', parent_node=rootnode)
        sbx_folder = SystemTreeNode(type='FOLDER', name='SBX', parent_node=rootnode)

        e1d_node = SystemTreeNode(type='ABAP', parent_node=dev_folder, name='E1D')
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

        e1s_node = SystemTreeNode(type='ABAP', parent_node=sbx_folder, name='E1S')
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

    def test_find_root_element(self):
        """ Validate that exactly one root object exists """
        print('step_001: Finding Root Element')
        rootcount=self.session.query(SystemTreeNode).filter(SystemTreeNode.type=='ROOT').count()
        assert rootcount==1
        print('success: only one root element')


    def test_populate_tree(self):
        print('step_002: Populating Tree')
        self.populate_tree()
        rootnode=self.session.query(SystemTreeNode).filter(SystemTreeNode.name=='RoteNode').first()
        self.assertEqual(rootnode._child_count, 4)


    def test_validate_child_names(self):
        print('step_004: validating child labels')
        self.populate_tree()
        rootnode=self.session.query(SystemTreeNode).filter_by(type='ROOT').first()
        child=rootnode._child(0)
        assert child.name == 'DEV'
        child=rootnode._child(1)
        assert child.name == 'QAS'
        child=rootnode._child(2)
        assert child.name == 'PRD'
        child=rootnode._child(3)
        assert child.name == 'SBX'

    def test_visible_columns(self):
        print('step_005a: Validating Visible Column Count')
        self.populate_tree()
        rootnode = self.session.query(SystemTreeNode).filter_by(type='ROOT').first()
        assert rootnode._visible_column_count() == 1

    def test_insert_child_at_position(self):
        print('step_006: Insert child at a specific position')
        rootnode = self.session.query(SystemTreeNode).filter_by(type='ROOT').first()
        position_folder=SystemTreeNode(type='FOLDER', parent_node=rootnode, name='Position Test')
        pos1_node = SystemTreeNode(type='FOLDER', parent_node=position_folder, name='Pos 1')
        pos2_node = SystemTreeNode(type='FOLDER', parent_node=position_folder, name='Pos 2')
        pos3_node = SystemTreeNode(type='FOLDER', parent_node=position_folder, name='Pos 3')

        pos4_node = SystemTreeNode(type='ROLDER', name='Pos 4')
        position_folder._insert_child(1, pos4_node)

        position_folder._dump()

        testchild=position_folder._child(1)
        print(testchild.name)

    def test_delete_children(self):
        print('step_007: Delete child at a specific position')
        rootnode = self.session.query(SystemTreeNode).filter_by(type='ROOT').first()
        delete_folder=SystemTreeNode(type='FOLDER', parent_node=rootnode, name='Position Test')
        del1_node = SystemTreeNode(type='FOLDER', parent_node=delete_folder, name='Del 1')
        del2_node = SystemTreeNode(type='FOLDER', parent_node=delete_folder, name='Del 2')
        del3_node = SystemTreeNode(type='FOLDER', parent_node=delete_folder, name='Del 3')
        del4_node = SystemTreeNode(type='FOLDER', parent_node=delete_folder, name='Del 4')

        childcount=delete_folder._child_count()

        self.logger.info('Delete Folder has {} children'.format(childcount))
        assert delete_folder._child_count() == 4

        self.logger.info('Deleting child from position 2 (Del 3)'.format(childcount))
        delete_folder._remove_child(2)

        assert delete_folder._child_count() == 3
        deleted=delete_folder._child(2)
        assert deleted.name == 'Del 4'

    def test_delete_parent(self):
        self.populate_tree()
        rootnode = self.session.query(SystemTreeNode).filter_by(type='ROOT').first()
        self.assertEqual(rootnode._child_count(), 4)
        self.assertEqual(self.session.query(AbapSystem).count(), 2)
        rootnode._remove_child(0)
        self.assertEqual(rootnode._child_count(), 3)
        self.assertEqual(self.session.query(AbapSystem).count(), 1)

    # pprint(result)


    def tearDown(self):

        self.session.close()
        if os.path.exists(self.PATH):
            os.remove(self.PATH)
