# define authorship information

__authors__     = ['Lars Fasel']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2017'
__license__     = 'GNU AGPLv3'

# maintanence information
__maintainer__  = 'Lars Fasel'
__email__       = 'systemcheck@team-fasel.com'



from systemcheck.models.meta import Base, SurrogatePK, SurrogateUuidPK, UniqueConstraint, \
    Column, String, CHAR, generic_repr, validates, backref, QtModelMixin, BaseMixin, \
    Integer, ForeignKey, ChoiceType, UUIDType, relationship, RichString, qtRelationship, OperatorMixin, TableNameMixin


from systemcheck.models.meta.orm_choices import choices
from systemcheck.models.meta.systemcheck_choices import OperatorChoice, InclusionChoice

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

@choices
class CriticalityChoice:
    class Meta:
        VERYHIGH = ['VERYHIGH', 'Very High']
        HIGH = ['HIGH', 'High']
        MEDIUM = ['MEDIUM', 'Medium']
        LOW = ['LOW', 'Low']
        INFO = ['INFO', 'Info']


@choices
class CheckFailCriteriaOptions:
    class Meta:
        FAIL_IF_ANY_FAILS = ['FAIL_IF_ANY_FAILS', 'Fail check if any parameter set fails']
        FAIL_IF_ALL_FAIL = ['FAIL_IF_ALL_FAIL', 'Fail check if all parameter sets fail']
        NO_RATING = ['NO_RATING', 'No Rating, just Information']


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
class CheckTreeStructure(QtModelMixin, Base, BaseMixin, TableNameMixin):

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


    description = Column(RichString,
                         nullable=True,
                         qt_label='Check Description',
                         qt_description='Brief description what the check does',
                         )


    children = relationship('CheckTreeStructure',
                          cascade="all, delete-orphan",
                          backref=backref("parent_node", remote_side=id),
                          )

    type = Column(String(250),
                        nullable=False,
                        qt_label='Node Type',
                        qt_description='Node Type',
                        )

    __qtmap__ = [name, description]

    __icon__ = ':Folder'


    __mapper_args__ = {
        'polymorphic_identity':'CheckFolder',
        'polymorphic_on':type,
    }



@generic_repr
class Check(CheckTreeStructure):
    """ The Generic Data Model of a Check

    Similar to the generic tree for systems, this is a tree structure for checks.
    """

    __tablename__ = 'checks_metadata'

    __table_args__ = (
        UniqueConstraint("type", "name"),
        {'extend_existing' : True}
    )


    criticality = Column(String,
                  nullable=False,
                  qt_label='Criticality',
                  qt_description='Describes the criticality of the finding or whether it is informational only',
                  choices=CriticalityChoice.CHOICES,
                  default=CriticalityChoice.INFO
                  )

    failcriteria = Column(String,
                       default = CheckFailCriteriaOptions.FAIL_IF_ANY_FAILS,
                       qt_description='Defines when a check is considered as failed. ',
                       qt_label = 'Fail Criteria',
                       choices=CheckFailCriteriaOptions.CHOICES,
                          )

    technical_name = Column(String,
                            qt_label='Technical Name',
                            qt_description='Each Check has a unique technical name')

    __qtmap__ = [CheckTreeStructure.name, CheckTreeStructure.description, criticality, failcriteria]

    __icon__ = ':Checkmark'



    def _parameter_count(self):
        count = len(self.params)

        return count

    def _restriction_count(self):
        return len(self.restrictions)

    def _add_parameter_set(self, parameterDict):

        paramClass = Base._decl_class_registry.get(self.__class__.__name__+'__params')
        if paramClass:
            paramObject=paramClass(**parameterDict)

            self.params.append(paramObject)

    __mapper_args__ = {
        'polymorphic_identity':'Check',
    }
