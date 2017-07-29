from systemcheck.models.checks import Check
from systemcheck.systems.ABAP.plugins.checks.check_abap_count_table_entries import CheckAbapCountTableEntries, CheckAbapCountTableEntries__params
from unittest import TestCase

import systemcheck.models as models
from systemcheck.session import SESSION
from systemcheck.models.credentials import Credential
from systemcheck.models.meta.base import scoped_session, sessionmaker, engine_from_config
import sqlalchemy_utils
import logging
import os

class TestChecks(TestCase):

    #TODO: clean up and align with PyCharm testing integration

    PATH=r'test_Checks.sqlite'

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

    def tearDown(self):

        self.session.close()
        if os.path.exists(self.PATH):
            os.remove(self.PATH)


    def test_CheckAbapCountTableEntries(self):

        check=CheckAbapCountTableEntries(name = 'Clients 001 and 066 removed',
                                         description = 'If client 001 is not actively used, it can be deleted. Client 066 is no longer required in any case',
                                         )


        param001 = CheckAbapCountTableEntries__params(
                                         table_name = 'T000',
                                         table_fields = 'MANDT',
                                         expected_count = 0,
                                         operator = 'NE',
                                         where_clause = "MANDT EQ '001'"
                                         )
        param066 = CheckAbapCountTableEntries__params(
                                         table_name = 'T000',
                                         table_fields = 'MANDT',
                                         expected_count = 0,
                                         operator = 'NE',
                                         where_clause = "MANDT EQ '066'"
                                         )
        check.params.append(param001)
        check.params.append(param066)

        self.session.add(check)
        self.session.commit()