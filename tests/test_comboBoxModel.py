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


from systemcheck.models import meta
from systemcheck.gui.utils import ComboBoxModel

class TestComboboxModel(unittest.TestCase):


    def test_find_root_element(self):

        operations=meta.OperatorChoice()
        model=ComboBoxModel(operations.CHOICES)

        self.assertEqual(model.rowCount(), len(operations.CHOICES))

    def test_loop(self):

        operations=meta.OperatorChoice()
        operators = meta.Operators()
        model=ComboBoxModel(operations.CHOICES)

        self.assertEqual(model.columnCount(), 2)

        for row in range(model.rowCount()):
            index1 = model.index(row, 0)
            index2 = model.index(row, 1)

            value=model.data(index1)
            data=model.data(index2)

            newdata = operators.lookup(value)
            print('{}: {}/{}'.format(value, data, newdata))
            self.assertEqual(data, operators.lookup(value), msg='{}: {}/{}'.format(value, data, newdata))
