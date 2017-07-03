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

from .meta import Base, SurrogatePK, SurrogateUuidPK, UniqueConstraint, \
    Column, String, CHAR, generic_repr, validates, \
    UniqueMixin, Session, DateTime, relationship, declared_attr,  \
    one_to_many, many_to_one, Boolean, Integer, ForeignKey, ChoiceType, UUIDType


@generic_repr
class AbapClient(SurrogateUuidPK, Base):
    """ Contains ABAP specific information"""

    __tablename__ = 'abap_clients'

    client=Column(String(3),
                  nullable=False,
                  label='Client',
                  description='The 3 digit number that describes the client',
                  qtmodel_column=1)

    description= Column(String(250),
                        nullable=True,
                        label='Description',
                        description="Client Description",
                        qtmodel_column=2)
    use_sso = Column(Boolean,
                     default=True,
                     label='Use SSO',
                     description='Use Single Sign On',
                     qtmodel_column=3)

    credential_id = Column(CHAR(32), ForeignKey('identities.id'), add_to_ui=False)
    credential=relationship("Credential")

    abapsystem_id = Column(Integer, ForeignKey('abap_systems.id'), add_to_ui=False)
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


    sid = Column(String(32),
                 unique=True,
                 nullable=False,
                 label='SID',
                 description='Unique System Identifier',
                 qtmodel_column=1)

    tier = Column(String(32),
                  nullable=True,
                  default='Unspecified',
                  label='Tier',
                  description='Tier the system resides in (for example DEV, PRD, or others)',
                  qtmodel_column=2)

    rail = Column(String(32),
                  nullable=True,
                  default='Unspecified',
                  label='Rail',
                  description='The rail the system resides in (N, N+1)',
                  qtmodel_column=3)

    description= Column(String(250),
                        nullable=True,
                        label='Description',
                        description='Description of the system',
                        qtmodel_column=4)

    enabled = Column(Boolean,
                     default=True,
                     label='Enabled',
                     description='System enabled',
                     qtmodel_column=5)

    sncPartnername = Column(String(250),
                            nullable=True,
                            label="SNC Partner Name",
                            description="SNC Partner Name",
                            qtmodel_column=6)

    sncQop=Column(ChoiceType(SNC_QOP_CHOICES),
                  nullable=True,
                  default=9,
                  label='SNC QoP',
                  description='SNC Quality of Protection',
                  qtmodel_column=7,
                  choices=SNC_QOP_CHOICES)

    use_snc=Column(Boolean,
                   default=True,
                   label='Use SNC',
                   description='Use a secured connection',
                   qtmodel_column=8)

    defaultClient=Column(String(3),
                         unique=False,
                         nullable=False,
                         default='000',
                         label='Default Client',
                         description='The client that should be used for client independent checks',
                         qtmodel_column=9)

    ms_hostname=Column(String(250),
                       nullable=True,
                       label='MS Hostname',
                       description='Specify the Message Server for load balanced connections',
                       qtmodel_column=10)

    ms_sysnr=Column(String(2),
                    default='00',
                    nullable=True,
                    label='MS SysNr.',
                    description='System Number of the message server',
                    qtmodel_column=11)

    ms_logongroup=Column(String(32),
                         nullable=True,
                         label='Logon Group',
                         default='PUBLIC',
                         description='Logon Group to use for load balanced connections',
                         qtmodel_column=12)

    as_hostname=Column(String(250),
                       nullable=True,
                       label='AS Hostname',
                       description='Application Server Hostname, to be used in case load balancing should not be used.',
                       qtmodel_column=13)

    as_sysnr=Column(String(2),
                    nullable=True,
                    default='00',
                    label='AS SysNr.',
                    description='System Number of the application server',
                    qtmodel_column=14)

    system_tree_uuid = Column(UUIDType, ForeignKey='system_tree.id')
    tree = relationship('SystemTree', back_populates='abap_systems')
    clients = relationship('AbapClient', back_populates='abapsystem', cascade="save-update, merge, delete")


@generic_repr
class Credential(SurrogatePK, Base):
    __tablename__ = 'credentials'

    application = Column(String(250), nullable=False,  unique=False)
    description = Column(String(250), nullable=False,  unique=True)
    username = Column(String(40), unique=False, nullable=False)
    type = Column(String(40), unique=False, nullable=False, default='Password')
    uq_application_description_username = UniqueConstraint(application, description, username)

class SystemTree(SurrogateUuidPK, Base):
    __tablename__ = 'system_tree'

    parent_uuid = Column(UUIDType(), ForeignKey('credentials.id'))
    type = Column(String(50))
    abap_system = relationship('AbapSystem', uselist=False, back_populates='system_tree')
    children=relationship('SystemTree')