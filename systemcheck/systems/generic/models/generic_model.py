# define authorship information
__authors__     = ['Lars Fasel']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2017'
__license__     = 'GNU AGPLv3'

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
    relationship, Integer, ForeignKey, RichString, BaseMixin
from systemcheck.models.meta.orm_choices import choices

@choices
class SystemCategoryChoices:
    class Meta:
        DEV = [0, 'Development']
        QAS = [1, 'Quality Assurance']
        SBX = [2, 'Sandbox']
        PRD = [3, 'Production']


@generic_repr
class GenericSystemTreeNode(Base, QtModelMixin, BaseMixin):
    """ A generic node that is the foundation of the tree stored in a database table"""

    __tablename__ = 'systems'

    __table_args__ = {'extend_existing' : True}


    id = Column(Integer, primary_key=True, qt_label='Primary Key')
    parent_id = Column(Integer, ForeignKey('systems.id'), qt_label='Parent Key')
    type = Column(String(50), qt_show=False, qt_label='Type')
    name = Column(String(50), qt_show=True, qt_label='Name')

    description = Column(RichString,
                         nullable=True,
                         qt_label='Description',
                         qt_description='Brief description',
                         )

    children=relationship('GenericSystemTreeNode',
                          cascade="all, delete-orphan",
                          backref=backref("parent_node", remote_side=id),
                          )

    __mapper_args__ = {
        'polymorphic_identity':'GenericSystemTreeNode',
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
        """ Provide the Logon Information to the system


        Reimplement this method for all relevant system nodes
        """

        return None

class GenericSystem(GenericSystemTreeNode):

    category = Column(Integer, choices=SystemCategoryChoices.CHOICES, default=SystemCategoryChoices.DEV,
                      qt_label='System Category', qt_description='System Category')

    __mapper_args__ = {
        'polymorphic_identity':'GenericSystem',
    }

    __table_args__ = {'extend_existing' : True}