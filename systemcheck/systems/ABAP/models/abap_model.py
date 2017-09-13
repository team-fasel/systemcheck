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
import traceback
import re

import sqlalchemy_utils

import enum
from sqlalchemy import inspect, Integer, ForeignKey, String, Boolean
from typing import Any, List, Union
from systemcheck.models.meta import Base, SurrogatePK, SurrogateUuidPK, UniqueConstraint, \
    StandardAbapAuthSelectionOptionMixin, Column, String, CHAR, generic_repr, validates, backref, QtModelMixin, \
    PasswordKeyringMixin, UniqueMixin, Session, DateTime, qtRelationship, declared_attr, attribute_mapped_collection, \
    one_to_many, many_to_one, Boolean, Integer, ForeignKey, ChoiceType, hybrid_property, RichString
from systemcheck.models.credentials import Credential
from systemcheck.systems.ABAP.utils import get_snc_name
from systemcheck.config import CONFIG
import keyring
from systemcheck.models.meta.orm_choices import choices
from systemcheck.systems.generic.models import GenericSystemTreeNode
from systemcheck.checks.models import Check
import uuid
import logging

class StandardAuthSelectionOptionMixin:


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


@generic_repr
class SystemABAPFolder(GenericSystemTreeNode):

    __mapper_args__ = {
        'polymorphic_identity':'systems_ABAP_FOLDER',
    }

@generic_repr
class SystemABAP(GenericSystemTreeNode):
    """ ABAP System Specification
    """

    __tablename__ = 'systems_ABAP'
    __table_args__ = {'extend_existing': True}


    SNC_QOP_CHOICES=[
                        ('1', '1: Secure Auth. Only'),
                        ('2', '2: Data Integrity'),
                        ('3', '3: Data Confidentiality.'),
                        ('9', '9: Max. Available')
                    ]

    id = Column(Integer, ForeignKey('systems.id'), primary_key=True, qt_show=False)

    sid = Column(String(32),
                 unique=False,
                 nullable=False,
                 default='NEW',
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


    __mapper_args__ = {
        'polymorphic_identity':'systems_ABAP',
    }

    __qtmap__ = [GenericSystemTreeNode.name, GenericSystemTreeNode.description, sid, tier, rail,
                 enabled, snc_partnername, snc_qop, use_snc, default_client,
                 ms_hostname, ms_sysnr, ms_logongroup, as_hostname, as_sysnr]

    def _icon(self):
        return ":SAP"

    def getDefaultClient(self):

        for client in self.children:
            if client.client == self.default_client:
                return client
        raise ValueError('No definition of default client for the system')

@generic_repr
class SystemABAPClient(GenericSystemTreeNode, PasswordKeyringMixin):
    """ Contains ABAP specific information"""
    __tablename__ = 'systems_ABAP_client'
    __table_args__ = {'extend_existing': True}
    __mapper_args__ = {
        'polymorphic_identity':'systems_ABAP_client',
    }


    id = Column(Integer, ForeignKey('systems.id'), primary_key=True, qt_show=False)

    client = Column(String(3),
                  nullable=False,
                  qt_label='Client',
                  qt_description='The 3 digit number that describes the client',
                  )

    use_sso = Column(Boolean,
                     default=True,
                     qt_label='Use SSO',
                     qt_description='Use Single Sign On',
                     )
    username = Column(String(40), default='<initial>', nullable=True, qt_label='Username', qt_description='Username to logon to the ABAP Client')


    __qtmap__ = [client, GenericSystemTreeNode.description, use_sso, username]

    def __init__(self, **kwargs):
        uuid_string = str(uuid.uuid4())
        self.keyring_uuid = uuid_string
        self.client = kwargs.get('client')
        self.description = kwargs.get('description')
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.use_sso = kwargs.get('use_sso')

    def _icon(self):
        return ":Client"

    def getDefaultClient(self):

        parent = self.parent_node
        return parent.getDefaultClient()

    def logon_info(self):

        logon_info = {}
        self.logger = logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))
        abap_system = self.parent_node
        if abap_system:
            sysid = abap_system.sid
            logon_info['sysid'] = sysid  #technically only required for load balancing, but we specify it
                                         # anyway since it's handy down the road.
            logon_info['client'] = self.client
            if abap_system.ms_hostname and abap_system.ms_sysnr and abap_system.ms_logongroup:
                mshost=abap_system.ms_hostname
                msserv='36' + abap_system.ms_sysnr
                group = abap_system.ms_logongroup
                self.logger.debug('Logon using Load Balancing. mshost: %s, msserv: %s, sysid: %s, group: %s', mshost, msserv, sysid, group)
                logon_info['mshost'] = mshost
                logon_info['msserv'] = msserv
                logon_info['group'] = group
            elif abap_system.as_hostname and abap_system.as_sysnr:
                logon_info['ashost'] = abap_system.as_hostname
                logon_info['sysnr'] = abap_system.as_sysnr
                self.logger.debug('Logon using direct as connection. ashost: %s, sysnr: %s', logon_info['ashost'],
                                  logon_info['sysnr'])
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


@generic_repr
class ActionABAPFolder(Check):
    __mapper_args__ = {
        'polymorphic_identity': 'ActionABAPFolder',
    }

class ActionABAPIsClientSpecificMixin:
    """ Define a readonly property for client specific checks """

    client_specific = Column(Boolean,
                             default=True,
                             qt_label='Client Specific',
                             qt_description="This check is client specific. It's not possible to manually "
                                            "change this value",
                             qt_enabled=False,
                             qt_show=True)


class ActionABAPIsNotClientSpecificMixin:
    """ Define a readonly property for client independent checks  """

    client_specific = Column(Boolean,
                             default=False,
                             qt_label='Client Specific',
                             qt_description="This check is not client specific. It's not possible to manually "
                                            "change this value",
                             qt_enabled=False,
                             qt_show=True)


class ActionABAPClientSpecificMixin:
    """ Creates a checkbox for all ABAP checks to define whether they are client specific or not """

    client_specific = Column(Boolean, name='client_specific',
                             default=True,
                             qt_label='Client Specific',
                             qt_description='Check the box if the check is client specific',
                             qt_show=True)

