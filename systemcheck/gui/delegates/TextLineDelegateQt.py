""" A simple Line Editor Delegate


Will get extended with validators in the future
"""


from systemcheck import gui
from PyQt5 import QtWidgets, QtCore, QtGui

class TextLineDelegate(QtWidgets.QStyledItemDelegate):

#    textChanged = QtCore.pyqtSignal(str)
#    returnPressed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__()

    def createEditor(self, parent, option, index, *args, **kwargs):
        editor = QtWidgets.QLineEdit(parent=parent)
        value = index.model().data(index, QtCore.Qt.DisplayRole)
        editor.setText(value)
        styleSheet="background-color: white; border-width: 0px; border-color: transparent"
        editor.setStyleSheet(styleSheet)
        editor.setAutoFillBackground(True)
        editor.setCursorPosition(0)
#        editor.textChanged.connect(self.textChanged)
#        editor.returnPressed.connect(self.returnPressed)
        return editor

    def setEditorData(self, editor, index, *args, **kwargs):
        value = index.model().data(index, QtCore.Qt.DisplayRole)
        if value is None:
            value=''

        editor.setText(value)

    def setModelData(self, editor, model, index, *args, **kwargs):
        value = editor.text()
        model.setData(index, value)
        return True

#    def paint(self, painter, option, index):
#        return None


#    def event(self, event):
#        return QtWidgets.QStyledItemDelegate.editorEvent(self, event)
