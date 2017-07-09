# define authorship information
__authors__     = ['Lars Fasel']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2017'
__license__     = 'MIT'

# maintanence information
__maintainer__  = 'Lars Fasel'
__email__       = 'systemcheck@team-fasel.com'

from pprint import pprint, pformat
import re

import sqlalchemy_utils
from sqlalchemy import inspect

from typing import Any, List, Union
from .meta import Base, SurrogatePK, SurrogateUuidPK, UniqueConstraint, \
    Column, String, CHAR, generic_repr, validates, backref, \
    UniqueMixin, Session, DateTime, relationship, declared_attr, attribute_mapped_collection, \
    one_to_many, many_to_one, Boolean, Integer, ForeignKey, ChoiceType, UUIDType

@generic_repr
class AbapClient(Base):
    """ Contains ABAP specific information"""

    __tablename__ = 'abap_clients'

    id=Column(Integer, primary_key=True)

    client=Column(String(3),
                  nullable=False,
                  qt_label='Client',
                  qt_description='The 3 digit number that describes the client',
                  )

    description= Column(String(250),
                        nullable=True,
                        qt_label='Description',
                        qt_description="Client Description",
                        )
    use_sso = Column(Boolean,
                     default=True,
                     qt_label='Use SSO',
                     qt_description='Use Single Sign On',
                     )

    credential_id = Column(CHAR(32), ForeignKey('credentials.id'), qt_show=False)
    credential=relationship("Credential")

    abapsystem_id = Column(Integer, ForeignKey('abap_systems.id'), qt_show=False)
    abapsystem = relationship('AbapSystem', back_populates='clients')


@generic_repr
class AbapSystem(SurrogateUuidPK, Base):
    """ ABAP System Specification
    """

    __tablename__ = 'abap_systems'

    SNC_QOP_CHOICES=[(1, '1: Secure Auth. Only'),
                     (2, '2: Data Integrity'),
                     (3, '3: Data Confidentiality.'),
                     (9, '9: Max. Available')]

    id = Column(Integer, primary_key=True, qt_show=False)

    sid = Column(String(32),
                 unique=True,
                 nullable=False,
                 qt_label='SID',
                 qt_description='Unique System Identifier')

    tier = Column(String(32),
                  nullable=True,
                  default='Unspecified',
                  qt_label='Tier',
                  qt_description='Tier the system resides in (for example DEV, PRD, or others)',
                  )

    rail = Column(String(32),
                  nullable=True,
                  default='Unspecified',
                  qt_label='Rail',
                  qt_description='The rail the system resides in (N, N+1)',
                  )

    description= Column(String(250),
                        nullable=True,
                        qt_label='Description',
                        qt_description='Description of the system',
                        )

    enabled = Column(Boolean,
                     default=True,
                     qt_label='Enabled',
                     qt_description='System enabled',
                     )

    snc_partnername = Column(String(250),
                             nullable=True,
                             qt_label="SNC Partner Name",
                             qt_description="SNC Partner Name",
                             )

    snc_qop=Column(ChoiceType(SNC_QOP_CHOICES),
                   nullable=True,
                   default=9,
                   qt_label='SNC QoP',
                   qt_description='SNC Quality of Protection',
                   choices=SNC_QOP_CHOICES,
                   )

    use_snc=Column(Boolean,
                   default=True,
                   qt_label='Use SNC',
                   qt_description='Use a secured connection',
                   )

    default_client=Column(String(3),
                         unique=False,
                         nullable=False,
                         default='000',
                         qt_label='Default Client',
                         qt_description='The client that should be used for client independent checks',
                         )

    ms_hostname=Column(String(250),
                       nullable=True,
                       qt_label='MS Hostname',
                       qt_description='Specify the Message Server for load balanced connections',
                       )

    ms_sysnr=Column(String(2),
                    default='00',
                    nullable=True,
                    qt_label='MS SysNr.',
                    qt_description='System Number of the message server',
                    )

    ms_logongroup=Column(String(32),
                         nullable=True,
                         qt_label='Logon Group',
                         default='PUBLIC',
                         qt_description='Logon Group to use for load balanced connections',
                         )

    as_hostname=Column(String(250),
                       nullable=True,
                       qt_label='AS Hostname',
                       qt_description='Application Server Hostname, to be used in case load balancing should not be used.',
                       )

    as_sysnr=Column(String(2),
                    nullable=True,
                    default='00',
                    qt_label='AS SysNr.',
                    qt_description='System Number of the application server')

    system_tree_id = Column(Integer, ForeignKey('system_tree.id'))
    tree = relationship('SystemTreeNode', back_populates='abap_system')
    clients = relationship('AbapClient', back_populates='abapsystem', cascade="save-update, merge, delete")


@generic_repr
class Credential(Base):
    __tablename__ = 'credentials'

    id = Column(Integer, primary_key=True)
    application = Column(String(250), nullable=False,  unique=False)
    description = Column(String(250), nullable=False,  unique=True)
    username = Column(String(40), unique=False, nullable=False)
    type = Column(String(40), unique=False, nullable=False, default='Password')
    uq_application_description_username = UniqueConstraint(application, description, username)


@generic_repr
class SystemTreeNode(SurrogateUuidPK, Base):
    """ A generic node that is the foundation of the tree stored in a database table"""
    __tablename__ = 'system_tree'

    id = Column(Integer, primary_key=True, qt_label='Primary Key', qt_show=False)
    parent_id = Column(Integer, ForeignKey('system_tree.id'), qt_label='Parent Key', qt_show=False)
    type = Column(String(50), qt_show=True, qt_label = 'Type')
    name = Column(String(50), qt_show=True, qt_label='Name')
    abap_system = relationship('AbapSystem', uselist=False, back_populates='tree')
    children=relationship('SystemTreeNode',
                          cascade="all, delete-orphan",
                          backref=backref("parent", remote_side=id),
                          )

    def __init__(self, type, name, parent=None):
        self.type = type
        self.parent = parent
        self.name = name

        #To be able to map a Qt column nuber to a table column numer, build a mapping

    def _child(self, childnr:int)->Any:
        """  Return the child object at a specific position"""
        if self._child_count() >0:
            if childnr >= 0 and childnr<self._child_count():
                return self.children[childnr]

        return False

    def _child_count(self)->int:
        """ Return the number of children """
        return len(self.children)

    def _column_count(self)->int:
        """ Return the number of columns """
        return len(self.__table__.columns)

    def _visible_columns(self)->List[Any]:
        """ Return a list of columns that have the info medatadata variable qt_show set to True"""
        return [colData
                for colData in self.__table__.columns
                if colData.info.get('qt_show')==True]

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

    def _insert_child(self, position:int, node)->bool:
        self.children.insert(position, node)

        session=inspect(self).session
        session.commit()
        return True

    def _remove_child(self, position:int)->bool:
        """ Remove a child item at a particular position

        :param position: The position within the list of children

        """
        if 0 <= position < self._child_count():
            child=self._child(position)

            session=inspect(child).session

            # Since we are using SQLAlchemy, we can't simply delete objects. If an object is part of a change that was not
            # committet yet, we need to use 'Session.expunge()' instead of 'Session.delete()'.
            if child in session.new:
                session.expunge(child)
            else:
                session.delete(child)
            session.commit()

        return True



    def _colnr_is_valid(self, colnr:int)->bool:


        if colnr>=0 and colnr < len(self.__table__.columns):
            return True
        return False

    def _visible_colnr_is_valid(self, colnr:int)->bool:
        """ Validate that the column number is ok fo a visible column"""

        visible_columns=self._visible_columns()

        if colnr>=0 and colnr < len(visible_columns):
            return True
        return False

    def _row(self):
        if self.parent is not None:
            return self.parent.children.index(self)

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
            self._commit()
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

    def _dump(self, _indent=0)->str:
        """ Recursively return the structure of the node and all its children as text """
        return "   " * _indent + repr(self) + \
            "\n" + \
            "".join([
                c._dump(_indent + 1)
                for c in self.children
            ])

    def _commit(self):
        session = inspect(self).session
        session.commit()

    def _flush(self):
        session = inspect(self).session
        session.flush()
