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

import inspect
from typing import Any
from sqlalchemy import inspect
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
class Check(Base):
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
                         qt_description='Name of the check that describes it briefly',
                         qt_show=False,
                         default=example_text
                         )

    __qtmap__ = [name, description]


    def _column_count(self)->int:
        """ Return the number of columns """
        return 1

    def _colnr_is_valid(self, colnr:int)->bool:

        if colnr>=0 and colnr < 1:
            return True
        return False



    __mapper_args__ = {
        'polymorphic_identity':'FOLDER',
        'polymorphic_on':type,
    }


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
        self._commit()
        return True

    def _row(self):
        if self.parent_node is not None:
            return self.parent_node.children.index(self)

    def _visible_colnr_is_valid(self, colnr:int)->bool:
        """ Validate that the column number is ok fo a visible column"""

        if colnr >= 0 and colnr<len(self.__qtmap__):
            return True
        return False


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

    def _column_count(self) -> int:
        """ Return the number of columns """
        return len(self.__qtmap__)

    def _colnr_is_valid(self, colnr: int) -> bool:
        insp = inspect(self)
        col_count = len(insp.attrs._data)

        if colnr >= 0 and colnr < col_count:
            return True
        return False

    def _commit(self):
        session = systemcheck.session.SESSION
        session.commit()

    def _flush(self):
        session = inspect(self).session
        session.flush()

    def _info_by_colnr(self, colnr: int) -> Union[dict, bool]:
        """ Return the info metadata for any column"""
        if self._colnr_is_valid(colnr):
            value = list(self.__table__.columns)[colnr].info
            return value
        else:
            return False

    def _icon(self):
        """ Returns the Icon of the node type """

        return False

    def _info_by_visible_colnr(self, colnr: int) -> Union[dict, bool]:
        """ Return the info metadata for a visible column"""
        if self._visible_colnr_is_valid(colnr):
            visible_columns = self._visible_columns()
            value = visible_columns[colnr].info
            return value
        else:
            return False

    def _set_value_by_colnr(self, colnr: int, value: object):
        """ Get the Value of a Column by its Number

        QtModels refer to the underlying data by rows and columns. Somewhere a mapping has to occur that does this
        automatically.

        :param colnr: The Qt Column Number
        :type int:


        """

        # TODO: The implementation here is quite ugly. Need to find a better way to do this, but for now it's acceptable

        if self._colnr_is_valid(colnr):
            self.__qtmap__[colnr] = value
            self._flush()
            return True
        else:
            return False

    def _set_value_by_visible_colnr(self, colnr: int, value: object):
        """ Set the Value of a Column by its its visible Number

        QtModels refer to the underlying data by rows and columns. Somewhere a mapping has to occur that does this
        automatically.

        :param colnr: The Qt Column Number
        :type int:
        :param value: The value to be set in the column


        """

        # TODO: The implementation here is quite ugly. Need to find a better way to do this, but for now it's acceptable

        if self._visible_colnr_is_valid(colnr):
            column = self.__qtmap__[colnr]
            setattr(self, column.name, value)
            self._commit()
            return True
        else:
            return False

    def _visible_headers(self):

        return [colData.info.get('qt_label')
                for colData in self.__table__.columns
                if colData.info.get('qt_show')]

    def _value_by_colnr(self, colnr: int) -> object:
        """ Get the Value of a Column by its Number

        QtModels refer to the underlying data by rows and columns. Somewhere a mapping has to occur that does this
        automatically.

        :param colnr: The Qt Column Number
        :type int:


        """

        # TODO: The implementation here is quite ugly. Need to find a better way to do this, but for now it's acceptable

        if self._colnr_is_valid(colnr):

            value = self.__qtmap__[colnr]
            return value
        else:
            return None

    def _value_by_visible_colnr(self, colnr: int) -> object:
        """ Get the Value of a Column by its its visible Number

        QtModels refer to the underlying data by rows and columns. Somewhere a mapping has to occur that does this
        automatically.

        :param colnr: The Qt Column Number
        :type int:


        """

        # TODO: The implementation here is quite ugly. Need to find a better way to do this, but for now it's acceptable

        if self._visible_colnr_is_valid(colnr):
#            visible_columns = self._visible_columns()
            try:
                column = self.__qtmap__[colnr]
                value=getattr(self, column.name)
                return value
            except Exception as err:
                pprint(err)
        else:
            return False

    def _visible_columns(self) -> List[Any]:
        """ Return a list of columns that have the info medatadata variable qt_show set to True"""
        return self.__qtmap__

    def _visible_column_count(self) -> int:
        """Returns the number of visible Columns


        This is required due to the issue that you can't hide the first column of the QTreeView. If you hide the first column,
        all you see are entries immediately under the root node. The first column however is usually a primary key or something
        else that is not relevant for processing.

        The primary key is also determined automatically when inserting a new record and does not need to be maintained
        manually. Due to this, the handling of visible and invisible columns needs to get added to the tree handling.

        Here, we only return the visible column count.
        """
#        visible_columns = self._visible_columns()

        return len(self.__qtmap__)

    def _parameter_count(self):
        pprint(self.params)
        return len(self.params)