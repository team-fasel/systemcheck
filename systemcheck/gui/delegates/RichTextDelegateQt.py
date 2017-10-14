from PyQt5 import QtWidgets, QtCore, QtGui
from systemcheck.gui import utils
from systemcheck.gui.widgets.rich_text_editor import RichTextEditor

class RichTextDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, parent=None):
        super().__init__(parent)


    def createEditor(self, parent, option, index, *args, **kwargs):
        editor = RichTextEditor(parent=parent)
        return editor


    def setEditorData(self, editor, index, *args, **kwargs):
        value = index.model().data(index, QtCore.Qt.DisplayRole)
        editor.setHtml(value)


    def setModelData(self, editor, model, index, *args, **kwargs):
        value = editor.toHtml()
        model.setData(index, value)

    def paint(self, painter, option, index):
        return None


    def sizeHint(self, option, index):
        model = index.model()

        record = model.data(index, role=QtCore.Qt.DisplayRole)
        doc = QtGui.QTextDocument(self)
        doc.setHtml(record)
        doc.setTextWidth(option.rect.width())

        return QtCore.QSize(option.rect.width(), option.rect.height()*3)


