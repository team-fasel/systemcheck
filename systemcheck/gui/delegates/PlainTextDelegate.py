from systemcheck.gui import utils
from PyQt5 import QtWidgets, QtCore



class PlainTextDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, parent=None):
        super().__init__(parent)


    def createEditor(self, parent, option, index, *args, **kwargs):
        lineedit = utils.lineEdit(parent=parent)
        return lineedit


    def setEditorData(self, editor, index, *args, **kwargs):
        value = index.model().data(index, QtCore.Qt.DisplayRole)
        editor.setText(value)


    def setModelData(self, editor, model, index):
        model.setData(index, editor.text())


