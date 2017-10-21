from systemcheck.checks.models.checks import Check
from systemcheck.models.meta import Base, ChoiceType, Column, ForeignKey, Integer, QtModelMixin, String, qtRelationship, \
    relationship, RichString, generic_repr, Boolean, OperatorMixin, BaseMixin
from systemcheck.models.meta.orm_choices import choices
from systemcheck.systems.ABAP.models import ActionAbapIsClientSpecificMixin, StandardAuthSelectionOptionMixin


@choices
class ActionAbapRsusr002ResultConsolidationChoice:
    class Meta:
        MERGE = ['MERGE', 'Merge All Parameter Sets']
        INDIVIDUAL = ['INDIVIDUAL', 'Treat each result set individually']

@generic_repr
class ActionAbapRsusr002(Check, ActionAbapIsClientSpecificMixin):

    __tablename__ = 'ActionAbapRsusr002'

    __table_args__ = {'extend_existing':True}

    id = Column(Integer, ForeignKey('checks_metadata.id'), primary_key=True)
    params = relationship('ActionAbapRsusr002__params', cascade="all, delete-orphan")
    consolidation = Column(Integer,
                           default = ActionAbapRsusr002ResultConsolidationChoice.INDIVIDUAL,
                           qt_description='Merge so that only common results are presented',
                           qt_label = 'Result Set Merge Strategy',
                           choices=ActionAbapRsusr002ResultConsolidationChoice.CHOICES)

    __qtmap__ = [Check.name, Check.description, Check.failcriteria, consolidation]

    __mapper_args__ = {
        'polymorphic_identity':'ActionAbapRsusr002',
    }

@generic_repr
class ActionAbapRsusr002__params(QtModelMixin, Base, BaseMixin):
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

    check = relationship("ActionAbapRsusr002", back_populates="params")


    id = Column(Integer, ForeignKey('checks_metadata.id'), primary_key=True)

    param_set_name = Column(String,
                            qt_label='Parameter Set Name',
                            qt_description='Parameter Set Description')

    IT_USER = qtRelationship('ActionAbapRsusr002__IT_USER', qt_label='User')
    IT_GROUP = qtRelationship('ActionAbapRsusr002__IT_GROUP', qt_label='Group for Authorization')
    IT_UGROUP = qtRelationship('ActionAbapRsusr002__IT_UGROUP', qt_label='User group (general)')
    IT_UALIAS = qtRelationship('ActionAbapRsusr002__IT_UALIAS', qt_label='Alias')
    IT_UTYPE = qtRelationship('ActionAbapRsusr002__IT_UTYPE', qt_label='User Type')
    IT_SECPOL = qtRelationship('ActionAbapRsusr002__IT_SECPOL', qt_label='Security Policy')
    IT_SNC = qtRelationship('ActionAbapRsusr002__IT_SNC', qt_label='SNC Name')

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
                      qt_label='Valid From Date',
                      qt_description='Valid From Date',
                      )

    IV_TDATE = Column(String,
                      qt_label='Valid To Date',
                      qt_description='Valid To Date',
                      )

    IV_TCODE = Column(String(20),
                      default='',
                      qt_label='Transaction Code',
                      qt_description='Transaction Code',
                      )

    IV_START_TX = Column(Boolean,
                     default=True,
                     qt_label='Only Executable Transactions',
                     qt_description='Only Executable Transactions',
                   )

    IT_UREF = qtRelationship('ActionAbapRsusr002__IT_UREF', qt_label='Reference User')

    IT_ACTGRPS = qtRelationship('ActionAbapRsusr002__IT_ACTGRPS', qt_label='Role')

    IT_PROF1 = qtRelationship('ActionAbapRsusr002__IT_PROF1', qt_label='Profile Name')

    IV_PROF2 = Column(String(12),
                        nullable=True,
                        qt_label='AND Profile',
                        qt_description='Additional Authorization Profile Name',
                        )

    IV_PROF3 = Column(String(12),
                        nullable=True,
                        qt_label='AND Profile',
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

    IT_OBJCT = qtRelationship('ActionAbapRsusr002__IT_OBJCT', qt_label='Authorization Object')
    IT_AUTH = qtRelationship('ActionAbapRsusr002__IT_AUTH', qt_label='Authorization')

    IV_CONV = Column(Boolean,
                     default=False,
                     qt_label='Always Convert Value',
                     qt_description='Always Convert Value',
                   )

    IT_VALUES = qtRelationship('ActionAbapRsusr002__IT_VALUES')

    __qtmap__ = [param_set_name, IV_PWD_LOCK, IV_TCODE, IT_USER, IT_GROUP, IT_UGROUP]


@generic_repr
class ActionAbapRsusr002__IT_USER(Base, StandardAuthSelectionOptionMixin, BaseMixin):
    """ Selection Options for Users"""
    __tablename__ = 'ActionAbapRsusr002__IT_USER'

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('ActionAbapRsusr002__params.id'))

    LOW = Column(String(12),
                 nullable=False,
                 default='',
                 qt_label='User Name in User Master Record',
                 qt_description='User Name in User Master Record. Must be specified.',
                )

    HIGH = Column(String(12),
                 nullable=True,
                 default='',
                 qt_label='User Name in User Master Record',
                 qt_description='User Name in User Master Record (Upper range limit). Optional.',
                )

    paramset = qtRelationship("ActionAbapRsusr002__params", back_populates="IT_USER")


@generic_repr
class ActionAbapRsusr002__IT_GROUP(Base, StandardAuthSelectionOptionMixin, BaseMixin):
    """ Selection Options for Groups """
    __tablename__ = 'ActionAbapRsusr002__IT_GROUP'
    __table_args__ = {'extend_existing':True}

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('ActionAbapRsusr002__params.id'))

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

    paramset = qtRelationship("ActionAbapRsusr002__params", back_populates="IT_GROUP")


@generic_repr
class ActionAbapRsusr002__IT_UGROUP(Base, StandardAuthSelectionOptionMixin, BaseMixin):
    """ Selection Options for User Groups  """

    __tablename__ = 'ActionAbapRsusr002__IT_UGROUP'
    __table_args__ = {'extend_existing':True}

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('ActionAbapRsusr002__params.id'))

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

    paramset = qtRelationship("ActionAbapRsusr002__params", back_populates="IT_UGROUP")


@generic_repr
class ActionAbapRsusr002__IT_UALIAS(Base, StandardAuthSelectionOptionMixin, BaseMixin):
    """ Selection Options for User Aliases """
    __tablename__ = 'ActionAbapRsusr002__IT_UALIAS'

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('ActionAbapRsusr002__params.id'))

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

    paramset = qtRelationship("ActionAbapRsusr002__params", back_populates="IT_UALIAS")


@generic_repr
class ActionAbapRsusr002__IT_UTYPE(Base, StandardAuthSelectionOptionMixin, BaseMixin):
    """ Selection Options for User Types """
    __tablename__ = 'ActionAbapRsusr002__IT_UTYPE'
    __table_args__ = {'extend_existing':True}

    CHOICE_USERTYPE = [('A', 'Dialog'),
                       ('B', 'System'),
                       ('C', 'Communications Data'),
                       ('L', 'Reference (Logn not possible)'),
                       ('S', 'Service')]


    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('ActionAbapRsusr002__params.id'))

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

    paramset = qtRelationship("ActionAbapRsusr002__params", back_populates="IT_UTYPE")


@generic_repr
class ActionAbapRsusr002__IT_SECPOL(Base, StandardAuthSelectionOptionMixin, BaseMixin):
    """ Selection Options for Security Policy """
    __tablename__ = 'ActionAbapRsusr002__IT_SECPOL'
    __table_args__ = {'extend_existing':True}


    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('ActionAbapRsusr002__params.id'))

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

    paramset = qtRelationship("ActionAbapRsusr002__params", back_populates="IT_SECPOL")


@generic_repr
class ActionAbapRsusr002__IT_SNC(Base, StandardAuthSelectionOptionMixin, BaseMixin):
    """ Selection Options for SNC """

    __tablename__ = 'ActionAbapRsusr002__IT_SNC'
    __table_args__ = {'extend_existing':True}


    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('ActionAbapRsusr002__params.id'))

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

    paramset = qtRelationship("ActionAbapRsusr002__params", back_populates="IT_SNC")


@generic_repr
class ActionAbapRsusr002__IT_ACTGRPS(Base, StandardAuthSelectionOptionMixin, BaseMixin):
    """ Selection Options for Roles """
    __tablename__ = 'ActionAbapRsusr002__IT_ACTGRPS'
    __table_args__ = {'extend_existing':True}


    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('ActionAbapRsusr002__params.id'))

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

    paramset = qtRelationship("ActionAbapRsusr002__params", back_populates="IT_ACTGRPS")


@generic_repr
class ActionAbapRsusr002__IT_PROF1(Base, StandardAuthSelectionOptionMixin, BaseMixin):
    """ Selection Options for Profiles """
    __tablename__ = 'ActionAbapRsusr002__IT_PROF1'

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('ActionAbapRsusr002__params.id'))

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

    paramset = qtRelationship("ActionAbapRsusr002__params", back_populates="IT_PROF1")


@generic_repr
class ActionAbapRsusr002__IT_OBJCT(Base, StandardAuthSelectionOptionMixin, BaseMixin):

    __tablename__ = 'ActionAbapRsusr002__IT_OBJCT'
    __table_args__ = {'extend_existing':True}


    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('ActionAbapRsusr002__params.id'))

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

    paramset = qtRelationship("ActionAbapRsusr002__params", back_populates="IT_OBJCT")


@generic_repr
class ActionAbapRsusr002__IT_AUTH(Base, StandardAuthSelectionOptionMixin, BaseMixin):
    """ Selection Options for Authorizations """

    __tablename__ = 'ActionAbapRsusr002__IT_AUTH'
    __table_args__ = {'extend_existing':True}


    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('ActionAbapRsusr002__params.id'))

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

    paramset = qtRelationship("ActionAbapRsusr002__params", back_populates="IT_AUTH")


@generic_repr
class ActionAbapRsusr002__IT_VALUES(QtModelMixin, Base, BaseMixin):
    """ Sel. According to Authorization Values """

    __tablename__ = 'ActionAbapRsusr002__IT_VALUES'

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('ActionAbapRsusr002__params.id'))

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

    paramset = qtRelationship("ActionAbapRsusr002__params", back_populates="IT_VALUES")


@generic_repr
class ActionAbapRsusr002__IT_UREF(Base, StandardAuthSelectionOptionMixin, BaseMixin):
    """ Selection Options for Reference Users """
    __tablename__ = 'ActionAbapRsusr002__IT_UREF'
    __table_args__ = {'extend_existing':True}


    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('ActionAbapRsusr002__params.id'))

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

    paramset = qtRelationship("ActionAbapRsusr002__params", back_populates="IT_UREF")
