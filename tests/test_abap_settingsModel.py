
import os

import systemcheck.model as model
from systems.generic.gui.model import SystemTreeModel, SettingsModel
from systemcheck.model.systems import AbapClient, Credential
from systems.ABAP.model.abap_model import AbapTreeNode, AbapSystem
from systemcheck.model.meta.base import scoped_session, sessionmaker, engine_from_config
import logging

from PyQt5 import QtCore

from unittest import TestCase



class TestSettingsModel(TestCase):


    def setUp(self):
        self.PATH = r'D:\Python\Projects\systemcheck\tests\{}.sqlite'.format(self.__class__.__name__)
        self.logger = logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))

        self.dbconfig = {'sqlalchemy.echo': False, 'sqlalchemy.url': 'sqlite:///' + self.PATH}

        if os.path.exists(self.PATH):
            os.remove(self.PATH)

        self.engine = engine_from_config(self.dbconfig)
        model.meta.base.Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind=self.engine)
        self.session = scoped_session(self.session_factory)

        if self.session.query(AbapTreeNode).filter(AbapTreeNode.type == 'ROOT').count() == 0:
            self.session.add(AbapTreeNode(type='ROOT', name='RootNode'))
            self.session.commit()

        self.populate_tree()

    def tearDown(self):

        self.session.close()
        if os.path.exists(self.PATH):
            os.remove(self.PATH)

    def populate_tree(self):

        rootnode = self.session.query(AbapTreeNode).filter_by(type='ROOT').first()

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
                              use_snc=True,
                              default_client='100',
                              ms_hostname='sape1d.team-fasel.lab',
                              ms_sysnr='00',
                              ms_logongroup='PUBLIC')

        e1d_node.abap_system = e1d_abap

        e1s_node = AbapTreeNode(type='ABAP', parent_node=sbx_folder, name='E1S')
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
        e1s_node.abap_system = e1s_abap

        self.logger.info('Generated Tree: ' + rootnode._dump())
        self.session.commit()

        self.treemodel = SystemTreeModel(rootnode)


    def test_columnCount(self):

        dev_index = self.treemodel.index(0, 0, QtCore.QModelIndex())
        system_index = self.treemodel.index(0, 0, dev_index)
        system_tree_node = system_index.internalPointer()
        system_node = system_tree_node._system_node()
        self.assertEqual(system_node.sid, 'E1D')

        settings_model = SettingsModel(system_node)
        column_count = settings_model.columnCount()
        self.assertEqual(column_count, 15)
        self.assertEqual(column_count, system_node._visible_column_count())

    def test_data(self):
        dev_index = self.treemodel.index(0, 0, QtCore.QModelIndex())
        system_index = self.treemodel.index(0, 0, dev_index)
        system_tree_node = system_index.internalPointer()
        system_node = system_tree_node._system_node()
        self.assertEqual(system_node.sid, 'E1D')

        settings_model = SettingsModel(system_node)
        index = settings_model.index(0, 0, QtCore.QModelIndex())
        sid_from_model = settings_model.data(index, QtCore.Qt.DisplayRole)
        self.assertEqual(sid_from_model, 'E1D')

#    def test_flags(self):


#    def test_setData(self):
#        self.fail()

    def test_index(self):
        dev_index = self.treemodel.index(0, 0, QtCore.QModelIndex())
        system_index = self.treemodel.index(0, 0, dev_index)
        system_tree_node = system_index.internalPointer()
        system_node = system_tree_node._system_node()
        self.assertEqual(system_node.sid, 'E1D')

        settings_model = SettingsModel(system_node)
        index = settings_model.index(0, 0, QtCore.QModelIndex())
        sid_from_model = settings_model.data(index, QtCore.Qt.DisplayRole)
        self.assertEqual(sid_from_model, 'E1D')

