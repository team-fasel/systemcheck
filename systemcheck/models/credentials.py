# define authorship information
__authors__     = ['Lars Fasel']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2017'
__license__     = 'MIT'

# maintanence information
__maintainer__  = 'Lars Fasel'
__email__       = 'systemcheck@team-fasel.com'

from systemcheck.models.meta import Base, Column, Integer, QtModelMixin, String, UniqueConstraint, generic_repr, \
    ChoiceType


@generic_repr
class Credential(Base, QtModelMixin):
    __tablename__ = 'credentials'
    __table_args__ = {'extend_existing': True}

    APPLICATIONS=[
                        ('1', 'ABAP'),
                        ('2', 'Windows'),
                        ('3', 'Generic'),
                ]

    CREDTYPE=[('1', 'Password')]

    id = Column(Integer, primary_key=True, qt_show=True)
    application = Column(ChoiceType(APPLICATIONS),
                         nullable=False,
                         unique=False,
                         qt_show=False,
                         qt_description="Application in case it's an application specific credential.",
                         default='1')
    description = Column(String(250),
                         nullable=False,
                         unique=False,
                         default='',
                         qt_show=True)
    username = Column(String(128),
                      unique=False,
                      nullable=False,
                      qt_show=True)
    type = Column(ChoiceType(CREDTYPE),
                  unique=False,
                  nullable=False,
                  default='1',
                  qt_show=True,
                  qt_description='Credential type. For now only Passwords and ABAP SSO through SNC are supported')

    uq_application_description_username = UniqueConstraint(application, description, username)

