import systemcheck
from systemcheck.models.meta.orm_choices import choices
import logging
import operator
import re
from pprint import pformat

@choices
class OperatorChoice:
    class Meta:
        NE = ['NE', 'not equal']
        EQ = ['EQ', 'equal']
        GT = ['GT', 'greater']
        GE = ['GE', 'greater or equal']
        LT = ['LT', 'lower']
        LE = ['LE', 'lower or equal']
        BE = ['BE', 'between']
        NB = ['NB', 'not between']
        INSTALLED = ['INSTALLED', 'installed']
        NOTINSTALLED = ['NOTINSTALLED', 'not installed']
        ACTIVE = ['ACTIVE', 'active']
        INACTIVE = ['INACTIVTE', 'inactive']
        MATCHES = ['MATCHES', 'matches']
        MATCHESNOT = ['MATCHESNOT', 'matches not']
        INCLUDED = ['INLUDED', 'included']
        NOTINCLUDED = ['NOTINCLUDED', 'not included']
        SET = ['SET', 'set']
        NOTSET = ['NOTSET', 'not set']

@choices
class ComparisonChoice:
    class Meta:
        NE = ['NE', 'not equal']
        EQ = ['EQ', 'equal']
        GT = ['GT', 'greater']
        GE = ['GE', 'greater or equal']
        LT = ['LT', 'lower']
        LE = ['LE', 'lower or equal']



@choices
class YesNoChoice:
    class Meta:
        YES = [True, 'Yes']
        NO = [False, 'No']

@choices
class TrueFalseChoice:
    class Meta:
        TRUE = [True, 'True']
        FALSE = [False, 'False']


@choices
class InclusionChoice:
    class Meta:
        INCLUDE = ['INCLUDE', 'include']
        EXCLUDE = ['EXCLUDE', 'exclude']


@choices
class ComponentChoice:
    class Meta:
        KERNEL = ['KERNEL', 'Kernel Version']
        KERNELPATCH = ['KERNELPATCH', 'Kernel Patch']
        COMPONENT = ['COMPONENT', 'Component/AddOn']
        COMPONENTVERSION = ['COMPONENTVERSION', 'Component Version']
        COMPONENTPATCH = ['COMPONENTPATCH', 'Component Patch']
        DBTYPE = ['DBTYPE', 'Database Type']
        DB = ['DB', 'Database']
        DBVERSION = ['DBVERSION', 'Database Version']
        DBPATCH = ['DBPATCH', 'Database Patchlevel']
        DBSCHEMA = ['DBSCHEMA', 'Database Schema']
        SID = ['SID', 'System ID']
        PARAMETER = ['PARAMETER', 'Parameter']
        HOSTNAME = ['HOSTNAME', 'Hostname']
        INSTANCE = ['INSTANCE', 'Instance']
        SYSNR = ['SYSNR', 'System Number']


@choices
class CodePageChoice:
    class Meta:
        UC = ['UC', 'Unicode']
        NUC = ['NUC', 'Non-Unicode']


@choices
class CheckFailCriteriaOptions:
    class Meta:
        FAIL_IF_ANY_FAILS = ['FAIL_IF_ANY_FAILS', 'Fail check if any parameter set fails']
        FAIL_IF_ALL_FAIL = ['FAIL_IF_ALL_FAIL', 'Fail check if all parameter sets fail']
        NO_RATING = ['NO_RATING', 'No Rating, just Information']


class Operators:

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.__operatorChoice=OperatorChoice()

        self.__int_description = dict()

        attribs = systemcheck.utils.get_user_attributes(OperatorChoice)
        attribs.remove('CHOICES')
        for attrib in attribs:
            item = getattr(self.__operatorChoice.Meta, attrib)
            self.__int_description[item[0]]=item[1]

        self.__str_operation = {
            'active': self._ACTIVE,
            'between': self._BETWEEN,
            'equal': self._EQ,
            'greater or equal': self._GE,
            'greater': self._GT,
            'inactive': self._INACTIVE,
            'included': self._INCLUDED,
            'installed': self._INSTALLED,
            'lower or equal': self._LE,
            'lower': self._LT,
            'matches': self._MATCHES,
            'matches not': self._MATCHESNOT,
            'not between': self._NOTBETWEEN,
            'not equal': self._NE,
            'not included': self._NOTINCLUDED,
            'not installed': self._NOTINSTALLED,
            'not set': self._NOTSET,
            'set': self._SET,
        }

    def lookup(self, value:int):
        """ Get String Representation for numeric value

        :param value: numeric value that represents the operation
        """

        operation = self.__int_description[value]
        return operation

    def operation(self, operation, value1, value2, value3=None):
        """ Execute Operation configured based on the numeric value


        """
        self.logger.debug("Execute Operation: %i, Value 1: %s, Value 2: %s, Value3: %s", operation, value1, value2, value3)
        value1, value2, value3 = self._convert_values(value1, value2, value3)

        if isinstance(operation, int):
            operation = self.__int_description[operation]

        result = self.__str_operation[operation](value1, value2, value3)
        return result

    def _to_int(self, value1, value2, value3=None):

        self.logger.debug("Convert to Integer. Value 1: %s, Value 2: %s, Value 3: %s",
                          pformat(value1), pformat(value2), pformat(value3))
        value1 = int(value1)
        value2 = int(value2)
        if value3:
            value3=int(value3)
        return value1, value2, value3

    def _to_float(self, value1, value2, value3=None):
        value1 = float(value1)
        value2 = float(value2)
        if value3:
            value3=float(value3)
        return value1, value2, value3

    def _to_str(self, value1, value2, value3=None):
        value1 = str(value1)
        value2 = str(value2)
        if value3:
            value3=str(value3)
        return value1, value2, value3

    def _convert_values(self, value1, value2, value3):
        """ Convert both values to identical types

        Comparisons are only possible with similar data types.
        """
        try:
            value1, value2, value3 = self._to_int(value1, value2, value3)
        except ValueError:
            try:
                value1, value2, value3 = self._to_float(value1, value2, value3)
            except ValueError:
                try:
                    value1, value2, value3 = self._to_str(value1, value2, value3)
                except ValueError:
                    self.logger.debug('conversions to int, float or string failed')

        return value1, value2, value3

    def _ACTIVE(self, component, *args, **kwargs):
        """ Check whether a component is active """

        raise NotImplemented

    def _BETWEEN(self, value, lower, upper, *args, **kwargs):
        """ Verify whether value is between two values

        :param value: corresponds to the configured value
        :param lower: the lower border
        :param upper: The upper border


        """
        return lower <= value <= upper

    def _EQ(self, value1, value2, *args, **kwargs):
        return operator.eq(value1, value2)

    def _GE(self, value1, value2, *args, **kwargs):
        return operator.ge(value1, value2)

    def _GT(self, value1, value2, *args, **kwargs):
        return operator.gt(value1, value2)

    def _INACTIVE(self, *args, **kwargs):
        raise NotImplemented

    def _INCLUDED(self, value1, value2,  *args, **kwargs):
        """ Checks whether value1 is contained in value2

        :param value1: correspnds to the expected value
        :param value2: corresponds to the configured value
        """

        return value1 in value2

    def _INSTALLED(self, component, *args, **kwargs):
        """ Check whether a component is installed.

        Needs to be reimplemented for specific use cases. For example ABAP systems or HANA systems need different procedures. """
        raise NotImplemented

    def _LE(self, value1, value2, *args, **kwargs):
        return operator.le(value1, value2)

    def _LT(self, value1, value2, *args, **kwargs):
        return operator.lt(value1, value2)

    def _MATCHES(self, pattern, string, *args, **kwargs):
        """ Checks whether pattern is included in string

        :param pattern: The regular expression pattern (Expected Value)
        :param string: The string that should be searched

        """

        if re.match(pattern, string):
            return True
        else:
            return False

    def _MATCHESNOT(self, value1, value2, *args, value3=None, **kwargs):
        """ A inverted match operator


        :param value1: The regular expression pattern
        :param value2: the sting that should be searched"""



        result = not self._MATCHES(value1, value2)
        return result

    def _NE(self, value1, value2, *args, **kwargs):
        return operator.ne(value1, value2)

    def _NOTACTIVE(self, component, *args, **kwargs):
        """ Check whether a component is not active """

        raise NotImplemented

    def _NOTBETWEEN(self, value1, value2, value3, *args, **kwargs):
        """ Inverted between check

        :param value1: check value
        :param value2: Lower value
        :param value3: upper value
        """
        return not self._BETWEEN(value1, value2, value3)

    def _NOTINCLUDED(self, value1, value2, *args, value3=None, **kwargs):
        """ Checks whether value1 is not included in value2 """

        return not value1 in value2

    def _NOTINSTALLED(self, component):
        """ Inverted install check.

        Needs to be reimplemented for specific use cases. For example ABAP systems or HANA systems need different procedures. """
        raise NotImplemented

    def _NOTSET(self, value1, value2, *args, value3=None, **kwargs):
        """ Check if something is not set.

        :param value1: corresponds to expected value, ignored for the "not set" check
        :param value2: corresonds to the configured value. Used for the "not set" check

        """

        result = value2 is not None
        return result

    def _SET(self, value1, value2, *args, value3=None, **kwargs):
        """ Check if something is set.

        :param value1: corresponds to expected value, ignored for the "set" check
        :param value2: corresonds to the configured value. Used for the "set" check

        """

        result = value2 == None
        return result

