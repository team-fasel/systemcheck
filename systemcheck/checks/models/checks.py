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
    Integer, ForeignKey, ChoiceType, UUIDType, relationship, RichString, qtRelationship

#from systemcheck.session import SESSION

from typing import Any
from sqlalchemy.inspection import inspect
from typing import Union, List
from pprint import pprint
import systemcheck

example_text="""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:20pt; font-weight:600;">Heading</span></p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:20pt; font-weight:600;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:14pt;">This is an example text</span></p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt;"><br /></p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt;"><br /></p></body></html>"""

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
class Check(QtModelMixin, Base):
    """ The Generic Data Model of a Check

    Similar to the generic tree for systems, this is a tree structure for checks.
    """

    __tablename__ = 'checks_metadata'

    __table_args__ = (
        UniqueConstraint("type", "name"),
        {'extend_existing' : True}
    )

    SYSTEM_TYPE_CHOICES=[
                        ('ABAP', 'ABAP System'),
                    ]

    FAILURE_CRITERIA = [
        ('FAIL_IF_ANY_FAILS', 'Rate Fail if any parameter set fails'),
        ('FAIL_IF_ALL_FAIL',  'Rate Fail if all sets fail'),
    ]


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
                         default=example_text
                         )

    __qtmap__ = [name, description]



    def _parameter_count(self):
        return len(self.params)


    __mapper_args__ = {
        'polymorphic_identity':'FOLDER',
        'polymorphic_on':type,
    }
