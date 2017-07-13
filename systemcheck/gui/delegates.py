from PyQt5 import QtWidgets, QtCore, QtGui
from systemcheck.gui import utils

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
        self.setLayout(layout)
        self.show()

    def checkState(self):
        return self.cbox.checkState()

    def setCheckState(self, state):
        if state is True:
            self.cbox.setCheckState(QtCore.Qt.Checked)
        else:
            self.cbox.setCheckState(QtCore.Qt.Unchecked)


class ComboDelegate(QtWidgets.QItemDelegate):


    def __init__(self, choices:list, parent=None):
        QtWidgets.QItemDelegate.__init__(self, parent)
        self.choices=choices


    def createEditor(self, parent, option, index):
        combo = QtWidgets.QComboBox(parent)

        for x in self.choices:
            combo.addItem(x[1], x[0])
        combo.currentIndexChanged.connect(self.currentIndexChanged)
        return combo

    def setEditorData(self, editor, index):
        editor.blockSignals(True)
        editor.setCurrentIndex(int(index.model().data(index)))
        editor.blockSignals(False)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentIndex())

    @QtCore.pyqtSlot()
    def currentIndexChanged(self):
        self.commitData.emit(self.sender())


class GenericDelegate(QtWidgets.QItemDelegate):
    """ A Generic Delegate Class """

    def __init__(self):
        super().__init__()
        self.delegates={}

    def insertColumnDelegate(self, column, delegate):
        delegate.setParent(self, self)
        self.delegates[column]=delegate

    def removeColumnDelegate(self, column):
        if column in self.delegates.keys():
            del self.delegates[column]

    def paint(self, painter, option, index):
        delegate = self.delegates.get(index.column())
        if delegate is not None:
            delegate.paint(painter, option, index)
        else:
            QtWidgets.QItemDelegate.paint(self, painter, option, index)

    def createEditor(self, parent, option, index):
        delegate = self.delegates.get(index.column())
        if delegate is not None:
            return delegate.createEditor(parent, option, index)
        else:
            return QtWidgets.QItemDelegate.createEditor(self, parent, option, index)

    def setEditorData(self, editor, index):
        delegate=self.delegates.get(index.column())
        if delegate is not None:
            delegate.setEditorData(self, editor, index)
        else:
            QtWidgets.QItemDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        delegate=self.delegates.get(index.column())
        if delegate is not None:
            delegate.setModelData(self, editor, model, index)
        else:
            QtWidgets.QItemDelegate.setModelData(self, editor, model, index)


class IntegerColumnDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, minimum=0, maximum=100, parent=None):
        super(IntegerColumnDelegate, self).__init__(parent)
        self.minimum = minimum
        self.maximum = maximum


    def createEditor(self, parent, option, index):
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


    def createEditor(self, parent, option, index):
        lineedit = utils.lineEdit(parent)
        return lineedit


    def setEditorData(self, editor, index):
        value = index.model().data(index, QtCore.Qt.DisplayRole)
        editor.setText(value)


    def setModelData(self, editor, model, index):
        model.setData(index, editor.text())


class ComboBoxDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, parent=None):
        super().__init__(parent)


    def createEditor(self, parent, option, index):
        widget = QtWidgets.QComboBox(parent)

        for row in option:
            widget.addItem(str(row[1]), row[0])

        return widget


    def setEditorData(self, editor, index):
        choice = index.model().data(index, QtCore.Qt.DisplayRole)
        editor.setCurrentIndex(editor.findData(choice.code))


    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentData(QtCore.Qt.DisplayRole))


class CenteredCheckBoxDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, parent=None):
        super().__init__(parent)


    def createEditor(self, parent, option, index):
        editor=CenteredCheckbox()
        return editor


    def setEditorData(self, editor, index):
        status = index.model().data(index, QtCore.Qt.DisplayRole)
        editor.setCheckState(status)


    def setModelData(self, editor, model, index):
        model.setData(index, editor.checkState())


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