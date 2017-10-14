from PyQt5 import QtWidgets, QtCore, QtGui
from pprint import pprint
import logging
import os
import systemcheck.models as models
from systemcheck import plugins
from systemcheck.utils import get_or_create
from systemcheck.checks.models.checks import Check
from systemcheck.gui.models import GenericTreeModel
from systemcheck.models.meta.base import engine_from_config, scoped_session, sessionmaker
import systemcheck.systems.ABAP.plugins.actions.check_abap_count_table_entries
from systemcheck.systems.ABAP.models import ActionAbapFolder
from systemcheck.gui.models import PolyMorphicFilterProxyModel
import unittest
from systemcheck_tools import populateChecksTree, populateSystemsABAPTree


class TestSystemCheckPM(unittest.TestCase):

    PATH = 'TestPolyMorphicFilterProxyModel.sqlite'

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

        populateChecksTree(self.session)

    def tearDown(self):

        self.session.close()
        if os.path.exists(self.PATH):
            os.remove(self.PATH)


    def test_pluginInitialization(self):

        pm = plugins.SysCheckPM()
        map = pm.pluginObjectMap()
        pprint(map)

    def test_mapping(self):

        print(systemcheck.systems.ABAP.plugins.actions.check_abap_count_table_entries.CheckAbapCountTableEntries.__name__)