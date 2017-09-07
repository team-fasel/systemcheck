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
from systemcheck.utils import get_or_create
from systemcheck.session import SESSION
from systemcheck.models.credentials import Credential
from systemcheck.systems.ABAP.models import SystemABAPFolder, SystemABAP, SystemABAPClient
from systemcheck.systems.generic.models import GenericSystemTreeNode
from systemcheck.models.meta.base import scoped_session, sessionmaker, engine_from_config
import sqlalchemy_utils
import logging
import systemcheck_tools


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

    def _steps(self):
        for name in sorted(dir(self)):
            if name.startswith("step"):
                yield name, getattr(self, name)


    def populate_tree(self):
        systemcheck_tools.populateSystemsABAPTree(self.session)

    def test_find_root_element(self):
        """ Validate that exactly one root object exists """
        print('step_001: Finding Root Element')
        self.populate_tree()
        rootcount=self.session.query(GenericSystemTreeNode).filter(GenericSystemTreeNode.parent_id == None).count()
        self.assertEqual(rootcount, 1)

    def test_password(self):
        self.populate_tree()

        e1s_client000 = SystemABAPClient(client='000', username ='TestUser', password='PassWord1', use_sso=True)
        pwd = e1s_client000.password
        self.assertEqual(pwd, 'PassWord1')

    def test_logon_info(self):
        rootnode = get_or_create(self.session, GenericSystemTreeNode, parent_id=None, name='RootNode')
        dev_folder = SystemABAPFolder(name='DEV', parent_node=rootnode)
        e1d_abap = SystemABAP(sid='E1D', tier='Dev', rail='N',
                              description='ECC Development System',
                              enabled=True,
                              snc_partnername="Fill SNC Name Here",
                              snc_qop='9',
                              use_snc=False,
                              default_client='100',
                              ms_hostname='sape1d.team-fasel.lab',
                              ms_sysnr='00',
                              ms_logongroup='PUBLIC')
        dev_folder.children.append(e1d_abap)

        e1d_client000 = SystemABAPClient(client='000', username ='TestUser', password ='PassWord1', use_sso=False)
        e1d_abap.children.append(e1d_client000)
        logon_info = e1d_client000.logon_info()

        self.assertDictEqual(logon_info, {'group': 'PUBLIC',
                                      'mshost': 'sape1d.team-fasel.lab',
                                      'msserv': '3600',
                                      'passwd': 'PassWord1',
                                      'sysid': 'E1D',
                                      'user': 'TestUser',
                                      'client':'000'})

        e1d_abap.use_snc = True
        e1d_client000.use_sso=True
        logon_info = e1d_client000.logon_info()
        self.assertDictEqual(e1d_client000.logon_info(), {'group': 'PUBLIC',
                                                      'mshost': 'sape1d.team-fasel.lab',
                                                      'msserv': '3600',
                                                      'snc_myname': 'p:CN=LARS@< please customize >',
                                                      'snc_partnername': 'Fill SNC Name Here',
                                                      'snc_qop': '9',
                                                      'sysid': 'E1D',
                                                          'client':'000'})


    def test_populate_tree(self):
        print('step_002: Populating Tree')
        self.populate_tree()
        rootnode=self.session.query(GenericSystemTreeNode).filter(GenericSystemTreeNode.parent_id == None).one()
        self.assertEqual(rootnode._qt_child_count(), 4)


    def test_validate_child_names(self):
        print('step_004: validating child labels')
        self.populate_tree()
        rootnode=self.session.query(GenericSystemTreeNode).filter(GenericSystemTreeNode.parent_id == None).one()
        child=rootnode._qt_child(0)
        assert child.name == 'DEV'
        child=rootnode._qt_child(1)
        assert child.name == 'QAS'
        child=rootnode._qt_child(2)
        assert child.name == 'PRD'
        child=rootnode._qt_child(3)
        assert child.name == 'SBX'

    def test_insert_child(self):
        print('step_006: Insert child at a specific position')
        self.populate_tree()
        rootnode=self.session.query(GenericSystemTreeNode).filter(GenericSystemTreeNode.parent_id == None).one()
        position_folder=SystemABAPFolder(parent_node=rootnode, name='Position Test')
        pos1_node = SystemABAPFolder(parent_node=position_folder, name='Pos 1')
        pos2_node = SystemABAPFolder(parent_node=position_folder, name='Pos 2')
        pos3_node = SystemABAPFolder(parent_node=position_folder, name='Pos 3')
        pos4_node = SystemABAPFolder(name='Pos 4')
        position_folder._qt_insert_child(1, pos4_node)

        print(position_folder._dump())

        count=position_folder._qt_child_count()
        self.assertEqual(count, 4)

    def test_delete_children(self):
        print('step_007: Delete child at a specific position')
        self.populate_tree()
        rootnode = self.session.query(GenericSystemTreeNode).filter_by(parent_id=None).one()
        delete_folder=SystemABAPFolder(parent_node=rootnode, name='Position Test')
        del1_node = SystemABAPFolder(parent_node=delete_folder, name='Del 1')
        del2_node = SystemABAPFolder(parent_node=delete_folder, name='Del 2')
        del3_node = SystemABAPFolder(parent_node=delete_folder, name='Del 3')
        del4_node = SystemABAPFolder(parent_node=delete_folder, name='Del 4')

        childcount=delete_folder._qt_child_count()

        self.logger.info('Delete Folder has {} children'.format(childcount))
        assert delete_folder._qt_child_count() == 4

        self.logger.info('Deleting child from position 2 (Del 3)'.format(childcount))
        delete_folder._qt_remove_child(2)

        assert delete_folder._qt_child_count() == 3
        deleted=delete_folder._qt_child(2)
        assert deleted.name == 'Del 4'

    def test_delete_parent(self):
        self.populate_tree()
        rootnode = self.session.query(GenericSystemTreeNode).filter_by(parent_id=None).one()
        self.assertEqual(rootnode._qt_child_count(), 4)
        self.assertEqual(self.session.query(SystemABAP).count(), 2)
        rootnode._qt_remove_child(0)
        self.assertEqual(rootnode._qt_child_count(), 3)
        self.assertEqual(self.session.query(SystemABAP).count(), 1)

    # pprint(result)


    def tearDown(self):

        self.session.close()
        if os.path.exists(self.PATH):
            os.remove(self.PATH)
