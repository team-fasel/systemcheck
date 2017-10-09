from PyQt5 import QtWidgets, QtCore, QtGui
from systemcheck.gui import utils
import inspect

class CenteredCheckbox(QtWidgets.QWidget):

    """ A Centered QCheckBox Widget

    When adding a QCheckBox to a widget (for example to a QTableWidgetItem), the check box is not aligned in the center
    This widget provides a centered alternative

    """

    def __init__(self, parent=None):
        super().__init__(parent)
        layout=QtWidgets.QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.cbox=QtWidgets.QCheckBox()
        layout.addWidget(self.cbox, alignment=QtCore.Qt.AlignCenter)
        self.setStyleSheet("background-color: white")
        self.setAutoFillBackground(True)
        self.setLayout(layout)
        self.show()

    def checkState(self):
        return self.cbox.checkState()

    def setCheckState(self, state):
        if state is True:
            self.cbox.setCheckState(QtCore.Qt.Checked)
        else:
            self.cbox.setCheckState(QtCore.Qt.Unchecked)


class ComboDelegate(QtWidgets.QStyledItemDelegate):


    def __init__(self, choices, parent=None):
        super().__init__(parent)
        self.choices=None


    def createEditor(self, parent, option, index, *args, alchemyObject=None, **kwargs):
        combo = QtWidgets.QComboBox(parent=parent)

        if alchemyObject is not None:
            for choice in alchemyObject.choices:
                combo.addItem(choice[1], choice[0])

#        combo.currentIndexChanged.connect(self.currentIndexChanged)
        return combo

    def setEditorData(self, editor, index, *args, **kwargs):
        editor.blockSignals(True)
        model=index.model()
#        rowcount=model.rowCount()
#        columncount=model.columnCount()
#        column=index.column()
        data=model.data(index, QtCore.Qt.DisplayRole)
        if data:
            newIdx=editor.findData(data)
            editor.setCurrentIndex(newIdx)
        editor.blockSignals(False)

    def setModelData(self, editor, model, index, *args, **kwargs):
        model.setData(index, editor.currentData())

    #@QtCore.pyqtSlot()
    def currentIndexChanged(self):
        self.commitData.emit(self.sender())


    def updateEditorGeometry(self, editor, option, Index):
        geom = QtWidgets.QStyle.alignedRect(option.direction, QtCore.Qt.AlignCenter, editor.sizeHint(), option.rect)
        editor.setGeometry(option.rect)


class GenericStyledItemDelegate(QtWidgets.QStyledItemDelegate):
    """ A Generic Delegate Class """

    def __init__(self, itemview=None):
        super().__init__()
        self.delegates={}
        self.__itemView = None

    @property
    def itemView(self):
        return self.__itemView

    @itemView.setter
    def itemView(self, view):
        self.__itemView=view

    def insertColumnDelegate(self, column, delegate, *args, **kwargs):
        if inspect.isclass(delegate):
            delegate.setParent(self, self)
        self.delegates[column]=delegate

    def removeColumnDelegate(self, column):
        if column in self.delegates.keys():
            del self.delegates[column]

    def paint(self, painter, option, index, *args, **kwargs):
        delegate = self.delegates.get(index.column())
        if delegate is not None:
            delegate.paint(self, painter, option, index)
        else:
            QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)

    def createEditor(self, parent, option, index, *args, **kwargs):
        delegate = self.delegates.get(index.column())
        if delegate is not None:
            return delegate.createEditor(self, parent, option, index, *args, **kwargs)
        else:
            return QtWidgets.QStyledItemDelegate.createEditor(self, parent, option, index)

    def setEditorData(self, editor, index):
        delegate=self.delegates.get(index.column())
        if delegate is not None:
            delegate.setEditorData(self, editor, index)
        else:
            QtWidgets.QStyledItemDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        delegate=self.delegates.get(index.column())
        if delegate is not None:
            delegate.setModelData(self, editor, model, index)
        else:
            QtWidgets.QStyledItemDelegate.setModelData(self, editor, model, index)

class GenericStyledItemDelegateColumToRow(QtWidgets.QStyledItemDelegate):
    """ A Generic Delegate Class  for a table view that shows the columns as rows """

    def __init__(self):
        super().__init__()
        self.delegates={}
        self.delegates_alchemyObjects={}
        self.__itemView = None

    @property
    def itemView(self):
        return self.__itemView

    @itemView.setter
    def itemView(self, view):
        self.__itemView = view

    def insertRowDelegate(self, row, delegate, *args, alchemyObject=None, **kwargs):
        """ Insert a new Delegate

        :param row: The row of the delegate
        :param delegate: The class of the delegate
        :param alchemyObject: The SQLAlchemy column object

        """
#        delegate.setParent(self, self)
        self.delegates[row]=delegate
#        self.delegates_alchemyObjects[row]=alchemyObject

    def removeRowDelegate(self, row):
        if row in self.delegates.keys():
            del self.delegates[row]

    def paint(self, painter, option, index, *args, **kwargs):
        column=index.column()
        row=index.row()
        if column==1:
            delegate = self.delegates.get(row)
            if delegate is not None:
                delegate.paint(painter, option, index)
#            else:
#                QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)
        else:
            QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)

    def createEditor(self, parent, option, index):
        column=index.column()
        row=index.row()
        delegate = self.delegates.get(row)
        if delegate is not None:
            alchemyObject=self.delegates_alchemyObjects.get(row)
            return delegate.createEditor(parent, option, index)
        else:
            return QtWidgets.QStyledItemDelegate.createEditor(self, parent, option, index)

    def setEditorData(self, editor, index):
        column=index.column()
        row=index.row()
        if column==1:
            delegate = self.delegates.get(row)
            if delegate is not None:
                delegate.setEditorData(editor, index)
            else:
                QtWidgets.QStyledItemDelegate.setEditorData(editor, index)
        else:
            QtWidgets.QStyledItemDelegate.setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        column=index.column()
        row=index.row()
        if column==1:
            delegate=self.delegates.get(row)
            if delegate is not None:
                delegate.setModelData(editor, model, index)
        QtWidgets.QStyledItemDelegate.setModelData(self, editor, model, index)

#    def updateEditorGeometry(self, editor, option, index):
#        column=index.column()
#        row=index.row()
#        if column==1:
#            delegate = self.delegates.get(row)
#            if delegate is not None:
#                delegate.updateEditorGeometry(self, editor, option, index)
#            else:
#                QtWidgets.QStyledItemDelegate.paint(self, editor, option, index)
#        else:
#            QtWidgets.QStyledItemDelegate.paint(self, editor, option, index)

    def editorEvent(self, event, model, option, index):
        column=index.column()
        row=index.row()
        delegate = self.delegates.get(row)
        if delegate is not None:
            delegate.editorEvent(event, model, option, index)
        else:
            QtWidgets.QStyledItemDelegate.editorEvent(self, event, model, option, index)


class IntegerColumnDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, minimum=0, maximum=100, parent=None):
        super(IntegerColumnDelegate, self).__init__(parent)
        self.minimum = minimum
        self.maximum = maximum

    def createEditor(self, parent, option, index, *args, **kwargs):
        spinbox = QtWidgets.QSpinBox(parent)
        spinbox.setRange(self.minimum, self.maximum)
        spinbox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        return spinbox

    def setEditorData(self, editor, index):
        value = int(index.model().data(index, QtCore.Qt.DisplayRole))
        editor.setValue(value)

    def setModelData(self, editor, model, index):
        editor.interpretText()
        model.setData(index, editor.value())


class PlainTextColumnDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, parent=None):
        super().__init__(parent)


    def createEditor(self, parent, option, index, *args, **kwargs):
        lineedit = utils.lineEdit(parent)
        return lineedit


    def setEditorData(self, editor, index, *args, **kwargs):
        value = index.model().data(index, QtCore.Qt.DisplayRole)
        editor.setText(value)


    def setModelData(self, editor, model, index):
        model.setData(index, editor.text())



class RichTextColumnDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, parent=None):
        super().__init__(parent)


    def createEditor(self, parent, option, index, *args, **kwargs):
        editor = utils.richTextEditor(parent)
        return editor


    def setEditorData(self, editor, index, *args, **kwargs):
        value = index.model().data(index, QtCore.Qt.DisplayRole)
        editor.setText(value)


    def setModelData(self, editor, model, index, *args, **kwargs):
        model.setData(index, editor.document())


class CenteredCheckBoxDelegate(QtWidgets.QStyledItemDelegate):
    """ Delegate for editing bool values via a checkbox with no label centered in its cell.
    Does not actually create a QCheckBox, but instead overrides the paint() method to draw the checkbox directly.
    Mouse events are handled by the editorEvent() method which updates the model's bool value.
    """
    def __init__(self, parent=None):
        super(CenteredCheckBoxDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index, *args, **kwargs):
        """ Important, otherwise an editor is created if the user clicks in this cell.
        """
        return None

    def paint(self, painter, option, index):
        """ Paint a checkbox without the label.
        """
        checked = bool(index.model().data(index, QtCore.Qt.DisplayRole))
        opts = QtWidgets.QStyleOptionButton()
        opts.state |= QtWidgets.QStyle.State_Active
        if index.flags() & QtCore.Qt.ItemIsEditable:
            opts.state |= QtWidgets.QStyle.State_Enabled
        else:
            opts.state |= QtWidgets.QStyle.State_ReadOnly
        if checked:
            opts.state |= QtWidgets.QStyle.State_On
        else:
            opts.state |= QtWidgets.QStyle.State_Off

        checkBoxRect = QtWidgets.QApplication.style().subElementRect(QtWidgets.QStyle.SE_CheckBoxIndicator, opts, None)
        # Center checkbox in option.rect.
        x = option.rect.x()
        y = option.rect.y()
        w = option.rect.width()
        h = option.rect.height()
        checkBoxTopLeftCorner = QtCore.QPoint(x + w / 2 - checkBoxRect.width() / 2, y + h / 2 - checkBoxRect.height() / 2)
        opts.rect = QtCore.QRect(checkBoxTopLeftCorner, checkBoxRect.size())
        QtWidgets.QApplication.style().drawControl(QtWidgets.QStyle.CE_CheckBox, opts, painter)

    def editorEvent(self, event, model, option, index):
        """ Change the data in the model and the state of the checkbox if the
        user presses the left mouse button and this cell is editable. Otherwise do nothing.
        """

        # Get size of a standard checkbox.
        opts = QtWidgets.QStyleOptionButton()
        checkBoxRect = QtWidgets.QApplication.style().subElementRect(QtWidgets.QStyle.SE_CheckBoxIndicator, opts, None)
        # Center checkbox in option.rect.
        x = option.rect.x()
        y = option.rect.y()
        w = option.rect.width()
        h = option.rect.height()
        checkBoxTopLeftCorner = QtCore.QPoint(x + w / 2 - checkBoxRect.width() / 2, y + h / 2 - checkBoxRect.height() / 2)
        checkopts = QtCore.QRect(checkBoxTopLeftCorner, checkBoxRect.size())


        if not (index.flags() & QtCore.Qt.ItemIsEditable):
            return False
        if event.button() == QtCore.Qt.LeftButton:
            if event.type() == QtCore.QEvent.MouseButtonRelease:
                if checkopts.contains(event.pos()):
                    self.setModelData(None, model, index)
                    return True
            elif event.type() == QtCore.QEvent.MouseButtonDblClick:
                if checkopts.contains(event.pos()):
                    return True
        return False

    def setModelData(self, editor, model, index):
        """ Toggle the boolean state in the model.
        """
        checked = not bool(index.model().data(index, QtCore.Qt.DisplayRole))
        model.setData(index, checked, QtCore.Qt.EditRole)

    def getCheckBoxRect(self, option):
        """ Get rect for checkbox centered in option.rect.
        """
        # Get size of a standard checkbox.
        opts = QtWidgets.QStyleOptionButton()
        checkBoxRect = QtWidgets.QApplication.style().subElementRect(QtWidgets.QStyle.SE_CheckBoxIndicator, opts, None)
        # Center checkbox in option.rect.
        x = option.rect.x()
        y = option.rect.y()
        w = option.rect.width()
        h = option.rect.height()
        checkBoxTopLeftCorner = QtCore.QPoint(x + w / 2 - checkBoxRect.width() / 2, y + h / 2 - checkBoxRect.height() / 2)
        return QtCore.QRect(checkBoxTopLeftCorner, checkBoxRect.size())

class CenteredCheckBoxDelegate2(QtWidgets.QStyledItemDelegate):

    def __init__(self, parent=None):
        super().__init__(parent)


    def createEditor(self, parent, option, index, *args, **kwargs):
        editor=QtWidgets.QCheckBox(parent)
        return editor


    def setEditorData(self, editor, index, *args, **kwargs):
        status = index.model().data(index, QtCore.Qt.CheckStateRole)
        editor.setCheckState(status)


    def setModelData(self, editor, model, index, *args, **kwargs):
        model.setData(index, editor.checkState())

    def paint(self, painter, option, index):
        status= index.model().data(index, QtCore.Qt.CheckStateRole)
        checkboxstyle=QtWidgets.QStyleOptionButton()
        checkbox_rect = QtWidgets.QApplication.style().subElementRect(QtWidgets.QStyle.SE_CheckBoxIndicator, checkboxstyle)
        checkboxstyle.rect=option.rect
        checkboxstyle.rect.setLeft(option.rect.x()+option.rect.width()/2 - checkbox_rect.width()/2)
        checkboxstyle.state=QtWidgets.QStyle.State_On|QtWidgets.QStyle.State_Enable
        QtWidgets.QApplication.style().drawControl(QtWidgets.QStyle.CE_CheckBox, checkboxstyle, painter)


if __name__ == "__main__":
    import logging
    import sys

    logging.basicConfig(level='DEBUG')
    logging.getLogger('yapsy').setLevel(logging.DEBUG)

    app = QtWidgets.QApplication(sys.argv)
    main = CenteredCheckbox()
    main.setCheckState(QtCore.Qt.Checked)
    main.show()

    sys.exit(app.exec_())