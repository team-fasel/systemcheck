from unittest import TestCase
from systemcheck.models.meta.systemcheck_choices import Operators, OperatorChoice


class TestOperators(TestCase):

    def setUp(self):
        self.choice = OperatorChoice()
        self.operators = Operators()

    def test__to_int(self):

        values=[('123', 123, 554),
                (123, 123, 332),
                (123, 123, None)]

        for value1, value2, value3 in values:
            value1, value2, value3 = self.operators._to_int(value1, value2, value3)
            if value1:
                self.assertIsInstance(value1, int)
            if value2:
                self.assertIsInstance(value2, int)
            if value3:
                self.assertIsInstance(value3, int)

    def test__to_str(self):

        values=[('123', 123, 554),
                (123, 123, 332),
                (123, 123, None)]

        for value1, value2, value3 in values:
            value1, value2, value3 = self.operators._to_str(value1, value2, value3)
            if value1:
                self.assertIsInstance(value1, str)
            if value2:
                self.assertIsInstance(value2, str)
            if value3:
                self.assertIsInstance(value3, str)

    def test__to_float(self):

        values=[('123.23', 123, 554),
                (123.23, 123, 332),
                (123.23, 123, None)]

        for value1, value2, value3 in values:
            value1, value2, value3 = self.operators._to_float(value1, value2, value3)
            if value1:
                self.assertIsInstance(value1, float)
            if value2:
                self.assertIsInstance(value2, float)
            if value3:
                self.assertIsInstance(value3, float)

    def test_equal_not_equal(self):

        values = [(1, 1, True),
                  (1, 2, False),
                  ('1', 1, True),
                  (1, '1', True),
                  (1, '2', False),
                  ('123', 'ABC', False),
                  ('123', '123', True)]

        for value1, value2, expected in values:
            result = self.operators.operation('equal', value1, value2)
            self.assertEqual(expected, result)
            result = self.operators.operation(self.choice.EQ, value1, value2)
            self.assertEqual(expected, result)
            result = self.operators.operation('not equal', value1, value2)
            self.assertEqual(not expected, result)
            result = self.operators.operation(self.choice.NE, value1, value2)
            self.assertEqual(not expected, result)

    def test_lt(self):

        values = [(1, 1, False),
                  (1, 2, True),
                  ('1', 1, False),
                  (1, '1', False),
                  (1, '2', True),
                  (2, 1, False),
                  ('2', '1', False),
                  ('123', 'ABC', True),
                  ('123', '123', False)]

        for value1, value2, expected in values:
            result = self.operators.operation('lower', value1, value2)
            self.assertEqual(expected, result)

    def test_le(self):
        op = 'lower or equal'
        values = [(1, 1, True),
                  (1, 2, True),
                  ('1', 1, True),
                  (1, '1', True),
                  (1, '2', True),
                  (2, 1, False),
                  ('2', '1', False),
                  ('123', 'ABC', True),
                  ('123', '123', True)]

        for value1, value2, expected in values:
            result = self.operators.operation(op , value1, value2)
            self.assertEqual(expected, result, msg='Operation: {}, Value 1: {}, Value 2: {}'.format(op, value1, value2))

    def test_gt(self):
        op = 'greater'
        values = [(1, 1, False),
                  (1, 2, False),
                  ('1', 1, False),
                  (1, '1', False),
                  (1, '2', False),
                  (2, 1, True),
                  ('2', '1', True),
                  ('123', 'ABC', False),
                  ('123', '123', False)]

        for value1, value2, expected in values:
            result = self.operators.operation(op , value1, value2)
            self.assertEqual(expected, result, msg='Operation: {}, Value 1: {}, Value 2: {}'.format(op, value1, value2))

    def test_ge(self):
        op = 'greater or equal'
        values = [(1, 1, True),
                  (1, 0, True),
                  (1, 2, False),
                  ('1', 1, True),
                  (1, '1', True),
                  (1, '2', False),
                  (2, 1, True),
                  ('2', '1', True),
                  ('123', 'ABC', False),
                  ('123', '123', True)]

        for value1, value2, expected in values:
            result = self.operators.operation(op , value1, value2)
            self.assertEqual(expected, result, msg='Operation: {}, Value 1: {}, Value 2: {}'.format(op, value1, value2))

    def test_matches(self):

        op = 'matches'
        values = [('ABC', 'ABC', True),
                  ('.*', 'ABC', True),
                  ('[A-Z]BC', 'ABC', True),
                  ('[A-C]BC', 'DEF', False)]

        for value1, value2, expected in values:
            result = self.operators.operation(op , value1, value2)
            self.assertEqual(expected, result, msg='Operation: {}, Value 1: {}, Value 2: {}'.format(op, value1, value2))


    def test_matches_not(self):
        op = 'matches not'
        values = [('ABC', 'ABC', False),
                  ('.*', 'ABC', False),
                  ('[A-Z]BC', 'ABC', False),
                  ('[A-C]BC', 'DEF', True)]

        for value1, value2, expected in values:
            result = self.operators.operation(op , value1, value2)
            self.assertEqual(expected, result, msg='Operation: {}, Value 1: {}, Value 2: {}'.format(op, value1, value2))

    def test_between(self):

        op = 'between'

        values = [(1, 0, 10, True),
                  (1, 5, 10, False)]

        for value1, value2, value3, expected in values:
            result = self.operators.operation(op , value1, value2, value3)
            self.assertEqual(expected, result, msg='Operation: {}, Value 1: {}, Value 2: {}, Value 3: {}'.format(op, value1, value2, value3))

    def test_not_between(self):

        op = 'not between'

        values = [(1, 0, 10, False),
                  (1, 5, 10, True)]

        for value1, value2, value3, expected in values:
            result = self.operators.operation(op , value1, value2, value3)
            self.assertEqual(expected, result, msg='Operation: {}, Value 1: {}, Value 2: {}, Value 3: {}'.format(op, value1, value2, value3))
