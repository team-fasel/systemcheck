
from PyQt5 import QtWidgets, QtCore
import traceback

def lineEdit(*args, editable:bool=True, transparentBackground:bool=True, borders=False, **kwargs):
    """ Generate a pre-customized QLineEdit Widget

    :param parent: Parent Index
    :param editable: Defines whether the line edit should be editable or not
    :param transparentBackground: Sets the style sheet to a transparent background if set to True
    :param borders: Defines wheter the widget should have any borders. Useful to disable if you display the widget in a
                    QTableWidgetItem.
    """

    stylesheetlist=[]
    if transparentBackground:
        stylesheetlist.append('background-color: rgba(0, 0, 0, 0);')

    if not borders:
        stylesheetlist.append('border: none;')

    widget=QtWidgets.QLineEdit(**kwargs)

    if stylesheetlist:
        stylesheet = "QLineEdit { " + ' '.join(stylesheetlist) + '}'
        print(stylesheet)
        widget.setStyleSheet(stylesheet)
    return widget

def checkBox(*args, info:dict=None, **kwargs):
    flat=kwargs.get('flat')
    widget = QtWidgets.QCheckBox()
    return widget

def comboBox(*args, choices=None, **kwargs):

    widget=QtWidgets.QComboBox()
    for choice in choices:
        widget.addItem(choice[1], choice[0])
    return widget

def message(text, icon:int = QtWidgets.QMessageBox.Information, title=None, informativeText=None, details=None,
            buttons=None, defaultButton=None, exc_info=False, parent=None):
    """Show a Message

    :param icon: Icon that should be displayed
    :param text: The main message text
    :param title: The message title
    :param informativeText: a text for the informative section of the message
    :param details: Text for the details message
    :param buttons: The normal Qt bitmask for the buttons to be displayed
    :param defaultButton: The default button
    :param exc_info: If set to True, a stack trace will be added to the details section
    :param parent: The parent index


    """

    if title is None:
        title = "Message"
    if not text:
        text = "Message text is missing?!?!?!"

    if buttons is None:
        buttons = QtWidgets.QMessageBox.Ok

    if details is None and exc_info:
        details = traceback.format_exc(limit=20)

    mbox = QtWidgets.QMessageBox(icon, title, text, buttons, parent)

    if informativeText:
        mbox.setInformativeText(informativeText)

    if details:
        mbox.setDetailedText(details)

    if defaultButton is not None:
        mbox.setDefaultButton(defaultButton)

    return mbox.exec_()