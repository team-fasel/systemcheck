
from PyQt5 import QtWidgets, QtCore, QtGui
import traceback
from systemcheck import gui


import functools


class ComboBoxModel(QtCore.QAbstractTableModel):
    def __init__(self, choices:list, header:list=None, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.__choices = choices
        if header is None:
            self.__header=[]
        else:
            self.__header = header


    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.__choices)

    def columnCount(self, parent=None, *args, **kwargs):
        if self.rowCount() > 0:
            return len(self.__choices[0])
        else:
            return 0

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            column = index.column()
            value = self.__choices[row][column]
            return value

    def headerData(self, col, orientation, role):
        return None



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
        widget.setStyleSheet(stylesheet)
    return widget

def richTextEditor(parent, *args, editable:bool=True, transparentBackground:bool=True, borders=False, **kwargs):
    """ Generate a pre-customized RichTextEditor Widget

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

    widget=gui.widgets.RichTextEditor(parent, **kwargs)

    if stylesheetlist:
        stylesheet = "QTextEdit { " + ' '.join(stylesheetlist) + '}'
        print(stylesheet)
        widget.setStyleSheet(stylesheet)
    return widget


def checkBox(*args, info:dict=None, **kwargs):
    flat=kwargs.get('flat')
    widget = QtWidgets.QCheckBox()
    return widget

def comboBox2(*args, choices=None, **kwargs):

    #widget=FlatComboBox()
    widget=QtWidgets.QComboBox()
#    widget.setEditable(True)
#    widget.lineEdit().setReadOnly(True)

    if choices:

        for value, text in choices:
            widget.addItem(text, value)

#        view=QtWidgets.QTreeView()
#        view.header().hide()
#        view.setRootIsDecorated(False)
#        widget=QtWidgets.QComboBox()
#        widget.setView(view)
#        widget.setModel(model)
#        widget.setModelColumn(1)


    return widget

class comboBox3(QtWidgets.QComboBox):

    activated=QtCore.pyqtSignal('PyQt_PyObject')

    def __init__(self):
        super().__init__()
        self.activated.connect(self.triggerVariantActivated)

    def setChoices(self, choices):
        for value, text in choices:
            self.addItem(str(value), text)

    def triggerVariantActivated(self, index):

        self.activated.emit(self.itemData(index))

    def paintEvent(self, e):
        painter=QtWidgets.QStylePainter(self)
        option=QtWidgets.QStyleOptionComboBox()
        option.text=self.currentData(QtCore.Qt.DisplayRole)
        self.initStyleOption(option)
        painter.drawComplexControl(QtWidgets.QStyle.CC_ComboBox, option)
        painter.drawControl(QtWidgets.QStyle.CE_ComboBoxLabel, option)


class comboBox(QtWidgets.QComboBox):

    activated=QtCore.pyqtSignal('PyQt_PyObject')

    def __init__(self, choices):
        super().__init__()

        local_view=QtWidgets.QTableView()
        self.setView(local_view)
        local_model=QtGui.QStandardItemModel()
        for value, text in choices:

            textItem=QtGui.QStandardItem(text)
            valueItem=QtGui.QStandardItem(str(value))
            local_model.appendRow([valueItem, textItem])

        self.setModel(local_model)
        local_view.resizeColumnsToContents()
        local_view.resizeRowsToContents()
        local_view.horizontalHeader().setVisible(False)



def message(text, icon:int = QtWidgets.QMessageBox.Information, title=None, informativeText=None, details=None,
            buttons=None, defaultButton=None, exc_info=False, parent=None, windowIcon:QtGui.QIcon=None):
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

    if windowIcon:
        mbox.setWindowIcon(windowIcon)

    if informativeText:
        mbox.setInformativeText(informativeText)

    if details:
        mbox.setDetailedText(details)

    if defaultButton is not None:
        mbox.setDefaultButton(defaultButton)

    return mbox.exec_()