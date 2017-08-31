from unittest import TestCase
from PyQt5 import QtWidgets, QtCore, QtGui
import logging
import os
import systemcheck.models as models
from systemcheck.checks.models.checks import Check
from systemcheck.gui.models import GenericTreeModel
from systemcheck.models.meta.base import engine_from_config, scoped_session, sessionmaker
from systemcheck.systems.ABAP.plugins.actions.check_abap_count_table_entries import CheckAbapCountTableEntries, \
    CheckAbapCountTableEntries__params
from systemcheck.systems.ABAP.models import CheckABAPFolder
from systemcheck.gui.models import PolyMorphicFilterProxyModel

from . import tools


class TestPolyMorphicFilterProxyModel(TestCase):

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

        self.filter=[Check, CheckABAPFolder]
        self.all = [Check, CheckABAPFolder, CheckAbapCountTableEntries, CheckAbapCountTableEntries__params]

    def tearDown(self):

        self.session.close()
        if os.path.exists(self.PATH):
            os.remove(self.PATH)


    def test_filterAcceptsRow(self):
        tools.populateChecksTree(self.session)
        rootnode = self.session.query(Check).filter_by(parent_id=None).first()
        model = GenericTreeModel(rootnode, treenode=Check)

        filter_model=PolyMorphicFilterProxyModel(filterClasses=self.filter)
        filter_model.setSourceModel(model)

        rootindex=QtCore.QModelIndex()
        self.assertEqual(model.rowCount(rootindex), 2)
        self.assertEqual(filter_model.rowCount(rootindex), 2)
        index=model.index(1, 0, rootindex)  #Folder "Basis"
        self.assertEqual(model.rowCount(index), 1)
        self.assertEqual(model.data(index, QtCore.Qt.DisplayRole), 'Basis')
        self.assertEqual(model.rowCount(index), 1)
        index=model.index(0, 0, index)
        self.assertEqual(model.data(index, QtCore.Qt.DisplayRole), 'Post Install')
        self.assertEqual(model.rowCount(index), 1)
        index=model.index(0, 0, index)
        self.assertEqual(model.data(index, QtCore.Qt.DisplayRole), 'Clients 001 and 066 removed')

        filter_index=filter_model.index(1, 0, rootindex)
        self.assertEqual(filter_model.data(filter_index, QtCore.Qt.DisplayRole), 'Basis')
        filter_index=filter_model.index(0, 0, filter_index)
        self.assertEqual(filter_model.data(filter_index, QtCore.Qt.DisplayRole), 'Post Install')
        self.assertEqual(filter_model.rowCount(filter_index), 0)