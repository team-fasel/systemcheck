import sqlalchemy
from inspect import isclass
from sqlalchemy import ForeignKey, Table, DateTime, Integer, CHAR
from sqlalchemy import event, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.sql import functions
from sqlalchemy_utils.types import UUIDType

def bool_or_str(type_):
    return is_string(type_) or is_boolean(type_)


class Column(sqlalchemy.Column):
    """ Customized Column Type

    The customized column type is used to provide information to the Qt layer when building dynamic user interfaces.
    """
    def __init__(self, *args, **kwargs):
        """ Supported Init Variables

        The following variables are supported and are primarily intended to allow the dynamic generation of Qt forms:

        :param choices: possible values
        :type dict:
        :param label: The label text that gets displayed in the UI
        :type str:
        :param description: A description that gets displayed in the UI when hovering over a field.
        :type str:
        :param validators: A list of functions to validate a entered record
        :type list:
        :param min: A minimum allowed value
        :type int:
        :param max: A maximum allowed value
        :type int:
        :param add_to_ui: Flag that determines whether a column should be displayed in a dynamically generated UI.
        :type bool:
        :param auto_now: Only relevant for date entries within PyQt. If set to true, it will show the current date.
        :type bool:
        :param qtmodel_column: Defines the column number within a Qt Model.
        :type int:
        """
        kwargs.setdefault('info', {})

        kwargs['info'].setdefault('choices', kwargs.pop('choices', None))
        kwargs['info'].setdefault('label', kwargs.pop('label', ''))
        kwargs['info'].setdefault('description', kwargs.pop('description', ''))
        kwargs['info'].setdefault('validators', kwargs.pop('validators', []))
        kwargs['info'].setdefault('min', kwargs.pop('min', None))
        kwargs['info'].setdefault('max', kwargs.pop('max', None))
        kwargs['info'].setdefault('add_to_ui', kwargs.pop('add_to_ui', True))
        kwargs['info'].setdefault('auto_now', kwargs.pop('auto_now', False))
        kwargs['info'].setdefault('qtmodel_column', kwargs.pop('qtmodel_column', None))

        # Make strings and booleans not nullable by default
        if args:
            if (
                any(bool_or_str(arg) for arg in args[0:2]) or
                ('type' in kwargs and bool_or_str(kwargs['type']))
            ):
                kwargs.setdefault('nullable', False)

        sqlalchemy.Column.__init__(self, *args, **kwargs)

    @property
    def choices(self):
        return self.info['choices'] if 'choices' in self.info else []

    @property
    def description(self):
        return self.info['description'] if 'description' in self.info else ''


    @property
    def validators(self):
        return self.info['validators'] if 'validators' in self.info else []


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

    id = Column(UUIDType(), primary_key=True)


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



