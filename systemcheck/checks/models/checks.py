# define authorship information

__authors__     = ['Lars Fasel']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2017'
__license__     = 'MIT'

# maintanence information
__maintainer__  = 'Lars Fasel'
__email__       = 'systemcheck@team-fasel.com'



from systemcheck.models.meta import Base, SurrogatePK, SurrogateUuidPK, UniqueConstraint, \
    Column, String, CHAR, generic_repr, validates, backref, QtModelMixin, \
    Integer, ForeignKey, ChoiceType, UUIDType, relationship, RichString, qtRelationship, OperatorMixin


from systemcheck.models.meta.orm_choices import choices
from systemcheck.models.meta.systemcheck_choices import OperatorChoice, InclusionChoice, \
    CheckFailCriteriaOptions

#from systemcheck.session import SESSION

from typing import Any
from sqlalchemy.inspection import inspect
from typing import Union, List
from pprint import pprint
import systemcheck
from systemcheck.models.meta.orm_choices import choices

@choices
class OptionChoice:
    class Meta:
        NE = ['NE', 'not equal']
        EQ = ['EQ', 'equal']
        GT = ['GT', 'greater']
        GE = ['GT', 'greater or equal']
        LT = ['LT', 'lower']
        LE = ['LE', 'lower or equal']


class StandardAbapAuthSelectionOptionMixin:

    SIGN = Column(String,
                  nullable = False,
                  default = InclusionChoice.INCLUDE,
                  qt_label = 'Incl./Excl.',
                  qt_description = 'Should the specified items be included or excluded? Default is to include them',
                  choices = InclusionChoice.CHOICES
    )

    OPTION = Column(String,
                  nullable = False,
                  default = OptionChoice.EQ,
                  qt_label = 'Sel. Option',
                  qt_description = 'Selection option',
                  choices = OptionChoice.CHOICES,
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
class Check(QtModelMixin, Base):
    """ The Generic Data Model of a Check

    Similar to the generic tree for systems, this is a tree structure for checks.
    """

    __tablename__ = 'checks_metadata'

    __table_args__ = (
        UniqueConstraint("type", "name"),
        {'extend_existing' : True}
    )

    id = Column(Integer, primary_key=True, qt_show=False)

    parent_id = Column(Integer, ForeignKey('checks_metadata.id'), qt_label='Parent Key', qt_show=False)

    name = Column(String(250),
                  nullable=False,
                  qt_label='Folder or Check Name',
                  qt_description='Name of the check or folder',
                  qt_show=True
                  )

    children = relationship('Check',
                          cascade="all, delete-orphan",
                          backref=backref("parent_node", remote_side=id),
                          )

    type = Column(String(250),
                        nullable=False,
                        qt_label='Node Type',
                        qt_description='Node Type',
                        qt_show=False
                        )

    description = Column(RichString,
                         nullable=True,
                         qt_label='Check Description',
                         qt_description='Brief description what the check does',
                         qt_show=False,
                         )

    failcriteria = Column(String,
                       default = CheckFailCriteriaOptions.FAIL_IF_ANY_FAILS,
                       qt_description='Defines when a check is considered as failed. ',
                       qt_label = 'Fail Criteria',
                       choices=CheckFailCriteriaOptions.CHOICES,
                       qt_show=True)

    __qtmap__ = [name, description]



    def _parameter_count(self):
        count = len(self.params)

        return count

    def _restriction_count(self):
        return len(self.restrictions)

    __mapper_args__ = {
        'polymorphic_identity':'FOLDER',
        'polymorphic_on':type,
    }
