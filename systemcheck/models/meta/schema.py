import sqlalchemy
from inspect import isclass
from sqlalchemy import ForeignKey, Table, DateTime, Integer, CHAR, inspect, String
from sqlalchemy import event, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.sql import functions
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils.types import UUIDType
from typing import Any, Union, List
import keyring
import uuid

def bool_or_str(type_):
    return is_string(type_) or is_boolean(type_)


class Column(sqlalchemy.Column):
    """ Customized Column Type

    The customized column type is used to provide information to the Qt layer when building dynamic user interfaces.
    """
    def __init__(self, *args, **kwargs):
        """ Supported Init Variables

        The following variables are supported and are primarily intended to allow the dynamic generation of Qt forms:

        :param qt_choices: possible values
        :type dict:
        :param qt_label: The label text that gets displayed in the UI
        :type str:
        :param qt_description: A description that gets displayed in the UI when hovering over a field.
        :type str:
        :param qt_show: Flag that determines whether a column should be displayed in a dynamically generated UI. By
        :type bool:
        """

        kwargs.setdefault('info', {})

        kwargs['info'].setdefault('choices', kwargs.pop('choices', None))
        kwargs['info'].setdefault('qt_label', kwargs.pop('qt_label', ''))
        kwargs['info'].setdefault('qt_description', kwargs.pop('qt_description', ''))
        kwargs['info'].setdefault('qt_show', kwargs.pop('qt_show', True))

        sqlalchemy.Column.__init__(self, *args, **kwargs)

    @property
    def choices(self):
        return self.info['choices'] if 'choices' in self.info else []

class QtModelMixin(object):

    def _column_count(self)->int:
        """ Return the number of columns """
        return len(self.__table__.columns)

    def _colnr_is_valid(self, colnr:int)->bool:

        if colnr>=0 and colnr < len(self.__table__.columns):
            return True
        return False

    def _commit(self):
        session = inspect(self).session
        session.commit()

    def _flush(self):
        session = inspect(self).session
        session.flush()

    def _info_by_colnr(self, colnr:int)->Union[dict, bool]:
        """ Return the info metadata for any column"""
        if self._colnr_is_valid(colnr):
            value=list(self.__table__.columns)[colnr].info
            return value
        else:
            return False

    def _info_by_visible_colnr(self, colnr:int)->Union[dict, bool]:
        """ Return the info metadata for a visible column"""
        if self._visible_colnr_is_valid(colnr):
            visible_columns=self._visible_columns()
            value=visible_columns[colnr].info
            return value
        else:
            return False

    def _set_value_by_colnr(self, colnr:int, value:object):
        """ Get the Value of a Column by its Number

        QtModels refer to the underlying data by rows and columns. Somewhere a mapping has to occur that does this
        automatically.

        :param colnr: The Qt Column Number
        :type int:


        """

        #TODO: The implementation here is quite ugly. Need to find a better way to do this, but for now it's acceptable

        if self._colnr_is_valid(colnr):
            setattr(self, list(self.__table__.columns)[colnr].name, value)
            self._flush()
            return True
        else:
            return False

    def _set_value_by_visible_colnr(self, colnr:int, value:object):
        """ Set the Value of a Column by its its visible Number

        QtModels refer to the underlying data by rows and columns. Somewhere a mapping has to occur that does this
        automatically.

        :param colnr: The Qt Column Number
        :type int:
        :param value: The value to be set in the column


        """

        #TODO: The implementation here is quite ugly. Need to find a better way to do this, but for now it's acceptable

        if self._visible_colnr_is_valid(colnr):
            visible_columns=self._visible_columns()
            setattr(self, visible_columns[colnr].name, value)
            self._commit()
            return True
        else:
            return False

    def _visible_headers(self):

        return [colData.info.get('qt_label')
                for colData in self.__table__.columns
                if colData.info.get('qt_show')]

    def _value_by_colnr(self, colnr:int)->object:
        """ Get the Value of a Column by its Number

        QtModels refer to the underlying data by rows and columns. Somewhere a mapping has to occur that does this
        automatically.

        :param colnr: The Qt Column Number
        :type int:


        """

        #TODO: The implementation here is quite ugly. Need to find a better way to do this, but for now it's acceptable

        if self._colnr_is_valid(colnr):
            value=getattr(self, list(self.__table__.columns)[colnr].name)
            return value
        else:
            return None

    def _value_by_visible_colnr(self, colnr: int) -> object:
        """ Get the Value of a Column by its its visible Number

        QtModels refer to the underlying data by rows and columns. Somewhere a mapping has to occur that does this
        automatically.

        :param colnr: The Qt Column Number
        :type int:


        """


        #TODO: The implementation here is quite ugly. Need to find a better way to do this, but for now it's acceptable

        if self._visible_colnr_is_valid(colnr):
            visible_columns=self._visible_columns()
            value=getattr(self, visible_columns[colnr].name)
            return value
        else:
            return False

    def _visible_columns(self)->List[Any]:
        """ Return a list of columns that have the info medatadata variable qt_show set to True"""
        return [colData
                for colData in self.__table__.columns
                if colData.info.get('qt_show')]

    def _visible_column_count(self)->int:
        """Returns the number of visible Columns


        This is required due to the issue that you can't hide the first column of the QTreeView. If you hide the first column,
        all you see are entries immediately under the root node. The first column however is usually a primary key or something
        else that is not relevant for processing.

        The primary key is also determined automatically when inserting a new record and does not need to be maintained
        manually. Due to this, the handling of visible and invisible columns needs to get added to the tree handling.

        Here, we only return the visible column count.
        """
        visible_columns=self._visible_columns()
        return len(visible_columns)

    def _visible_colnr_is_valid(self, colnr:int)->bool:
        """ Validate that the column number is ok fo a visible column"""

        visible_columns=self._visible_columns()

        if colnr>=0 and colnr < len(visible_columns):
            return True
        return False

class PasswordKeyringMixin():


    keyring_uuid = Column(String(32), qt_show=False)

    @hybrid_property
    def password(self):
        namespace='systemcheck'
        keyring_user=self.keyring_uuid
        pwd = keyring.get_password(namespace, username=keyring_user)
        return pwd

    @password.setter
    def password(self, password):
        namespace='systemcheck'
        pwd = password
        keyring_username=self.keyring_uuid
        keyring.set_password(namespace, username=keyring_username, password=pwd)



def is_string(type_):
    return (
        isinstance(type_, sqlalchemy.String) or
        (isclass(type_) and issubclass(type_, sqlalchemy.String))
    )


def is_boolean(type_):
    return (
        isinstance(type_, sqlalchemy.Boolean) or
        (isclass(type_) and issubclass(type_, sqlalchemy.Boolean))
    )


def is_numeric(type_):
    return any(
        isinstance(type_, type_cls)
        for type_cls in (sqlalchemy.Integer, sqlalchemy.Float, sqlalchemy.Numeric)
    )


class SurrogatePK(object):
    """A mixin that adds a surrogate integer 'primary key' column named
    ``id`` to any declarative-mapped class."""

    id = Column(Integer, primary_key=True)


class SurrogateUuidPK(object):
    """A mixin that adds a surrogate UUID 'primary key' column named
    ``id`` to any declarative-mapped class."""

    id = Column(UUIDType(binary=False), primary_key=True)


class References(object):
    """A mixin which creates foreign key references to related classes."""
    _to_ref = set()
    _references = _to_ref.add

    @classmethod
    def __declare_first__(cls):
        """declarative hook called within the 'before_configure' mapper event."""
        for lcl, rmt in cls._to_ref:
            cls._decl_class_registry[lcl]._reference_table(
                cls._decl_class_registry[rmt].__table__)
        cls._to_ref.clear()

    @classmethod
    def _reference_table(cls, ref_table):
        """Create a foreign key reference from the local class to the given remote
        table.

        Adds column references to the declarative class and adds a
        ForeignKeyConstraint.

        """
        # create pairs of (Foreign key column, primary key column)
        cols = [(Column(), refcol) for refcol in ref_table.primary_key]

        # set "tablename_colname = Foreign key Column" on the local class
        for col, refcol in cols:
            setattr(cls, "%s_%s" % (ref_table.name, refcol.name), col)

        # add a ForeignKeyConstraint([local columns], [remote columns])
        cls.__table__.append_constraint(ForeignKeyConstraint(*zip(*cols)))


class utcnow(functions.FunctionElement):
    key = 'utcnow'
    type = DateTime(timezone=True)



