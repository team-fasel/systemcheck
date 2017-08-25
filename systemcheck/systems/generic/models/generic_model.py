# define authorship information
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
from systemcheck.models.meta import Base, UniqueConstraint, \
    Column, String, generic_repr, validates, backref, QtModelMixin, \
    relationship, Integer, ForeignKey, RichString

@generic_repr
class GenericSystemTreeNode(Base, QtModelMixin):
    """ A generic node that is the foundation of the tree stored in a database table"""
    __tablename__ = 'systems'

    __table_args__ = (
        UniqueConstraint("type", "name"),
        {'extend_existing' : True}
    )


    id = Column(Integer, primary_key=True, qt_label='Primary Key', qt_show=False)
    parent_id = Column(Integer, ForeignKey('systems.id'), qt_label='Parent Key', qt_show=False)
    type = Column(String(50), qt_show=False, qt_label='Type')
    name = Column(String(50), qt_show=True, qt_label='Name')

    description = Column(RichString,
                         nullable=True,
                         qt_label='Description',
                         qt_description='Brief description',
                         qt_show=False,
                         )

    children=relationship('GenericSystemTreeNode',
                          cascade="all, delete-orphan",
                          backref=backref("parent_node", remote_side=id),
                          )

    __mapper_args__ = {
        'polymorphic_identity':'FOLDER',
        'polymorphic_on':type,
    }

    __qtmap__ = [name, description]

    def _dump(self, _indent=0)->str:
        """ Recursively return the structure of the node and all its children as text """
        return "   " * _indent + repr(self) + \
            "\n" + \
            "".join([
                c._dump(_indent + 1)
                for c in self.children
            ])


    def _system_node(self):
            return None

    def logon_info(self):
        return None