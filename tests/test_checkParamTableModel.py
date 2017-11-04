from unittest import TestCase
import logging
import os
import systemcheck.models as models
from systemcheck.checks.models.checks import Check
from systemcheck.gui.models import GenericTreeModel
from systemcheck.models.meta.base import engine_from_config, scoped_session, sessionmaker
from systemcheck.systems.ABAP.plugins.actions.check_abap_count_table_entries import CheckAbapCountTableEntries, \
    CheckAbapCountTableEntries__params
from PyQt5 import QtCore, QtWidgets, QtGui
import systemcheck_tools


from systemcheck.checks.gui.widgets.check_parameterEditor_widget import CheckParameterTableModel

class TestCheckParamTableModel(TestCase):

    PATH = r'TestCheckParamTableModel.sqlite'

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

        if self.session.query(Check).filter(Check.parent_id == None).count() == 0:
            self.session.add(Check(name='RootNode'))
            self.session.commit()

    def tearDown(self):

        self.session.close()
        if os.path.exists(self.PATH):
            os.remove(self.PATH)

    def populateTree(self):
        systemcheck_tools.populateChecksTree(self.session)
        self.check=self.session.query(CheckAbapCountTableEntries).filter_by(name='Clients 001 and 066 removed').one()


    def test_rowCount(self):
        self.populateTree()
        model = CheckParameterTableModel(self.check)
        self.assertEqual(model.rowCount(), 2)


    def test_columnCount(self):
        self.populateTree()
        model = CheckParameterTableModel(self.check)
        self.assertEqual(model.columnCount(), 1)


    def test_data(self):

        test_data = [['Client 001'],
                     ['Client 066']]

        self.populateTree()
        model = CheckParameterTableModel(self.check)

        for rownr in range(model.rowCount()):
            for colnr in range(model.columnCount()):
                idx = model.index(rownr, colnr)
                self.assertEqual(model.data(idx), test_data[rownr][colnr])



    def test_setData(self):

        test_data = [['Client 001_modified'],
                     ['Client 066_modified']]

        self.populateTree()
        model = CheckParameterTableModel(self.check)

        for rownr in range(model.rowCount()):
            for colnr in range(model.columnCount()):
                idx = model.index(rownr, colnr)
                model.setData(idx, test_data[rownr][colnr], QtCore.Qt.EditRole )

        for rownr in range(model.rowCount()):
            for colnr in range(model.columnCount()):
                idx = model.index(rownr, colnr)
                self.assertEqual(model.data(idx), test_data[rownr][colnr])



    def test_insertRows(self):

        new_data = ['999', 'MANDT999', "MANDT EQ '001' 999", 0, 'EQ999']

        self.populateTree()
        model = CheckParameterTableModel(self.check)
        self.assertEqual(model.rowCount(), 2)

        model.insertRows(0, 10)
        self.assertEqual(model.rowCount(), 12)

    def test_removeRows(self):

        new_data = ['999', 'MANDT999', "MANDT EQ '001' 999", 0, 'EQ999']

        self.populateTree()
        model = CheckParameterTableModel(self.check)
        self.assertEqual(model.rowCount(), 2)

        model.removeRows(1, 0)