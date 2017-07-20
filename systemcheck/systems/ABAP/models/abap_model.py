# define authorship information
from sqlalchemy.orm import relationship, backref
from sqlalchemy_utils import generic_repr, ChoiceType

from models.meta import Base, QtModelMixin, Column

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

import enum
from sqlalchemy import inspect, Integer, ForeignKey, String, Boolean
from typing import Any, List, Union
from systemcheck.models.meta import Base, SurrogatePK, SurrogateUuidPK, UniqueConstraint, \
    Column, String, CHAR, generic_repr, validates, backref, QtModelMixin, PasswordKeyringMixin, \
    UniqueMixin, Session, DateTime, relationship, declared_attr, attribute_mapped_collection, \
    one_to_many, many_to_one, Boolean, Integer, ForeignKey, ChoiceType, hybrid_property, UUIDType
from systemcheck.models.credentials import Credential
from systemcheck.systems.ABAP.utils import get_snc_name
from systemcheck.config import CONFIG
import keyring
import uuid
import logging

@generic_repr
class AbapTreeNode(Base, QtModelMixin):
    """ A generic node that is the foundation of the tree stored in a database table"""
    __tablename__ = 'abap_tree'
    __table_args__ = {'extend_existing': True}


    id = Column(Integer, primary_key=True, qt_label='Primary Key', qt_show=False)
    parent_id = Column(Integer, ForeignKey('abap_tree.id'), qt_label='Parent Key', qt_show=False)
    type = Column(String(50), qt_show=False, qt_label='Type')
    name = Column(String(50), qt_show=True, qt_label='Name')
    abap_system = relationship('AbapSystem', uselist=False, back_populates='tree', cascade='all, delete-orphan')
    abap_client = relationship('AbapClient', uselist=False, back_populates='tree', cascade='all, delete-orphan')
    children=relationship('AbapTreeNode',
                          cascade="all, delete-orphan",
                          backref=backref("parent_node", remote_side=id),
                          )


    def _dump(self, _indent=0)->str:
        """ Recursively return the structure of the node and all its children as text """
        return "   " * _indent + repr(self) + \
            "\n" + \
            "".join([
                c._dump(_indent + 1)
                for c in self.children
            ])

    def _child(self, childnr:int)->Any:
        """  Return the child object at a specific position"""
        if self._child_count() >0:
            if childnr >= 0 and childnr<self._child_count():
                return self.children[childnr]

        return False

    def _child_count(self)->int:
        """ Return the number of children """
        return len(self.children)

    def _insert_child(self, position:int, node)->bool:
        self.children.insert(position, node)

        session=inspect(self).session
        session.commit()
        return True

    def _row(self):
        if self.parent_node is not None:
            return self.parent_node.children.index(self)

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

    def _system_node(self):
        #TODO: That needs to be done dynamically at some point
        if self.type == 'ABAP':
            return self.abap_system
        elif self.type == 'ABAPCLIENT':
            return self.abap_client
        elif self.type =='FOLDER':
            return None
        else:
            return None


@generic_repr
class AbapSystem(Base, QtModelMixin):
    """ ABAP System Specification
    """

    __tablename__ = 'abap_systems'
    __table_args__ = {'extend_existing': True}


    SNC_QOP_CHOICES=[
                        ('1', '1: Secure Auth. Only'),
                        ('2', '2: Data Integrity'),
                        ('3', '3: Data Confidentiality.'),
                        ('9', '9: Max. Available')
                    ]

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
                   default='9',
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

    system_tree_id = Column(Integer, ForeignKey('abap_tree.id'))
    tree = relationship('AbapTreeNode', back_populates='abap_system', cascade='all, delete-orphan', single_parent=True)


@generic_repr
class AbapClient(Base, QtModelMixin, PasswordKeyringMixin):
    """ Contains ABAP specific information"""
    __tablename__ = 'abap_clients'
    __table_args__ = {'extend_existing': True}


    id = Column(Integer, primary_key=True, qt_show=False)

    client = Column(String(3),
                  nullable=False,
                  qt_label='Client',
                  qt_description='The 3 digit number that describes the client',
                  )
    description = Column(String(250),
                        nullable=True,
                        qt_label='Description',
                        qt_description="Client Description",
                        )
    use_sso = Column(Boolean,
                     default=True,
                     qt_label='Use SSO',
                     qt_description='Use Single Sign On',
                     )
    username = Column(String(40), default='<initial>', nullable=True, qt_label='Username', qt_description='Username to logon to the ABAP Client')
    system_tree_id = Column(Integer, ForeignKey('abap_tree.id'), qt_show=False)
    tree = relationship('AbapTreeNode', back_populates='abap_client', cascade='all, delete-orphan', single_parent=True)

    def __init__(self, **kwargs):
        uuid_string = str(uuid.uuid4())
        self.logger = logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))
        self.keyring_uuid = uuid_string
        self.client = kwargs.get('client')
        self.description = kwargs.get('description')
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.use_sso = kwargs.get('use_sso')

    def abap_system(self):
        parent_node = self.tree.parent_node
        if parent_node.type == 'ABAP':
            return parent_node.abap_system
        else:
            return None

    def login_info(self):

        logon_info = {}

        abap_system = self.abap_system()
        if abap_system:
            sysid = abap_system.sid
            logon_info['sysid'] = sysid  #technically only required for load balancing, but we specify it
                                         # anyway since it's handy down the road.
            if abap_system.ms_hostname and abap_system.ms_sysnr and abap_system.ms_logongroup:
                mshost=abap_system.ms_hostname
                msserv='36' + abap_system.ms_sysnr
                group = abap_system.ms_logongroup

                self.logger.debug('Logon using Load Balancing. mshost: %s, msserv: %s, sysid: %s, group: %s', mshost, msserv, sysid, group)
                logon_info['mshost'] = mshost
                logon_info['msserv'] = msserv
                logon_info['group'] = group
            elif abap_system.as_host and abap_system.as_sysnr:
                ashost = abap_system.as_hostname
                sysnr = abap_system.as_sysnr
                self.logger.debug('Logon using direct as connection. ashost: $s, sysnr: %s', ashost, sysnr)
            else:
                return False

            if abap_system.use_snc:
                snc_qop = abap_system.snc_qop
                snc_partnername = abap_system.snc_partnername
                self.logger.debug('Use SNC: snc_qop: %s, snc_partnername: %s', snc_qop, snc_partnername)

                if CONFIG['systemtype_ABAP'].get('snc.library'):
                    snc_lib = CONFIG['systemtype_ABAP'].get('snc.library')
                    self.logger.debug('SNC Lib specified in config: %s', snc_lib)
                    logon_info['snc_lib'] = snc_lib

            if self.use_sso and abap_system.use_snc:
                snc_myname = get_snc_name()
                self.logger.debug('Use SSO: snc_myname: %s', snc_myname)

                if snc_myname and snc_partnername and snc_qop:
                    self.logger.debug('Use SNC: snc_qop: %s, snc_partnername: %s, snc_myname: %s', snc_qop, snc_partnername, snc_myname)
                    logon_info['snc_qop'] = snc_qop
                    logon_info['snc_partnername'] = snc_partnername
                    logon_info['snc_myname'] = snc_myname

                else:
                    self.logger.error('SSO usage configured, but parameters are incomplete: '
                                      'snc_qop: %s, snc_partnername: %s, snc_myname: %s', snc_qop, snc_partnername, snc_myname)
                    return False
            else:
                user = self.username
                passwd = self.password

                if user and passwd:
                    if CONFIG['application'].getboolean('app.log_sensitive_info'):
                        self.logger.debug('no SSO: user: %s, passwd: %s', user, passwd)
                    else:
                        self.logger.debug('no SSO: user: %s, passwd: XXXXXXXX', user)

                    logon_info['user'] = user
                    logon_info['passwd'] = passwd
                else:
                    self.logger.error('No SSO, but username or Password missing')
                    return False
        return logon_info