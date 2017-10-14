from PyQt5 import QtWidgets, QtCore, QtGui
import systemcheck
#import systemcheck.models.meta
#from systemcheck.gui import utils
import sqlalchemy
import sqlalchemy_utils
from systemcheck.gui.delegates import PlainTextDelegate, ComboBoxDelegateQt, \
    RichTextDelegate, IntegerDelegate, GenericStyledItemDelegateColumToRow, TextLineDelegate


from sqlalchemy.inspection import inspect
import logging
from pprint import pprint, pformat

logger=logging.getLogger(__name__)

def generateQtDelegate(alchemyObject, sectionName=None):
    """ Generates a QItemDelegate from a SQLAlchemy Object

    :param alchemyObject: The SQLAlchemy object for which the delegate should be generated"""

    delegate=GenericStyledItemDelegateColumToRow()
    visible_columns=[]
    if sectionName is None:
        visible_columns = alchemyObject._qt_columns()

    else:
        section=getattr(alchemyObject, sectionName)
        if len(section)>0:
            item=section[0]
            visible_columns=item.__qtmap__

    for qtcolumn, column in enumerate(visible_columns):

        alchemyColumnType = sqlalchemy_utils.functions.get_type(column)

        if column.choices:
#            ComboDelegate(choices=column.choices)
            choices = [(choice[1], choice[0]) for choice in column.choices]
            delegate.insertRowDelegate(qtcolumn, ComboBoxDelegateQt(choices=choices))
        else:
            if isinstance(alchemyColumnType, systemcheck.models.meta.RichString):
                delegate.insertRowDelegate(qtcolumn, RichTextDelegate())
            elif isinstance(alchemyColumnType, systemcheck.models.meta.LongString):
                delegate.insertRowDelegate(qtcolumn, PlainTextDelegate())
            elif isinstance(alchemyColumnType, systemcheck.models.meta.String):
                delegate.insertRowDelegate(qtcolumn, TextLineDelegate())
            elif isinstance(alchemyColumnType, systemcheck.models.meta.Integer):
                delegate.insertRowDelegate(qtcolumn, IntegerDelegate())
            else:
                delegate.insertRowDelegate(qtcolumn, PlainTextDelegate())
    return delegate


def getQtWidgetForAlchemyType(column, *args, **kwargs):
    widget=None

    if column.choices:

        logger.debug('Identified Options: %s', pformat(column.choices))
        widget = systemcheck.gui.utils.comboBox(*args, choices=column.choices, **kwargs)
    else:
        alchemyColumnType = sqlalchemy_utils.functions.get_type(column)
        if isinstance(alchemyColumnType, systemcheck.models.meta.RichString):
            widget = QtWidgets.QTextEdit(*args, **kwargs)
        elif isinstance(alchemyColumnType, systemcheck.models.meta.String):
            widget = systemcheck.gui.utils.lineEdit(*args, **kwargs)
        elif isinstance(alchemyColumnType, systemcheck.models.meta.Boolean):
            widget = systemcheck.gui.utils.checkBox( *args, **kwargs)
        elif isinstance(alchemyColumnType, systemcheck.models.meta.Integer):
            widget = systemcheck.gui.utils.lineEdit(*args, **kwargs)
        elif isinstance(alchemyColumnType, systemcheck.models.meta.ChoiceType):
            choices=column.info.get('choices')
            widget = systemcheck.gui.utils.comboBox(*args, choices=choices, **kwargs)
        else:
            print('unknown')

    return widget