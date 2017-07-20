from PyQt5 import QtWidgets, QtCore, QtGui
from systemcheck.models import meta
from systemcheck.gui import utils
import sqlalchemy
import sqlalchemy_utils
from systemcheck.gui.delegates import PlainTextColumnDelegate, GenericDelegate, ComboBoxDelegate, CenteredCheckBoxDelegate


def generateQtDelegate(alchemyObject):
    """ Generates a QItemDelegate from a SQLAlchemy Object

    :param alchemyObject: The SQLAlchemy object for which the delegate should be generated"""

    delegate=GenericDelegate()

    visible_columns = alchemyObject._visible_columns()

    for qtcolumn, column in enumerate(visible_columns):
        alchemyColumnType=sqlalchemy_utils.functions.get_type(column)
        if isinstance(alchemyColumnType, meta.String):
            delegate.insertColumnDelegate(qtcolumn, PlainTextColumnDelegate)
        elif isinstance(alchemyColumnType, meta.ChoiceType):
            delegate.insertColumnDelegate(qtcolumn, ComboBoxDelegate)
        elif isinstance(alchemyColumnType, meta.Boolean):
            delegate.insertColumnDelegate(qtcolumn, CenteredCheckBoxDelegate)

    return delegate

def getQtWidgetForAlchemyType(column, *args, **kwargs):

    alchemyColumnType = sqlalchemy_utils.functions.get_type(column)

    if isinstance(alchemyColumnType, meta.String):
        return utils.lineEdit(*args, **kwargs)
    elif isinstance(alchemyColumnType, meta.Boolean):
        return utils.checkBox( *args, **kwargs)
    elif isinstance(alchemyColumnType, meta.ChoiceType):
        choices=column.info.get('choices')
        return utils.comboBox(*args, choices=choices, **kwargs)
