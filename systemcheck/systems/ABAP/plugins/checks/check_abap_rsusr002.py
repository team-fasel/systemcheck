import systemcheck.systems.ABAP.plugins as abapplugins
from systemcheck.config import CONFIG

class CheckAbapRsusr002Plugin(abapplugins.CheckAbapSUIMPlugin):
    """RSUSR002: Users by Complex Selection Criteria

    This plugin type retrieves user accounts similar to using SUIM with complex selection criteria. It's calling
    function module SUSR_SUIM_API_RSUSR002 which needs to be available in the system. The API to SUIM is delivered in
    OSS Note 1930238. The following Notes are required:
      - 1930238 - SUIM: API for RSUSR002
      - 2166771 - SUIM: SUSR_SUIM_API_RSUSR002 returns incorrect results
      - 1979313 - SUIM | RSUSR002: Search for executable transactions

    The selection options below depend on the version of the system. The list was retrieved using SE37 in a
    SAP NetWeaver 7.50 system

    Import:
        Standard Selection:
            IT_USER       User list
            IT_GROUP      Group for Authorization
            IT_UGROUP     User group general

        Selection Criteria:
            Documentation:
            Logon Data:
                IT_UALIAS     Selection options for Alias
                IT_UTYPE      Selection options for user type
                IT_SECPOL     Selection options for security policy
                IT_SNC        Selection options for SNC
                Selection by Locks:
                    IV_USER_LOCK  Lock status Y=locked, N=unlocked, Space = irrelevant
                    IV_PWD_LOCK   Lock status Y=locked, N=unlocked, Space = irrelevant
                    IV_LOCK       All Users with administrator- or password locks: TRUE (='X') und FALSE (=' ')
                    IV_UNLOCK     Only users without locks: TRUE (='X') und FALSE (=' ')
                IV_FDATE      Validity date from
                IV_TDATE      Validity date until
                IT_LIC_TYPE   Selection options for license types
                IT_ACCNT      Selection options for Account-Id
                IT_KOSTL      Selection options for cost center
            Default Values:
                IT_STCOD      Selection options for start menu
                IT_LANGU      Selection options for language
                IV_DCPFM      Decimal format
                IV_DATFM      Date format
                IV_TIMEFM     Time format (12-/24-Hour display)
                IT_SPLD       Output Device
                IV_TZONE      Time zone
                IV_CATTK      CATT Check indicator (TRUE (='X') und FALSE (=' '))
                IT_PARID      Selection options for Set-/Get-Paramter-Id
            Roles Profile:
                IV_TCODE      Transaktionscode
                IV_START_TX   Only executable transactions
                IT_UREF       Selection options for reference user
                IT_ACTGRPS    Selection options for role
                IT_PROF1      Selection options for profile
                IV_PROF2      Authorization profile in user master maintenance
                IV_PROF3      Authorization profile in user master maintenance
            Authorizations:
                Selection by Field Name:
                    IV_CONV1      Always convert Values (TRUE (='X') und FALSE (=' '))
                    IV_AUTH_FLD   Authorization field name
                Selection by Authorizations:
                    IV_AUTH_VAL   Authorization value
                    IT_OBJCT      Selection options for authorization objects
                Selection by Values:
                    IT_AUTH       Selection options for authorizations
                    IV_CONV       Data element zur Domäne BOOLE: TRUE (='X') und FALSE (=' ')
                    IT_VALUES     Transfer structure for selection by authorization values

    """

    FM = 'SUSR_SUIM_API_RSUSR002'
    RETURNSTRUCTURE='ET_USERS'

    def __init__(self):
        super().__init__()

        report_columns = CONFIG['systemtype_ABAP']['suim.reportcolumns.rsusr002'].split(',')
        header_descriptions = dict(CHECK = 'Checkbox', BNAME = 'Username', USERALIAS='User Alias',
                                                         CLASS = 'User Group', LOCKICON = 'Lockicon',
                                                         LOCKREASON = 'Lock Reason', GLTGV = 'Valid From',
                                                         GLTGB = 'Valid Until', USTYP = 'User Type',
                                                         REFUSER = 'Reference User', ACCNT = 'ACCNT',
                                                         KOSTL = 'Cost Center', NAME_TEXT = 'Name',
                                                         DEPARTMENT = 'Department', FUNCTION = 'Function',
                                                         BUILDING_C = 'Building', FLOOR_C = 'Floor', ROOMNUM_C = 'Room',
                                                         TEL_NUMBER = 'Phone Number', TEL_EXTENS = 'Phone Extension',
                                                         NAME1 = 'Name 1', NAME2 = 'Name 2', NAME3 = 'Name 3',
                                                         NAME4 = 'Name 4', POST_CODE1 = 'Zip Code', CITY1 = 'City',
                                                         STREET = 'Street', COUNTRY = 'Country', TZONE = 'Time Zone',
                                                         SECURITY_POLICY = 'Security Policy', EMAIL = 'eMail')

        for column in report_columns:
            self.pluginResult.addResultColumn(column, header_descriptions.get(column))

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


from sqlalchemy import inspect, Integer, ForeignKey, String, Boolean
from typing import Any, List, Union
from systemcheck.models.meta import Base, UniqueConstraint, \
    Column, String, generic_repr, validates, backref, QtModelMixin, \
    relationship, Boolean, Integer, ForeignKey, ChoiceType

from systemcheck.models.checks import Check


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
class CheckAbapRsusr002(Check):

    CHOICE_OPERATION = [('MERGE', 'Merge'),
                        ('INDIVIDUAL', 'Treat Individually')]

    id = Column(Integer, ForeignKey('checks_metadata.id'), primary_key=True)
    params = relationship('CheckAbapRsusr002Params')
    operation = Column(ChoiceType(CHOICE_OPERATION),
                       default = 'INDIVIUAL',
                       qt_description='Merge so that only common results are presented',
                       qt_label = 'Operator',
                       choices=CHOICE_OPERATION)

    __mapper_args__ = {
        'polymorphic_identity':'CheckAbapRsusr002Plugin',
    }

@generic_repr
class CheckAbapRsusr002Params(QtModelMixin, Base):
    """ The config data for the RSUSR002 plugin. Possible Parameters of the Function Module:

    ok: IT_USER	TYPE	SUSR_T_RANGE_4_XUBNAME	                     	Benutzerliste
    ok: IT_GROUP	TYPE	SUSR_T_SEL_OPT_GROUP	                     	Benutzergruppeliste
    ok: IT_UGROUP	TYPE	SUSR_T_SEL_OPT_GROUP	                     	Selektionsoptionen für Benutzergruppe
    ok: IT_UALIAS	TYPE	SUSR_T_SEL_OPT_ALIAS	                     	Selektionsoptionen für Alias
    ok: IT_UTYPE	TYPE	SUSR_T_SEL_OPT_UTYPE	                     	Selektionsoptionen für Benutzetyp
    ok: IT_SECPOL	TYPE	SUSR_T_SEL_OPT_SECPOL	                     	Selektionsoptionen für Sicherheitsrichtlinie
    ok: IT_SNC	TYPE	SUSR_T_SEL_OPT_SNC	                     	Selektionsoptionen für SNC
    ok: IV_USER_LOCK	TYPE	SUIM_LOCK_SEL	                     	Sperrestatus Y=gesperrt, N=nicht gesperrt, Space = irrelevant
    ok: IV_PWD_LOCK	TYPE	SUIM_LOCK_SEL	                     	Sperrestatus Y=gesperrt, N=nicht gesperrt, Space = irrelevant
    ok: IV_LOCK	TYPE	BOOLE_D	                     	Alle Benutzer mit Administrator- oder Kennwortspe: TRUE (='X') und FALSE (=' ')
    ok: IV_UNLOCK	TYPE	BOOLE_D	                     	Nur Benutzer ohne Sperren: TRUE (='X') und FALSE (=' ')
    ok: IV_FDATE	TYPE	CDDATUM	                     	Ablauf Gültigkeit von
    ok: IV_TDATE	TYPE	CDDATUM	                     	Ablauf Gültigkeit bis
    later: IT_LIC_TYPE	TYPE	SUSR_T_SEL_OPT_LIC_TYPE	                     	Selektionsoptionen für Lizenztypen
    later: IT_ACCNT	TYPE	SUSR_T_SEL_OPT_ACCNT	                     	Selektionsoptionen für Account-Id
    later: IT_KOSTL	TYPE	SUSR_T_SEL_OPT_KOSTL	                     	Selektionsoptionen für Kostenstelle
    later: IT_STCOD	TYPE	SUSR_T_SEL_OPT_STCOD	                     	Selektionsoptionen für Startmenü
    later: IT_LANGU	TYPE	SUSR_T_SEL_OPT_LANGU	                     	Selektionsoptionen für Sprache
    later: IV_DCPFM	TYPE	SUSR_T_SEL_OPT_DCPFM	                     	Dezimaldarstellung
    later: IV_DATFM	TYPE	SUSR_T_SEL_OPT_DATFM	                     	Datumsdarstellung
    later: IV_TIMEFM	TYPE	SUSR_T_SEL_OPT_TIMEFM	                     	Zeitformat (12-/24-Stundenangabe)
    later: IT_SPLD	TYPE	SUSR_T_SEL_OPT_SPLD	                     	Selektionsoptionen für Gerätenamen
    later: IV_TZONE	TYPE	TZNZONE	                     	Zeitzone
    later: IV_CATTK	TYPE	BOOLE_D	                     	Datenelement zur Domäne BOOLE: TRUE (='X') und FALSE (=' ')
    later: IT_PARID	TYPE	SUSR_T_SEL_OPT_PARID	                     	Selektionsoptionen für Set-/Get-Paramter-Id

    ok: IV_TCODE	TYPE	TCODE	                     	Transaktionscode
    ok: IV_START_TX	TYPE	BOOLE_D	                     	nur ausführbare Transaktion
    ok: IT_UREF	TYPE	SUSR_T_SEL_OPT_REF	                     	Selektionsoptionen für Referenzbenutzer
    ok: IT_ACTGRPS	TYPE	SUSR_T_SEL_OPT_AGR	                     	Selektionsoptionen für Rolle
    ok: IT_PROF1	TYPE	SUSR_T_SEL_OPT_PROF	                     	Selektionsoptionen für Profile
    ok: IV_PROF2	TYPE	XUPROFNAME	                     	Berechtigungsprofil in Benutzerstammpflege
    ok: IV_PROF3	TYPE	XUPROFNAME	                     	Berechtigungsprofil in Benutzerstammpflege
    ok: IV_CONV1	TYPE	BOOLE_D	                     	Datenelement zur Domäne BOOLE: TRUE (='X') und FALSE (=' ')
    ok: IV_AUTH_FLD	TYPE	FIELDNAME	                     	Feldname
    ok: IV_AUTH_VAL	TYPE	XUVAL	                     	Berechtigungswert
    ok: IT_OBJCT	TYPE	SUSR_T_SEL_OPT_OBJECT	                     	Selektionsoptionen für Berechtigungsobjekte
    ok: IT_AUTH	TYPE	SUSR_T_SEL_OPT_AUTH	                     	Selektionsoptionen für Berechtigungen
    ok: IV_CONV	TYPE	BOOLE_D	                     	Datenelement zur Domäne BOOLE: TRUE (='X') und FALSE (=' ')
    ok: IT_VALUES	TYPE	SUSR_T_SEL_OPT_VAL	                     	Übergabestruk. für Abgrenzungen bei Sel. nach Berecht.werten


    """

    __tablename__ = 'CheckAbapRsusr002Plugin'

    CHOICE_SUIM_LOCK_SEL = [('Y', 'Locked'),
                           ('N', 'Not Locked'),
                           (' ', 'Irrelevant')]

    id = Column(Integer, ForeignKey('checks_metadata.id'), primary_key=True)

    IT_USER = relationship('CheckAbapRsusr002Plugin__IT_USER')
    IT_GROUP = relationship('CheckAbapRsusr002Plugin__IT_GROUP')
    IT_UGROUP = relationship('CheckAbapRsusr002Plugin__IT_UGROUP')
    IT_UALIAS = relationship('CheckAbapRsusr002Plugin__IT_UALIAS')
    IT_UTYPE = relationship('CheckAbapRsusr002Plugin__IT_UTYPE')
    IT_SECPOL = relationship('CheckAbapRsusr002Plugin__IT_SECPOL')
    IT_SNC = relationship('CheckAbapRsusr002Plugin__IT_SNC')

    IV_USER_LOCK = Column(ChoiceType(CHOICE_SUIM_LOCK_SEL),
                 nullable=False,
                 default=' ',
                 qt_label='Administrator Lock',
                 qt_description='Administrator Lock Status',
                 choices=CHOICE_SUIM_LOCK_SEL
                )

    IV_PWD_LOCK = Column(ChoiceType(CHOICE_SUIM_LOCK_SEL),
                 nullable=False,
                 default=' ',
                 qt_label='Invalid Password Locks',
                 qt_description='Invalid Password Locks',
                 choices=CHOICE_SUIM_LOCK_SEL
                )

    IV_LOCK = Column(Boolean,
                     default=False,
                     qt_label='All Users with Admin and Password Locks',
                     qt_description='All Users with Admin and Password Locks',
                   )

    IV_UNLOCK = Column(Boolean,
                     default=True,
                     qt_label='Only Unlocked Users',
                     qt_description='Only Unlocked Users',
                   )

    IV_FDATE = Column(String,
                      default=True,
                      qt_label='Valid From Date',
                      qt_description='Valid From Date',
                      )

    IV_TDATE = Column(String,
                      default=True,
                      qt_label='Valid To Date',
                      qt_description='Valid To Date',
                      )

    IV_TCODE = Column(String(20),
                      default=True,
                      qt_label='Transaction Code',
                      qt_description='Transaction Code',
                      )

    IV_START_TX = Column(Boolean,
                     default=True,
                     qt_label='Only Executable Transactions',
                     qt_description='Only Executable Transactions',
                   )

    IT_UREF = relationship('CheckAbapRsusr002Plugin__IT_UREF')

    IT_ACTGRPS = relationship('CheckAbapRsusr002Plugin__IT_ACTGRPS')

    IT_PROF1 = relationship('CheckAbapRsusr002Plugin__IT_PROF1')

    IV_PROF2 = Column(String(12),
                        nullable=True,
                        qt_label='Profile Name',
                        qt_description='Authorization Profile Name',
                        )

    IV_PROF3 = Column(String(12),
                        nullable=True,
                        qt_label='Profile Name',
                        qt_description='Authorization Profile Name',
                        )

    IV_CONV1 = Column(Boolean,
                     default=False,
                     qt_label='Always Convert Value',
                     qt_description='Always Convert Value',
                   )

    IV_AUTH_FLD = Column(String(12),
                        nullable=True,
                        qt_label='Authorization Field',
                        qt_description='Authorization Field',
                        )

    IV_AUTH_VAL = Column(String(12),
                        nullable=True,
                        qt_label='Authorization Value',
                        qt_description='Authorization Value',
                        )

    IT_OBJCT = relationship('CheckAbapRsusr002Plugin__IT_OBJCT')
    IT_AUTH = relationship('CheckAbapRsusr002Plugin__IT_AUTH')

    IV_CONV = Column(Boolean,
                     default=False,
                     qt_label='Always Convert Value',
                     qt_description='Always Convert Value',
                   )

    IT_VALUES = relationship('CheckAbapRsusr002Plugin__IT_VALUES')


@generic_repr
class CheckAbapRsusr002Plugin__IT_USER(QtModelMixin, Base, StandardAuthSelectionOptionMixin):
    """ Selection Options for Users"""
    __tablename__ = 'CheckAbapRsusr002Plugin__IT_USER'


    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('CheckAbapRsusr002Plugin.id'))

    LOW = Column(String(12),
                 nullable=False,
                 qt_label='User Name in User Master Record',
                 qt_description='User Name in User Master Record. Must be specified.',
                )

    HIGH = Column(String(12),
                 nullable=True,
                 qt_label='User Name in User Master Record',
                 qt_description='User Name in User Master Record (Upper range limit). Optional.',
                )

@generic_repr
class CheckAbapRsusr002Plugin__IT_GROUP(QtModelMixin, Base, StandardAuthSelectionOptionMixin):
    """ Selection Options for Groups """
    __tablename__ = 'CheckAbapRsusr002Plugin__IT_GROUP'


    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('CheckAbapRsusr002Plugin.id'))

    LOW = Column(String(12),
                 nullable=False,
                 qt_label='User Group',
                 qt_description='User Goup. Must be specified.',
                )

    HIGH = Column(String(12),
                 nullable=True,
                 qt_label='User Group',
                 qt_description='User Group (Upper range limit). Optional.',
                )

@generic_repr
class CheckAbapRsusr002Plugin__IT_UGROUP(QtModelMixin, Base, StandardAuthSelectionOptionMixin):
    """ Selection Options for User Groups  """

    __tablename__ = 'CheckAbapRsusr002Plugin__IT_GROUP'


    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('CheckAbapRsusr002Plugin.id'))

    LOW = Column(String(12),
                 nullable=False,
                 qt_label='User Group',
                 qt_description='User Goup. Must be specified.',
                )

    HIGH = Column(String(12),
                 nullable=True,
                 qt_label='User Group',
                 qt_description='User Group (Upper range limit). Optional.',
                )

@generic_repr
class CheckAbapRsusr002Plugin__IT_UALIAS(QtModelMixin, Base, StandardAuthSelectionOptionMixin):
    """ Selection Options for User Aliases """
    __tablename__ = 'CheckAbapRsusr002Plugin__IT_UALIAS'


    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('CheckAbapRsusr002Plugin.id'))

    LOW = Column(String(40),
                 nullable=False,
                 qt_label='User Alias',
                 qt_description='User Alias',
                )

    HIGH = Column(String(40),
                 nullable=True,
                 qt_label='User Alias',
                 qt_description='User Alias',
                )

@generic_repr
class CheckAbapRsusr002Plugin__IT_UTYPE(QtModelMixin, Base, StandardAuthSelectionOptionMixin):
    """ Selection Options for User Types """
    __tablename__ = 'CheckAbapRsusr002Plugin__IT_UTYPE'

    CHOICE_USERTYPE = [('A', 'Dialog'),
                       ('B', 'System'),
                       ('C', 'Communications Data'),
                       ('L', 'Reference (Logn not possible)'),
                       ('S', 'Service')]


    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('CheckAbapRsusr002Plugin.id'))

    LOW = Column(ChoiceType(CHOICE_USERTYPE),
                 nullable=False,
                 default='A',
                 qt_label='User Type',
                 qt_description='User Type',
                 choices=CHOICE_USERTYPE
                )

    HIGH = Column(ChoiceType(CHOICE_USERTYPE),
                 nullable=True,
                 qt_label='User Type',
                 qt_description='User Type',
                 choices=CHOICE_USERTYPE
                )

@generic_repr
class CheckAbapRsusr002Plugin__IT_SECPOL(QtModelMixin, Base, StandardAuthSelectionOptionMixin):
    """ Selection Options for Security Policy """
    __tablename__ = 'CheckAbapRsusr002Plugin__IT_SECPOL'


    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('CheckAbapRsusr002Plugin.id'))

    LOW = Column(String(40),
                 nullable=False,
                 qt_label='Security Policy',
                 qt_description='Security Policy. Must be specified.',
                )

    HIGH = Column(String(40),
                 nullable=True,
                 qt_label='Security Policy',
                 qt_description='Security Policy (Upper range limit). Optional.',
                )

@generic_repr
class CheckAbapRsusr002Plugin__IT_SNC(QtModelMixin, Base, StandardAuthSelectionOptionMixin):
    """ Selection Options for SNC """

    __tablename__ = 'CheckAbapRsusr002Plugin__IT_SNC'


    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('CheckAbapRsusr002Plugin.id'))

    LOW = Column(String(255),
                 nullable=False,
                 qt_label='SNC: Printable Name',
                 qt_description='SNC Printable Name',
                )

    HIGH = Column(String(255),
                 nullable=True,
                 qt_label='SNC: Printable Name',
                 qt_description='SNC: Printable Name',
                )

@generic_repr
class CheckAbapRsusr002Plugin__IT_ACTGRPS(QtModelMixin, Base, StandardAuthSelectionOptionMixin):
    """ Selection Options for Roles """
    __tablename__ = 'CheckAbapRsusr002Plugin__IT_ACTGRPS'


    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('CheckAbapRsusr002Plugin.id'))

    LOW = Column(String(30),
                 nullable=False,
                 qt_label='Role Name',
                 qt_description='Role Name',
                )

    HIGH = Column(String(30),
                 nullable=True,
                 qt_label='Role Name',
                 qt_description='Role Name',
                )

@generic_repr
class CheckAbapRsusr002Plugin__IT_PROF1(QtModelMixin, Base, StandardAuthSelectionOptionMixin):
    """ Selection Options for Profiles """
    __tablename__ = 'CheckAbapRsusr002Plugin__IT_PROF1'


    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('CheckAbapRsusr002Plugin.id'))

    LOW = Column(String(12),
                 nullable=False,
                 qt_label='Profile Name',
                 qt_description='Profile Name',
                )

    HIGH = Column(String(12),
                 nullable=True,
                 qt_label='Profile Name',
                 qt_description='Profile Name',
                )

@generic_repr
class CheckAbapRsusr002Plugin__IT_OBJCT(QtModelMixin, Base, StandardAuthSelectionOptionMixin):

    __tablename__ = 'CheckAbapRsusr002Plugin__IT_OBJCT'


    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('CheckAbapRsusr002Plugin.id'))

    LOW = Column(String(10),
                 nullable=False,
                 qt_label='Authorization Object',
                 qt_description='Authorization Object',
                )

    HIGH = Column(String(10),
                 nullable=True,
                 qt_label='Authorzation Object',
                 qt_description='Authorization Object',
                )

@generic_repr
class CheckAbapRsusr002Plugin__IT_AUTH(QtModelMixin, Base, StandardAuthSelectionOptionMixin):
    """ Selection Options for Authorizations """

    __tablename__ = 'CheckAbapRsusr002Plugin__IT_AUTH'


    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('CheckAbapRsusr002Plugin.id'))

    LOW = Column(String(12),
                 nullable=False,
                 qt_label='Auth. Name',
                 qt_description='Auth. Name',
                )

    HIGH = Column(String(12),
                 nullable=True,
                 qt_label='Auth. Name',
                 qt_description='Auth. Name',
                )

@generic_repr
class CheckAbapRsusr002Plugin__IT_VALUES(QtModelMixin, Base):
    """ Sel. According to Authorization Values """

    __tablename__ = 'CheckAbapRsusr002Plugin__IT_AUTH'


    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('CheckAbapRsusr002Plugin.id'))

    NR = Column(String(1),
                 nullable=False,
                 qt_label='Auth. Name',
                 qt_description='Auth. Name',
                )

    OBJCT = Column(String(10),
                 nullable=False,
                 qt_label='Auth. Object',
                 qt_description='Auth. Object',
                )

    FIELD = Column(String(10),
                 nullable=False,
                 qt_label='Value',
                 qt_description='Value',
                )

    VAL1 = Column(String(40),
                 nullable=False,
                 qt_label='Value',
                 qt_description='Value',
                )

    VAL2 = Column(String(40),
                 nullable=True,
                 qt_label='Value',
                 qt_description='Value',
                )

    VAL3 = Column(String(40),
                 nullable=True,
                 qt_label='Value',
                 qt_description='Value',
                )

    VAL4 = Column(String(40),
                 nullable=True,
                 qt_label='Value',
                 qt_description='Value',
                )

    VAL5 = Column(String(40),
                 nullable=True,
                 qt_label='Value',
                 qt_description='Value',
                )

@generic_repr
class CheckAbapRsusr002Plugin__IT_UREF(QtModelMixin, Base, StandardAuthSelectionOptionMixin):
    """ Selection Options for Reference Users """
    __tablename__ = 'CheckAbapRsusr002Plugin__IT_UREF'


    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('CheckAbapRsusr002Plugin.id'))

    LOW = Column(String(12),
                 nullable=False,
                 qt_label='Reference User',
                 qt_description='Refernce User',
                )

    HIGH = Column(String(12),
                 nullable=True,
                 qt_label='Reference User',
                 qt_description='Refernce User',
                )

