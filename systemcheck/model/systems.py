# define authorship information
__authors__     = ['Lars Fasel']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2017'
__license__     = 'MIT'

# maintanence information
__maintainer__  = 'Lars Fasel'
__email__       = 'systemcheck@team-fasel.com'

from .meta import Base, Column, Integer, QtModelMixin, String, UniqueConstraint, \
    generic_repr



@generic_repr
class Credential(Base, QtModelMixin):
    __tablename__ = 'credentials'

    id = Column(Integer, primary_key=True)
    application = Column(String(250), nullable=False,  unique=False)
    description = Column(String(250), nullable=False,  unique=True)
    username = Column(String(40), unique=False, nullable=False)
    type = Column(String(40), unique=False, nullable=False, default='Password')
    uq_application_description_username = UniqueConstraint(application, description, username)


