# define authorship information
__authors__     = ['Lars Fasel']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2017'
__license__     = 'MIT'

# maintanence information
__maintainer__  = 'Lars Fasel'
__email__       = 'systemcheck@team-fasel.com'



from typing import Any, List, Union
from systemcheck.models.meta import Base, SurrogatePK, SurrogateUuidPK, UniqueConstraint, \
    StandardAbapAuthSelectionOptionMixin, Column, String, CHAR, generic_repr, validates, backref, QtModelMixin, \
    PasswordKeyringMixin, UniqueMixin, Session, DateTime, qtRelationship, declared_attr, attribute_mapped_collection, \
    one_to_many, many_to_one, Boolean, Integer, ForeignKey, hybrid_property, RichString
from systemcheck.systems.ABAP.utils import get_snc_name
from systemcheck.config import CONFIG
import keyring
from systemcheck.models.meta.orm_choices import choices
from systemcheck.models.meta.systemcheck_choices import YesNoChoice
from systemcheck.systems import generic
#from systemcheck.systems.generic.models import GenericSystem
from systemcheck import checks
from systemcheck.checks.models import Check
import uuid
import logging

@choices
class SystemAbapIncludeChoice:
    class Meta:
        INCLUDE = ['I', 'Include']
        EXCLUDE = ['E', 'Exclude']

@choices
class SystemAbapOptionChoice:
    class Meta:
        NE = ['NE', 'not equal']
        EQ = ['EQ', 'equal']
        GT = ['GT', 'greater']
        GE = ['GE', 'greater or equal']
        LT = ['LT', 'lower']
        LE = ['LE', 'lower or equal']

@choices
class SystemAbapSncChoice:
    class Meta:
        AUTHENTICATION = ['1', '1: Secure Authentication Only']
        INTEGRITY = ['2', '2: Data Integrity ']
        CONFIDENTIALITY = ['3', '3: Data Confidentiality']
        MAX = ['9', '9: Max. Available']

@choices
class AbapAppServerOsChoices:
    class Meta:
        WINDOWS = ['Windows NT', 'Windows']
        ANYOS = ['ANYOS', 'Any OS']
        OS400 = ['OS/400', 'OS/400']
        UNIX = ['UNIX', 'Unix']
        SYNOS = ['SUNOS', 'Solaris, SunOS']

@choices
class AbapLanguageChoices:
    class Meta:
        EN = ['E', 'English']
        DE = ['D', 'German']

class StandardAuthSelectionOptionMixin(QtModelMixin):

    SIGN = Column(String, name='SIGN',
                  nullable = False,
                  default = SystemAbapIncludeChoice.INCLUDE,
                  qt_label = 'Incl./Excl.',
                  qt_description = 'Should the specified items be included or excluded? Default is to include them',
                  choices = SystemAbapIncludeChoice.CHOICES,
                  )

    OPTION = Column(Integer, name='OPTION',
                    nullable = False,
                    default = SystemAbapOptionChoice.EQ,
                    qt_label = 'Sel. Option',
                    qt_description = 'Selection option',
                    choices = SystemAbapOptionChoice.CHOICES,
                    )

    LOW = Column(String(12), name='LOW',
                 nullable=False,
                 qt_label='Lower Range Value',
                 qt_description='Lower Range Value. Must be specified.',
                )

    HIGH = Column(String(12), name='HIGH',
                 nullable=True,
                 qt_label='Higher Range Value',
                 qt_description='Higher Range Value. Optional.',
                )

    __qtmap__ = [SIGN, OPTION, LOW, HIGH]

@generic_repr
class SystemAbapFolder(generic.models.GenericSystem):

    __mapper_args__ = {
        'polymorphic_identity':'SystemAbapFolder',
    }


@generic_repr
class SystemAbap(generic.models.GenericSystem):
    """ ABAP System Specification
    """

    __tablename__ = 'systems_ABAP'
    __table_args__ = {'extend_existing': True}

    __icon__ = ':Server'


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
                     default=YesNoChoice.YES,
                     choices=YesNoChoice.CHOICES,
                     qt_label='Enabled',
                     qt_description='System enabled',
                     )

    snc_partnername = Column(String(250),
                             nullable=True,
                             qt_label="SNC Partner Name",
                             qt_description="SNC Partner Name",
                             )

    snc_qop=Column(String,
                   nullable=True,
                   default=SystemAbapSncChoice.MAX,
                   qt_label='SNC QoP',
                   qt_description='SNC Quality of Protection',
                   choices=SystemAbapSncChoice.CHOICES,
                   )

    use_snc=Column(Boolean,
                   default=YesNoChoice.YES,
                   choices=YesNoChoice.CHOICES,
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

    __qtmap__ = [generic.models.GenericSystem.name, generic.models.GenericSystem.description,
                 generic.models.GenericSystem.category, sid, tier, rail,
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
class SystemAbapClient(generic.models.GenericSystemTreeNode, PasswordKeyringMixin):
    """ Contains ABAP specific information"""
    __tablename__ = 'SystemAbapClient'
    __table_args__ = {'extend_existing': True}
    __mapper_args__ = {
        'polymorphic_identity':'SystemAbapClient',
    }

    __icon__ = ':Brief'

    id = Column(Integer, ForeignKey('systems.id'), primary_key=True, qt_show=False)

    client = Column(String(3),
                  nullable=False,
                  qt_label='Client',
                  qt_description='The 3 digit number that describes the client',
                  )

    use_sso = Column(Boolean,
                     default=YesNoChoice.YES,
                     choices=YesNoChoice.CHOICES,
                     qt_label='Use SSO',
                     qt_description='Use Single Sign On',
                     )
    username = Column(String(40), default='<initial>', nullable=True, qt_label='Username', qt_description='Username to logon to the ABAP Client')


    __qtmap__ = [client, generic.models.GenericSystem.description, use_sso, username]

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
        snc_qop = None
        snc_partnername = None
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
class ActionAbapFolder(Check):
    __mapper_args__ = {
        'polymorphic_identity': 'ActionAbapFolder',
    }

class ActionAbapIsClientSpecificMixin:
    """ Define a readonly property for client specific checks """

    client_specific = Column(Boolean,
                             default=YesNoChoice.YES,
                             choices=YesNoChoice.CHOICES,
                             qt_label='Client Specific',
                             qt_description="This check is client specific. It's not possible to manually "
                                            "change this value",
                             qt_enabled=False)

class ActionAbapIsNotClientSpecificMixin:
    """ Define a readonly property for client independent checks  """

    client_specific = Column(Boolean,
                             default=YesNoChoice.NO,
                             choices=YesNoChoice.CHOICES,
                             qt_description="This check is not client specific. It's not possible to manually "
                                            "change this value",
                             qt_enabled=False)

class ActionAbapClientSpecificMixin:
    """ Creates a checkbox for all ABAP checks to define whether they are client specific or not """

    client_specific = Column(Boolean, name='client_specific',
                             default=YesNoChoice.YES,
                             choices=YesNoChoice.CHOICES,
                             qt_description='Check the box if the check is client specific')

class AbapSpoolParams_BAPIXMPRNT_Mixin:

    DESTIN = Column(String(4),
                    qt_label='Spool Output Device',
                    nullable=False)

    PRINTIMM = Column(Boolean,
                      qt_label='Immediate Spool Print',
                      choices=YesNoChoice.CHOICES,
                      default=YesNoChoice.NO, nullable=False)

    RELEASE = Column(Boolean,
                     qt_label='Immediate Spool Deletion',
                     choices=YesNoChoice.CHOICES,
                     default=YesNoChoice.NO,
                     nullable=False)

    COPIES = Column(Integer,
                    qt_label='Number of Spool Copies',
                    nullable=True)

    PRIARCMODE = Column(Boolean,
                        qt_label='Print: Archiving mode',
                        choices=YesNoChoice.CHOICES,
                        default=YesNoChoice.NO,
                        nullable=True)

    SHOWPASSWD = Column(String(12),
                        qt_label='Print: Authorization',
                        nullable=True)

    SAPBANNER = Column(Boolean,
                       qt_label='Print: SAP Cover Page',
                       choices=YesNoChoice.CHOICES,
                       default=YesNoChoice.NO,
                       nullable=True)
    BANNERPAGE = Column(Boolean,
                        qt_label='Spool Cover Sheet',
                       choices=YesNoChoice.CHOICES,
                       default=YesNoChoice.NO,
                       nullable=True)

    EXPIRATION =  Column(Integer,
                         qt_label='Spool Retention Period',
                         nullable=True)

    PRINTRECEIP =  Column(String(12),
                          qt_label='Spool Receipient Name',
                          nullable=True)

    NUMLINES = Column(Integer,
                      qt_label='Page Lenth of List',
                      nullable=True)

    NUMCOLUMNS = Column(Integer,
                        qt_label='Line Width of List',
                        nullable=True)

class AbapSpoolParams_BAPIPRIPAR_Mixin:
    PDEST = Column(String(4),
                    qt_label='Spool Output Device',
                    nullable=True,
                   name='PDEST',
                   default='LP01')

    PRCOP = Column(Integer,
                    qt_label='Number of Spool Copies',
                   name='PRCOP',
                   nullable=True)

    PLIST = Column(String(12),
                   qt_label='Spool Request',
                   name='PLIST',
                   nullable=True)

    PRTXT = Column(String(68),
                   qt_label='Spool Description',
                   name='PRTXT',
                   nullable=True)

    PRIMM = Column(Boolean,
                   qt_label='Immediate Spool Print',
                   choices=YesNoChoice.CHOICES,
                   default=YesNoChoice.NO,
                   name='PRIMM',
                   nullable=False)

    PRREL = Column(Boolean,
                   qt_label='Immediate Spool Deletion',
                   choices=YesNoChoice.CHOICES,
                   name='PRREL',
                   nullable=True)

    PRNEW  = Column(Boolean,
                     qt_label='Immediate Spool Deletion',
                     choices=YesNoChoice.CHOICES,
                    name='PRNEW',
                    nullable=True)

    PEXPI = Column(Integer,
                   qt_label='Spool Retention Period',
                   nullable=True,
                   name='PEXPI')

    LINCT = Column(Integer,
                   qt_label='Page Lenth of List',
                   name='LINCT',
                   nullable=True)

    LINSZ = Column(Integer,
                   qt_label='Line Width of List',
                   name='LINSZ',
                   nullable=True)

    PAART = Column(String(68),
                   qt_label='Spool Format',
                   nullable=True,
                   name='PAART'
                   )

    PRBIG = Column(Boolean,
                   qt_label='Spool Cover Sheet',
                   choices=YesNoChoice.CHOICES,
                   nullable=True,
                   name='PRBIG')

    PRSAP = Column(Boolean,
                   qt_label='Print: SAP Cover Page',
                   choices=YesNoChoice.CHOICES,
                   nullable=True,
                   name='PRSAP')

    PRREC =  Column(String(12),
                    qt_label='Spool Receipient Name',
                    nullable=True,
                    name='PRREC')

    PRABT =  Column(String(12),
                          qt_label='Spool Department Name',
                          nullable=True, name='PRABT')

    PRBER = Column(String(12),
                        qt_label='Print: Authorization',
                        nullable=True, name='PRBER')

    PRDSN = Column(String(6),
                   qt_label='Spool File',
                   nullable=True,
                   name='PRDSN')

    PTYPE = Column(String(12),
                        qt_label='Print: Type of Spool Request',
                        nullable=True,
                   name='PTYPE')

    ARMOD = Column(Boolean,
                        qt_label='Print: Archiving mode',
                        choices=YesNoChoice.CHOICES,
                        nullable=True,
                   name='ARMOD')

    FOOTL = Column(Boolean,
                        qt_label='Print: Output Footer',
                        choices=YesNoChoice.CHOICES,
                        nullable=True,
                   name='FOOTL')

    PRIOT = Column(Integer,
                   qt_label='Print: Spool Request Priority',
                   nullable=True,
                   name='PRIOT')

    PRUNX = Column(Boolean,
                        qt_label='Print: Host Spool Cover Page',
                        choices=YesNoChoice.CHOICES,
                        nullable=True,
                   name='PRUNX')

class Abap_BPJOBSTEP_Mixin:

    PROGRAM = Column(String(128),
                     nullable=True,
                     qt_label='Program Name')

    TYP = Column(String(1),
                 nullable=True,
                 qt_description='Identification of Step as ABAP, ext. command or program',
                 qt_label='Step Type')

    PARAMETER = Column(String(255),
                       nullable=True,
                       qt_description='Parameters of external program',
                       qt_label='Ext. Prog. Params')

    OPSYSTEM = Column(String(10),
                      nullable=True,
                      choices = AbapAppServerOsChoices,
                      qt_label='App Server OS')

    AUTHCKNAM = Column(String(12),
                       qt_label='Step User',
                       qt_description='Background User Name for Authorization Check',
                       nullable=True)

    LISTIDENT = Column(String(10),
                       qt_label='Job Output Id',
                       qt_description='ID of batch job output list in the spool',
                       nullable=True)

    XPGPID = Column(String(10),
                    qt_label='ID of ext. Program',
                    qt_description='ID of External Program',
                    nullable=True)

    XPGTGTSYS = Column(String(32),
                    qt_label='Target System',
                    qt_description='Target System to Run Background Job',
                    nullable=True)

    XPGRFCDEST = Column(String(32),
                    qt_label='Logical Destination',
                    qt_description='Logical Destination (Specified in function call)',
                    nullable=True)

    LANGUAGE = Column(String(10),
                      choices=AbapLanguageChoices.CHOICES,
                      default=AbapLanguageChoices.EN,
                      qt_label='Language',
                      qt_description='Language',
                      nullable=True)

    STATUS = Column(String(1),
                      qt_label='Step Status',
                      qt_description='Language',
                      nullable=True)

    CONNCNTL  = Column(String(1),
                      qt_label='Control Flag for ext. Prog',
                      qt_description='Language',
                      nullable=True)

#    STDINCNTL
#    STDOUTCNTL
#    STDERRCNTL
#    TRACECNTL
#    TERMCNTL




