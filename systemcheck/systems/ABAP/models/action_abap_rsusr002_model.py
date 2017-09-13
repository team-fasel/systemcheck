from systemcheck.checks.models.checks import Check
from systemcheck.models.meta import Base, ChoiceType, Column, ForeignKey, Integer, QtModelMixin, String, qtRelationship, \
    relationship, RichString, generic_repr, Boolean
from systemcheck.systems.ABAP.models import ActionABAPIsClientSpecificMixin, StandardAuthSelectionOptionMixin

@generic_repr
class ActionAbapRsusr002(Check, ActionABAPIsClientSpecificMixin):

    CHOICE_OPERATION = [('MERGE', 'Merge'),
                        ('INDIVIDUAL', 'Treat Individually')]

    __tablename__ = 'ActionAbapRsusr002Plugin'

    __table_args__ = {'extend_existing':True}

    id = Column(Integer, ForeignKey('checks_metadata.id'), primary_key=True)
    params = relationship('ActionAbapRsusr002')
    operation = Column(ChoiceType(CHOICE_OPERATION),
                       default = 'INDIVIUAL',
                       qt_description='Merge so that only common results are presented',
                       qt_label = 'Operator',
                       choices=CHOICE_OPERATION)

    __mapper_args__ = {
        'polymorphic_identity':'ActionAbapRsusr002',
    }

@generic_repr
class ActionAbapRsusr002__params(QtModelMixin, Base):
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

    __tablename__ = 'ActionAbapRsusr002__params'

    __table_args__ = {'extend_existing':True}

    CHOICE_SUIM_LOCK_SEL = [('Y', 'Locked'),
                           ('N', 'Not Locked'),
                           (' ', 'Irrelevant')]

    id = Column(Integer, ForeignKey('checks_metadata.id'), primary_key=True)

    IT_USER = relationship('ActionAbapRsusr002__IT_USER')
    IT_GROUP = relationship('ActionAbapRsusr002__IT_GROUP')
    IT_UGROUP = relationship('ActionAbapRsusr002__IT_UGROUP')
    IT_UALIAS = relationship('ActionAbapRsusr002__IT_UALIAS')
    IT_UTYPE = relationship('ActionAbapRsusr002__IT_UTYPE')
    IT_SECPOL = relationship('ActionAbapRsusr002__IT_SECPOL')
    IT_SNC = relationship('ActionAbapRsusr002__IT_SNC')

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

    IT_UREF = relationship('ActionAbapRsusr002__IT_UREF')

    IT_ACTGRPS = relationship('ActionAbapRsusr002__IT_ACTGRPS')

    IT_PROF1 = relationship('ActionAbapRsusr002__IT_PROF1')

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

    IT_OBJCT = relationship('ActionAbapRsusr002__IT_OBJCT')
    IT_AUTH = relationship('ActionAbapRsusr002__IT_AUTH')

    IV_CONV = Column(Boolean,
                     default=False,
                     qt_label='Always Convert Value',
                     qt_description='Always Convert Value',
                   )

    IT_VALUES = relationship('ActionAbapRsusr002__IT_VALUES')


@generic_repr
class ActionAbapRsusr002__IT_USER(QtModelMixin, Base, StandardAuthSelectionOptionMixin):
    """ Selection Options for Users"""
    __tablename__ = 'ActionAbapRsusr002__IT_USER'
    __table_args__ = {'extend_existing':True}

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('ActionAbapRsusr002.id'))

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
class ActionAbapRsusr002__IT_GROUP(QtModelMixin, Base, StandardAuthSelectionOptionMixin):
    """ Selection Options for Groups """
    __tablename__ = 'ActionAbapRsusr002__IT_GROUP'
    __table_args__ = {'extend_existing':True}

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('ActionAbapRsusr002.id'))

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
class ActionAbapRsusr002__IT_UGROUP(QtModelMixin, Base, StandardAuthSelectionOptionMixin):
    """ Selection Options for User Groups  """

    __tablename__ = 'ActionAbapRsusr002__IT_GROUP'
    __table_args__ = {'extend_existing':True}

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('ActionAbapRsusr002.id'))

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
class ActionAbapRsusr002__IT_UALIAS(QtModelMixin, Base, StandardAuthSelectionOptionMixin):
    """ Selection Options for User Aliases """
    __tablename__ = 'ActionAbapRsusr002__IT_UALIAS'
    __table_args__ = {'extend_existing':True}

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('ActionAbapRsusr002.id'))

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
class ActionAbapRsusr002__IT_UTYPE(QtModelMixin, Base, StandardAuthSelectionOptionMixin):
    """ Selection Options for User Types """
    __tablename__ = 'ActionAbapRsusr002__IT_UTYPE'
    __table_args__ = {'extend_existing':True}

    CHOICE_USERTYPE = [('A', 'Dialog'),
                       ('B', 'System'),
                       ('C', 'Communications Data'),
                       ('L', 'Reference (Logn not possible)'),
                       ('S', 'Service')]


    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('ActionAbapRsusr002.id'))

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
class ActionAbapRsusr002__IT_SECPOL(QtModelMixin, Base, StandardAuthSelectionOptionMixin):
    """ Selection Options for Security Policy """
    __tablename__ = 'ActionAbapRsusr002__IT_SECPOL'
    __table_args__ = {'extend_existing':True}


    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('ActionAbapRsusr002.id'))

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
class ActionAbapRsusr002__IT_SNC(QtModelMixin, Base, StandardAuthSelectionOptionMixin):
    """ Selection Options for SNC """

    __tablename__ = 'ActionAbapRsusr002__IT_SNC'
    __table_args__ = {'extend_existing':True}


    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('ActionAbapRsusr002.id'))

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
class ActionAbapRsusr002__IT_ACTGRPS(QtModelMixin, Base, StandardAuthSelectionOptionMixin):
    """ Selection Options for Roles """
    __tablename__ = 'ActionAbapRsusr002__IT_ACTGRPS'
    __table_args__ = {'extend_existing':True}


    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('ActionAbapRsusr002.id'))

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
class ActionAbapRsusr002__IT_PROF1(QtModelMixin, Base, StandardAuthSelectionOptionMixin):
    """ Selection Options for Profiles """
    __tablename__ = 'ActionAbapRsusr002__IT_PROF1'
    __table_args__ = {'extend_existing':True}


    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('ActionAbapRsusr002.id'))

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
class ActionAbapRsusr002__IT_OBJCT(QtModelMixin, Base, StandardAuthSelectionOptionMixin):

    __tablename__ = 'ActionAbapRsusr002__IT_OBJCT'
    __table_args__ = {'extend_existing':True}


    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('ActionAbapRsusr002.id'))

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
class ActionAbapRsusr002__IT_AUTH(QtModelMixin, Base, StandardAuthSelectionOptionMixin):
    """ Selection Options for Authorizations """

    __tablename__ = 'ActionAbapRsusr002__IT_AUTH'
    __table_args__ = {'extend_existing':True}


    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('ActionAbapRsusr002.id'))

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
class ActionAbapRsusr002__IT_VALUES(QtModelMixin, Base):
    """ Sel. According to Authorization Values """

    __tablename__ = 'ActionAbapRsusr002__IT_AUTH'
    __table_args__ = {'extend_existing':True}


    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('ActionAbapRsusr002.id'))

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
class ActionAbapRsusr002__IT_UREF(QtModelMixin, Base, StandardAuthSelectionOptionMixin):
    """ Selection Options for Reference Users """
    __tablename__ = 'ActionAbapRsusr002__IT_UREF'
    __table_args__ = {'extend_existing':True}


    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('ActionAbapRsusr002.id'))

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

