from PyQt5 import QtWidgets, QtCore, QtGui
from systemcheck.gui import utils
from systemcheck.gui.widgets.rich_text_editor import RichTextEditor
import platform
import logging

class RichTextDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)


    def createEditor(self, parent, option, index, *args, **kwargs):
        self.logger.debug('Creating RichText Editor')
        self.logger.debug('Size Options:  X=%i, Y=%i, Height=%i, Width=%i', option.rect.x(),
                          option.rect.y(),option.rect.height(), option.rect.width())

        editor = RichTextEditor(parent=parent, fixedHeight=200)
        editor.setFixedHeight(300)


        return editor

#    def eventFilter(self, editor:RichTextEditor, event:QtCore.QEvent):
#        if event.type() == QtCore.QEvent.KeyRelease:
#            self.sizeChanged(editor)


    def setEditorData(self, editor, index, *args, **kwargs):
        value = index.model().data(index, QtCore.Qt.DisplayRole)
        editor.setHtml(value)

    def sizeChanged(self, editor, index, option):
        self.logger.debug('looking for children')
        if len(self.children())==0:
            self.logger.debug('No children')
        else:
            self.logger.debug('Hum. Children: %i', len(self.children()))
        size=self.sizeHint(option, index)


#        self.updateEditorGeometry(editor, option, index)


    def setModelData(self, editor, model, index, *args, **kwargs):
        value = editor.toHtml()
        model.setData(index, value)


    def paint(self, painter, option, index):
        model=index.model()
        text = model.data(index, QtCore.Qt.DisplayRole)
        doc = QtGui.QTextDocument()
        doc.setTextWidth(option.rect.width())
        doc.setHtml(text)
        option.rect.setHeight(doc.size().height())
        painter.save()
        painter.translate(option.rect.topLeft())
        doc.drawContents(painter, QtCore.QRectF(0, 0, option.rect.width(), option.rect.height()))
        painter.restore()


    def sizeHint(self, option, index):

        model = index.model()

        print('in sizeHint:')
        print('X: {}'.format(option.rect.x()))
        print('Y: {}'.format(option.rect.y()))
        print('Width: {}'.format(option.rect.width()))
        print('Height: {}'.format(option.rect.height()))

        print('====')


        record = model.data(index, role=QtCore.Qt.DisplayRole)
        doc = QtGui.QTextDocument()
        doc.setHtml(record)
        doc.setTextWidth(option.rect.width())
        return QtCore.QSize(option.rect.width(), 300)


#        return QtCore.QSize(option.rect.width(), option.rect.height())


