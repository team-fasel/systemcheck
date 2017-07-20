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
from sqlalchemy import inspect
from typing import Any, List, Union
from systemcheck.models.meta import Base, SurrogatePK, SurrogateUuidPK, UniqueConstraint, \
    Column, String, CHAR, generic_repr, validates, backref, QtModelMixin, \
    UniqueMixin, Session, DateTime, relationship, declared_attr, attribute_mapped_collection, \
    one_to_many, many_to_one, Boolean, Integer, ForeignKey, ChoiceType, UUIDType


from systemcheck.systems.ABAP.models.abap_model import AbapSystem, AbapTreeNode, AbapClient

