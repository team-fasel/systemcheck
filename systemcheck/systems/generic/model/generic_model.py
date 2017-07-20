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


from pprint import pprint, pformat
import re

import sqlalchemy_utils

import enum
from sqlalchemy import inspect, Integer, ForeignKey, String, Boolean
from typing import Any, List, Union
from systemcheck.models.meta import Base, SurrogatePK, SurrogateUuidPK, UniqueConstraint, \
    Column, String, CHAR, generic_repr, validates, backref, QtModelMixin, \
    UniqueMixin, Session, DateTime, relationship, declared_attr, attribute_mapped_collection, \
    one_to_many, many_to_one, Boolean, Integer, ForeignKey, ChoiceType, UUIDType


@generic_repr
class GenericTreeNode(Base, QtModelMixin):
    """ A generic node that is the foundation of the tree stored in a database table"""
    __tablename__ = 'generic_tree'

    id = Column(Integer, primary_key=True, qt_label='Primary Key', qt_show=False)
    parent_id = Column(Integer, ForeignKey('generic_tree.id'), qt_label='Parent Key', qt_show=False)
    type = Column(String(50), qt_show=False, qt_label='Type')
    name = Column(String(50), qt_show=True, qt_label='Name')
    children=relationship('GenericTreeNode',
                          cascade="all, delete-orphan",
                          backref=backref("parent_node", remote_side=id),
                          )


    def _dump(self, _indent=0)->str:
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

    def _system_node(self):
            return None

