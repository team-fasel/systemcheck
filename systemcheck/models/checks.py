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



from systemcheck.models.meta import Base, SurrogatePK, SurrogateUuidPK, UniqueConstraint, \
    Column, String, CHAR, generic_repr, validates, backref, QtModelMixin, \
    Integer, ForeignKey, ChoiceType, UUIDType

import inspect
from typing import Any


class StandardAbapAuthSelectionOptionMixin:


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
class Check(Base, QtModelMixin):
    """ The Generic Data Model of a Check

    Similar to the generic tree for systems, this is a tree structure for checks.
    """

    __tablename__ = 'checks_metadata'

    SYSTEM_TYPE_CHOICES=[
                        ('ABAP', 'ABAP System'),
                    ]

    id = Column(Integer, primary_key=True)

    parent_node = Column(Integer, ForeignKey('checks_metadata.id'), qt_label='Parent Key', qt_show=False)

    children=relationship('checks_metadata',
                          cascade="all, delete-orphan",
                          backref=backref("parent_node", remote_side=id),
                          )


    classname = Column(String(250),
                        nullable=False,
                        qt_label='Plugin Class Name',
                        qt_description='Name of the Plugin Class',
                        )

    name = Column(String(250),
                  nullable=False,
                  qt_label='Folder or Check Name',
                  qt_description='Name of the check or folder',
                  )

    description = Column(String,
                         nullable=False,
                         qt_label='Check Description',
                         qt_description='Name of the check that describes it briefly',
                         )


    __mapper_args__ = {
        'polymorphic_identity':'folder',
        'polymorphic_on':classname
    }

    __table_args__ = (
        UniqueConstraint("classname", "name"),
    )

    def _dump(self, _indent:int=0)->str:
        """ Recursively return the structure of the node and all its children as text """
        return "   " * _indent + repr(self) + \
            "\n" + \
            "".join([
                c._dump(_indent + 1)
                for c in self.children
            ])

    def _child(self, childnr:int)->Any:
        """  Return the child object at a specific position"""
        if self._child_count() >0:
            if childnr >= 0 and childnr<self._child_count():
                return self.children[childnr]

        return False

    def _child_count(self)->int:
        """ Return the number of children """
        return len(self.children)

    def _insert_child(self, position:int, node)->bool:
        self.children.insert(position, node)

        session=inspect(self).session
        session.commit()
        return True

    def _row(self):
        if self.parent_node is not None:
            return self.parent_node.children.index(self)

    def _remove_child(self, position:int)->bool:
        """ Remove a child item at a particular position

        :param position: The position within the list of children

        """
        if 0 <= position < self._child_count():
            child=self._child(position)

            session=inspect(child).session

            # Since we are using SQLAlchemy, we can't simply delete objects. If an object is part of a change that was not
            # committet yet, we need to use 'Session.expunge()' instead of 'Session.delete()'.
            if child in session.new:
                session.expunge(child)
            else:
                session.delete(child)
            session.commit()

        return True