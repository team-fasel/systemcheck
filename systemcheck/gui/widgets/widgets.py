# -*- coding: utf-8 -*-

""" Generic UI Widgets


"""

# define authorship information
__authors__     = ['Lars Fasel']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2017'
__license__     = 'MIT'


from PyQt5 import QtWidgets, QtCore, QtGui

class FlatComboBox(QtWidgets.QComboBox):
    """ A Flat QComboBox

    The default QComboBox arrow button to open the selections, is raised, which looks weird if the rest is flat
    """
    def __init__(self):
        super().__init__()
        self._flat = True
        self._arrowAlignment = QtCore.Qt.AlignRight
        self.setAutoFillBackground(True)
        pallete = QtGui.QPalette()
        pallete.setColor(QtGui.QPalette.Background, QtCore.Qt.white)
        self.setPalette(pallete)

    def flat(self):
        return self._flat

    def setFlat(self, value):
        self._flat = value

    def paintEvent(self, event):

        if self.flat():
            painter = QtWidgets.QStylePainter(self)
            painter.setPen(self.palette().color(QtGui.QPalette.Text))
            opt = QtWidgets.QStyleOptionComboBox()
            # opt.initFrom(self)
            self.initStyleOption(opt)
            displayText = opt.currentText
            painter.drawItemText(self.rect(), QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, self.palette(), True,
                                 displayText)
            rcOld = opt.rect
            opt.rect = QtWidgets.QStyle.alignedRect(QtCore.Qt.LeftToRight, self.arrowAlignment(),
                                                    QtCore.QSize(16, rcOld.height()), rcOld)
            painter.drawPrimitive(QtWidgets.QCommonStyle.PE_IndicatorArrowDown, opt)
            opt.rec = rcOld
            painter.drawControl(QtWidgets.QStyle.CE_ComboBoxLabel, opt)

        else:
            super().paintEvent(event)

    def mousePressEvent(self, event):
        if (self.isEditable() and self.lineEdit().rect().contains(event.pos())):
            self.aboutToPullDown.emit()
        else:
            super().mousePressEvent(event)

    def arrowAlignment(self):
        return self._arrowAlignment

    def setArrowAlignment(self, alignment):
        self._arrowAlignment = alignment

class TreeView(QtWidgets.QTreeView):
    """ Customized Tree View
    """

    addNode = QtCore.pyqtSignal(dict)
    delNode = QtCore.pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self.setContentsMargins(0,0,0,0)
        self.setHeaderHidden(True)
        self.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.setSortingEnabled(True)


