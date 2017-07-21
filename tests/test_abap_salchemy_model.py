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


import systemcheck.models as models
from systemcheck.session import SESSION
from systemcheck.models.credentials import Credential
from systems.ABAP.models import AbapTreeNode, AbapSystem, AbapClient
from systemcheck.models.meta.base import scoped_session, sessionmaker, engine_from_config
import sqlalchemy_utils
import logging


class SqlalchemyAbapModel(unittest.TestCase):

    #TODO: clean up and align with PyCharm testing integration

    PATH=r'D:\Python\Projects\systemcheck\tests\test_systems.sqlite'

    def setUp(self):
        self.dbconfig = {'sqlalchemy.echo' : False,
                         'sqlalchemy.url' : 'sqlite:///'+self.PATH,}

        self.logger=logging.getLogger(__name__)
        if os.path.exists(self.PATH):
            os.remove(self.PATH)

        self.engine = engine_from_config(self.dbconfig)
        models.meta.base.Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind=self.engine)
        self.session = scoped_session(self.session_factory)

        if self.session.query(AbapTreeNode).filter(AbapTreeNode.type== 'ROOT').count() == 0:
            self.session.add(AbapTreeNode(type='ROOT', name='RootNode'))
            self.session.commit()

    def _steps(self):
        for name in sorted(dir(self)):
            if name.startswith("step"):
                yield name, getattr(self, name)


    def populate_tree(self):
        rootnode = self.session.query(AbapTreeNode).filter_by(parent_id=None).first()

        dev_folder = AbapTreeNode(type='FOLDER', name='DEV', parent_node=rootnode)
        qas_folder = AbapTreeNode(type='FOLDER', name='QAS', parent_node=rootnode)
        prd_folder = AbapTreeNode(type='FOLDER', name='PRD', parent_node=rootnode)
        sbx_folder = AbapTreeNode(type='FOLDER', name='SBX', parent_node=rootnode)

        e1d_node = AbapTreeNode(type='ABAP', parent_node=dev_folder, name='E1D')
        e1d_abap = AbapSystem(sid='E1D', tier='Dev', rail='N',
                              description='ECC Development System',
                              enabled=True,
                              snc_partnername="Fill SNC Name Here",
                              snc_qop='9',
                              use_snc=False,
                              default_client='100',
                              ms_hostname='sape1d.team-fasel.lab',
                              ms_sysnr='00',
                              ms_logongroup='PUBLIC')
        e1d_node.abap_system = e1d_abap

        e1d_client000 = AbapClient(client='000', username = 'TestUser', password = 'PassWord1', use_sso=False)
        e1d_client000_node = AbapTreeNode(type=e1d_client000.RELNAME, name='000', parent_node=e1d_node)
        e1d_client000_node.abap_client = e1d_client000
        e1d_client100 = AbapClient(client='100', username = 'TestUser', password = 'PassWord1', use_sso=False)
        e1d_client100_node = AbapTreeNode(type=e1d_client100.RELNAME, name='100', parent_node=e1d_node)
        e1d_client100_node.abap_client = e1d_client100

        e1s_abap = AbapSystem(sid='E1S', tier='Sandbox', rail='N',
                              description='ECC Sandbox System',
                              enabled=True,
                              snc_partnername="Fill SNC Name Here",
                              snc_qop='9',
                              use_snc=True,
                              default_client='100',
                              ms_hostname='sape1s.team-fasel.lab',
                              ms_sysnr='00',
                              ms_logongroup='PUBLIC')
        e1s_node = AbapTreeNode(type=e1s_abap.RELNAME, parent_node=sbx_folder, name='E1S')
        e1s_node.abap_system = e1s_abap

        e1s_client000 = AbapClient(client='000', username = 'TestUser', password = 'PassWord1', use_sso=True)
        e1s_client000_node = AbapTreeNode(type=e1s_client000.RELNAME, name='000', parent_node=e1s_node)
        e1s_client000_node.abap_client = e1s_client000
        e1s_client100 = AbapClient(client='100', username = 'TestUser', password = 'PassWord1', use_sso=True)
        e1s_client100_node = AbapTreeNode(type=e1s_client100.RELNAME, name='100', parent_node=e1s_node)
        e1s_client100_node.abap_client = e1s_client100

        pprint(rootnode._dump())
        self.session.commit()

    def test_find_root_element(self):
        """ Validate that exactly one root object exists """
        print('step_001: Finding Root Element')
        rootcount=self.session.query(AbapTreeNode).filter(AbapTreeNode.parent_id == None).count()
        self.assertEqual(rootcount, 1)

    def test_password(self):
        e1s_client000 = AbapClient(client='000', username = 'TestUser', password='PassWord1', use_sso=True)
        pwd = e1s_client000.password
        self.assertEqual(pwd, 'PassWord1')

    def test_logon_info(self):
        rootnode = self.session.query(AbapTreeNode).filter_by(parent_id=None).first()
        dev_folder = AbapTreeNode(type='FOLDER', name='DEV', parent_node=rootnode)
        e1d_node = AbapTreeNode(type='ABAP', parent_node=dev_folder, name='E1D')
        e1d_abap = AbapSystem(sid='E1D', tier='Dev', rail='N',
                              description='ECC Development System',
                              enabled=True,
                              snc_partnername="Fill SNC Name Here",
                              snc_qop='9',
                              use_snc=False,
                              default_client='100',
                              ms_hostname='sape1d.team-fasel.lab',
                              ms_sysnr='00',
                              ms_logongroup='PUBLIC')
        e1d_node.abap_system = e1d_abap

        e1d_client000 = AbapClient(client='000', username = 'TestUser', password = 'PassWord1', use_sso=False)
        e1d_client000_node = AbapTreeNode(type=e1d_client000.RELNAME, name='000', parent_node=e1d_node)
        e1d_client000_node.abap_client = e1d_client000

        logon_info = e1d_client000.login_info()
        self.assertEqual(logon_info, {'group': 'PUBLIC', 'mshost': 'sape1d.team-fasel.lab',  'msserv': '3600',
                                      'passwd': 'PassWord1',  'sysid': 'E1D', 'user': 'TestUser'})

        e1d_abap.use_snc = True
        e1d_client000.use_sso=True
        pprint(e1d_client000.login_info())
        self.assertEqual(e1d_client000.login_info(), {'group': 'PUBLIC', 'mshost': 'sape1d.team-fasel.lab',  'msserv': '3600',
                                         'snc_myname': 'p:CN=LARS@< please customize >',  'snc_partnername': 'Fill SNC Name Here',
                                         'snc_qop': '9', 'sysid': 'E1D'})


    def test_populate_tree(self):
        print('step_002: Populating Tree')
        self.populate_tree()
        rootnode=self.session.query(AbapTreeNode).filter(AbapTreeNode.parent_id == None).first()
        self.assertEqual(rootnode._child_count(), 4)


    def test_validate_child_names(self):
        print('step_004: validating child labels')
        self.populate_tree()
        rootnode=self.session.query(AbapTreeNode).filter(AbapTreeNode.parent_id == None).first()
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
        rootnode=self.session.query(AbapTreeNode).filter(AbapTreeNode.parent_id == None).first()
        assert rootnode._visible_column_count() == 1

    def test_insert_child_at_position(self):
        print('step_006: Insert child at a specific position')
        rootnode=self.session.query(AbapTreeNode).filter(AbapTreeNode.parent_id == None).first()
        position_folder=AbapTreeNode(type='FOLDER', parent_node=rootnode, name='Position Test')
        pos1_node = AbapTreeNode(type='FOLDER', parent_node=position_folder, name='Pos 1')
        pos2_node = AbapTreeNode(type='FOLDER', parent_node=position_folder, name='Pos 2')
        pos3_node = AbapTreeNode(type='FOLDER', parent_node=position_folder, name='Pos 3')

        pos4_node = AbapTreeNode(type='FOLDER', name='Pos 4')
        position_folder._insert_child(1, pos4_node)

        print(position_folder._dump())

        count=position_folder._child_count()
        self.assertEqual(count, 4)


    def test_delete_children(self):
        print('step_007: Delete child at a specific position')
        rootnode = self.session.query(AbapTreeNode).filter_by(parent_id=None).first()
        delete_folder=AbapTreeNode(type='FOLDER', parent_node=rootnode, name='Position Test')
        del1_node = AbapTreeNode(type='FOLDER', parent_node=delete_folder, name='Del 1')
        del2_node = AbapTreeNode(type='FOLDER', parent_node=delete_folder, name='Del 2')
        del3_node = AbapTreeNode(type='FOLDER', parent_node=delete_folder, name='Del 3')
        del4_node = AbapTreeNode(type='FOLDER', parent_node=delete_folder, name='Del 4')

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
        rootnode = self.session.query(AbapTreeNode).filter_by(parent_id=None).first()
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
