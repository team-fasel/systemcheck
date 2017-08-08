from PyQt5 import QtWidgets, QtCore, QtGui
import systemcheck
#import systemcheck.models.meta
#from systemcheck.gui import utils
import sqlalchemy
import sqlalchemy_utils
from systemcheck.gui.delegates import PlainTextColumnDelegate, GenericDelegate, ComboBoxDelegate, CenteredCheckBoxDelegate, RichTextColumnDelegate


def generateQtDelegate(alchemyObject):
    """ Generates a QItemDelegate from a SQLAlchemy Object

    :param alchemyObject: The SQLAlchemy object for which the delegate should be generated"""

    delegate=GenericDelegate()

    visible_columns = alchemyObject._visible_columns()

    for qtcolumn, column in enumerate(visible_columns):
        alchemyColumnType=sqlalchemy_utils.functions.get_type(column)
        if isinstance(alchemyColumnType, systemcheck.models.meta.RichString):
            delegate.insertColumnDelegate(qtcolumn, RichTextColumnDelegate)
        elif isinstance(alchemyColumnType, systemcheck.models.meta.String):
            delegate.insertColumnDelegate(qtcolumn, PlainTextColumnDelegate)
        elif isinstance(alchemyColumnType, systemcheck.models.meta.ChoiceType):
            delegate.insertColumnDelegate(qtcolumn, ComboBoxDelegate)
        elif isinstance(alchemyColumnType, systemcheck.models.meta.Boolean):
            delegate.insertColumnDelegate(qtcolumn, CenteredCheckBoxDelegate)

    return delegate

def getQtWidgetForAlchemyType(column, *args, **kwargs):

    alchemyColumnType = sqlalchemy_utils.functions.get_type(column)
    if isinstance(alchemyColumnType, systemcheck.models.meta.RichString):

        editor = QtWidgets.QTextEdit()

        return QtWidgets.QTextEdit(*args, **kwargs)
    elif isinstance(alchemyColumnType, systemcheck.models.meta.String):
        return systemcheck.gui.utils.lineEdit(*args, **kwargs)
    elif isinstance(alchemyColumnType, systemcheck.models.meta.Boolean):
        return systemcheck.gui.utils.checkBox( *args, **kwargs)
    elif isinstance(alchemyColumnType, systemcheck.models.meta.ChoiceType):
        choices=column.info.get('choices')
        return systemcheck.gui.utils.comboBox(*args, choices=choices, **kwargs)
