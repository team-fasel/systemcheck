import sqlalchemy
from uuid import UUID
import json
from datetime import datetime
from systemcheck.models.meta.systemcheck_choices import InclusionChoice, ComponentChoice, OperatorChoice
from inspect import isclass
from sqlalchemy import ForeignKey, Table, DateTime, Integer, CHAR, inspect, String, Date, Time
from sqlalchemy.orm import relationship, class_mapper, ColumnProperty,  RelationshipProperty
from sqlalchemy.orm.collections import InstrumentedDict, InstrumentedList, InstrumentedSet
from sqlalchemy import event, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.types import TypeDecorator
from sqlalchemy.sql import functions
from sqlalchemy.ext import declarative
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils.types import UUIDType, ChoiceType
from typing import Any, Union, List
import keyring
import uuid
from pprint import pprint
import systemcheck
from functools import reduce
from typing import Union
import yaml

import logging

logger = logging.getLogger(__name__)

def bool_or_str(type_):
    return is_string(type_) or is_boolean(type_)

def deepgetattr(obj, attr):
    """Recurses through an attribute chain to get the ultimate value."""
    return reduce(getattr, attr.split('.'), obj)


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
        kwargs['info'].setdefault('qt_enabled', kwargs.pop('qt_enabled', True))
        kwargs['info'].setdefault('rel_class', kwargs.pop('rel_class', None))

        sqlalchemy.Column.__init__(self, *args, **kwargs)

    @property
    def choices(self):
        return self.info['choices'] if 'choices' in self.info else []

class QtModelMixin(object):

    __qtmap__ = []

    __icon__ = None

    def _qt_column_count(self)->int:
        """ Return the number of columns """
        column_count=len(self.__qtmap__)
        return column_count

    def _qt_colnr_is_valid(self, colnr:int)->bool:
        column_count=self._qt_column_count()
        return 0 <= colnr < column_count


    def _qt_set_value_by_colnr(self, colnr: int, value: object):
        """ Set the Value of a Column by its its visible Number

        QtModels refer to the underlying data by rows and columns. Somewhere a mapping has to occur that does this
        automatically.

        :param colnr: The Qt Column Number
        :type int:
        :param value: The value to be set in the column


        """

        # TODO: The implementation here is quite ugly. Need to find a better way to do this, but for now it's acceptable

        if self._qt_colnr_is_valid(colnr):
            column = self.__qtmap__[colnr]
            setattr(self, column.name, value)
            self._commit()
            return True
        else:
            return False

    def _qt_headers(self):

        headers = []

        for column in self.__qtmap__:
            col_type = type(column)
            headers.append(col_type.info.get('qt_label'))

        return headers

    def _qt_header(self, column):

        if self._qt_colnr_is_valid(column):
            col = self.__qtmap__[column]
            header = col.info.get('qt_label')
            return header

        return False

    def _qt_data_colnr(self, colnr: int) -> object:
        """ Get the Value of a Column by its its visible Number

        QtModels refer to the underlying data by rows and columns. Somewhere a mapping has to occur that does this
        automatically.

        :param colnr: The Qt Column Number
        :type int:


        """

        # TODO: The implementation here is quite ugly. Need to find a better way to do this, but for now it's acceptable

        if self._qt_colnr_is_valid(colnr):
            #            visible_columns = self._visible_columns()
            try:
                column = self.__qtmap__[colnr]
                value = getattr(self, column.name)
                return value
            except Exception as err:
                pprint(err)
        else:
            return False

    def _qt_columns(self) -> List[Any]:
        """ Return a list of columns that have the info medatadata variable qt_show set to True"""
        return self.__qtmap__


    def _dump(self, _indent:int=0)->str:
        """ Recursively return the structure of the node and all its children as text """
        return "   " * _indent + repr(self) + \
            "\n" + \
            "".join([
                c._dump(_indent + 1)
                for c in self.children
            ])

    def _qt_child(self, childnr:int)->Any:
        """  Return the child object at a specific position"""
        if self._qt_child_count() >0:
            if childnr >= 0 and childnr<self._qt_child_count():
                return self.children[childnr]

        return False

    def _qt_child_count(self)->int:
        """ Return the number of children """
        return len(self.children)

    def _qt_insert_child(self, position:int, node)->bool:
        self.children.insert(position, node)
        self._commit()
        return True

    def _qt_row(self):
        if self.parent_node is not None:
            return self.parent_node.children.index(self)

    def _qt_remove_child(self, position:int)->bool:
        """ Remove a child item at a particular position

        :param position: The position within the list of children

        """
        if 0 <= position < self._qt_child_count():
            child=self._qt_child(position)

            session=inspect(child).session

            # Since we are using SQLAlchemy, we can't simply delete objects. If an object is part of a change that was not
            # committet yet, we need to use 'Session.expunge()' instead of 'Session.delete()'.
            if child in session.new:
                session.expunge(child)
            else:
                session.delete(child)
            session.commit()

        return True

    def _commit(self):
        session = systemcheck.session.SESSION
        session.commit()

    def _flush(self):
        session = systemcheck.session.SESSION
        session.flush()

class RestrictionsMixin:

    inclusion = Column(String,
                       name='inclusion',
                       qt_label='Incl./Excl.',
                       default=InclusionChoice.INCLUDE, choices=InclusionChoice.CHOICES)
    component = Column(String, name='component', qt_label='Component for restrictions', choices=ComponentChoice.CHOICES)
    component_name = Column(String, name='component_name', qt_label='Component Name')
    operator = Column(String, name='operator', qt_label='Restriction', choices=OperatorChoice.CHOICES)
    low = Column(String, name='low', qt_label='Lower', qt_description='Lower range value')
    high = Column(String, name='high', qt_label='High', qt_description='Higher range value')

    __qtmap__ = [inclusion, component, component_name, operator, low, high]

class OperatorMixin:

    operator = Column(Integer,
                      nullable=False, name='operator',
                      default=OperatorChoice.EQ,
                      qt_description='Comparison Operator',
                      qt_label='Comparison Operator',
                      qt_show=False,
                      choices=OperatorChoice.CHOICES
                      )

class TableNameMixin(object):
    """ MixIn to automatically return the table name """

    @declarative.declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class BaseMixin(object):
    """ Standard Mixin


    """

    @property
    def __relationships__(self):
        """
        Return a list of relationships name which are not as a backref
        name in model
        """
        back_ref_relationships = list()
        items = self.__mapper__.relationships.items()
        for (key, value) in items:
            if isinstance(value.backref, tuple):
                back_ref_relationships.append(key)
        return back_ref_relationships

    @declarative.declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @declarative.declared_attr
    def saClassName(cls):
        return cls.__name__.lower()

    def __iter__(self):
        return self.to_dict().items()

    def to_dict(self, *args, backref:tuple=None, include_relationships=True, ignore_keys=True,
                ignore_attrs:Union[list, None]=None,
                override_default_ignore_attrs:bool=False,
                rel_ignore_list=None,
                ignore_parents=True, **kwargs):
        """ Convert the values of a SQLAlchemy ORM Object into a dictionary


        :param backref: a tuple that consists of the table object as back reference and the primary key id of the record
        :param include_relationships: If set to False, only columns will be part of the dictionary
        :param ignore_keys: If set to True, the resulting dictionary will not include primary key values
        :param ignore_attributes: The list that contains the schema attributes that should be ignored.
        :param override_default_ignore_attrs: By default the attribute 'parent_node' is excluded
            since that would traverse the tree upwards. Had to be added since the the relationships for systemcheck
            are bidirectional.
        :param ignore_parents: If set to True, the attribute 'parent_node' will not get traversed.
        :param folder_as_attribute: a attribute called 'folder' will be added that contains the objects path from root downwards.
        """

        logger.debug('Converting to dictionary: %s', self.saClassName)

#        logger.debug('Name: %s', self.name)
        default_ignore_attrs=[]
        if ignore_attrs is None:
            ignore_attrs=default_ignore_attrs
        else:
            if override_default_ignore_attrs is False:
                ignore_attrs.extend(default_ignore_attrs)

        if ignore_parents:
            ignore_attrs.append('parent_node')

        primary_keys=[item.name for item in inspect(self.__class__).primary_key]
        foreign_keys=[item.name
                      for item in inspect(self.__class__).columns
                      if len(item.foreign_keys)>0]

        if ignore_keys:
            result = {str(column.key): getattr(self, attr)
                      for attr, column in self.__mapper__.c.items()
                      if str(column.key) not in primary_keys and column.key not in foreign_keys}
        else:
            result = {str(column.key): getattr(self, attr)
                      for attr, column in self.__mapper__.c.items()}

        if include_relationships:
            for attr, relation in self.__mapper__.relationships.items():
                # Avoid recursive loop between to tables.

                if relation.key not in ignore_attrs:
                    if backref is not None:
                        if relation.table._is_join:
                            if relation.table.right==backref[0] or relation.table.left==backref[0]:
                                continue

                        #
                        elif backref[0] == relation.target:
                            if backref[1] == self.id:
                                continue
#                        else:
#                            print('========== should not have happened ============')
#                            continue
                    value = getattr(self, attr)
                    if value is None:
                        result[str(relation.key)] = None
                    elif isinstance(value.__class__, declarative.DeclarativeMeta):
                        result[str(relation.key)] = value.to_dict(backref=(self.__table__, self.id))
                    else:
                        result[str(relation.key)] = [i.to_dict(backref=(self.__table__, self.id))
                                             for i in value]
        return result

    def to_json(self, *args, **kwargs):

        def extended_encoder(x):
            if isinstance(x, datetime):
                return x.isoformat()
            if isinstance(x, UUID):
                return str(x)

        return json.dumps(self.to_dict(*args, **kwargs))

    def to_yaml(self, *args, **kwargs):

        """ Converts the SQLAlchemy object to yaml


        """

        return yaml.dump(self.to_dict(*args, **kwargs))


class StandardAbapAuthSelectionOptionMixin:


    CHOICE_SIGN = [('I', 'Include'),
                   ('E', 'Exclude')]

    CHOICE_OPTION = [('EQ', 'Equal'),
                     ('NE', 'Not Equal'),
                     ('GT', 'Greater Than'),
                     ('GE', 'Greater or Equal'),
                     ('LT', 'Lower Than'),
                     ('LE', 'Lower or Equal')]

    SIGN = Column(ChoiceType(CHOICE_SIGN),
                  nullable = False,
                  default = 'I',
                  qt_label = 'Incl./Excl.',
                  qt_description = 'Should the specified items be included or excluded? Default is to include them',
                  choices = CHOICE_SIGN,
    )

    OPTION = Column(ChoiceType(CHOICE_SIGN),
                  nullable = False,
                  default = 'EQ',
                  qt_label = 'Sel. Option',
                  qt_description = 'Selection option',
                  choices = CHOICE_OPTION,
    )

    LOW = Column(String(12),
                 nullable=False,
                 qt_label='Lower Range Value',
                 qt_description='Lower Range Value. Must be specified.',
                )

    HIGH = Column(String(12),
                 nullable=True,
                 qt_label='Higher Range Value',
                 qt_description='Higher Range Value. Optional.',
                )

class PasswordKeyringMixin():


    keyring_uuid = Column(String(32), qt_show=False)

    @hybrid_property
    def password(self):
        namespace='systemcheck'
        keyring_user=self.keyring_uuid
        pwd = keyring.get_password(namespace, username=keyring_user)
        return pwd

    @password.setter
    def password(self, pwd):
        if pwd:
            namespace='systemcheck'
            keyring_username=self.keyring_uuid
            keyring.set_password(namespace, username=keyring_username, password=pwd)

class CheckParameterMixin(object):
    """ Name for Check Parameter Set

    A lot of checks will have multiple sets of parameters. These sets should have specific names to make navigating them
    easier in the user interface.

    """

    param_set_name = Column(String,
                        nullable=False,
                        qt_description='Name of the parameter set. It is easier to navigate a large list of parameter sets, if they have a descriptive name',
                        qt_label='Parameter Set Name',
                        qt_show=False,
                        default = 'Please Maintain'
                        )


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

class Password(TypeDecorator):

    impl = CHAR

    def process_bind_param(self, value, uuid):
        if value is None:
            return value
        keyring.set_password('systemcheck', username=uuid, password=value)

    def process_result_value(self, uuid):
        if uuid is None:
            return uuid
        else:
            return keyring.get_password('systemcheck', username=uuid)

class RichString(String):
    """ Represents a Rich String

    This column type will get mapped to a rich text editor in PyQt
    """

    def __init__(self):
        super().__init__()

class LongString(String):
    """ Represents a Long String

    This column type will get mapped to a the plain text editor in PyQt which allows the editing of larger texts

    """

    def __init__(self):
        super().__init__()

def qtRelationship(*args, **kwargs):

    kwargs.setdefault('info', {})

    info = {}

    info.setdefault('choices', kwargs.pop('choices', None))
    info.setdefault('qt_label', kwargs.pop('qt_label', ''))
    info.setdefault('qt_description', kwargs.pop('qt_description', ''))
    info.setdefault('qt_show', kwargs.pop('qt_show', True))
    info.setdefault('rel_class', kwargs.pop('rel_class', None))

    relation = relationship(*args, **kwargs)
    relation.info = info

    return relation