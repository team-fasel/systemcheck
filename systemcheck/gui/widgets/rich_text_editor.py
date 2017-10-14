#!/usr/bin/env python3
# Copyright (c) 2008-10 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 2 of the License, or
# version 3 of the License, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public License for more details.

import platform
import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt
import html


class RichTextEditor(QtWidgets.QTextEdit):
    returnPressed = QtCore.pyqtSignal()

    (Bold, Italic, Underline, StrikeOut, Monospaced, Sans, Serif,
     NoSuperOrSubscript, Subscript, Superscript) = range(10)

    def __init__(self, parent=None):
        super(RichTextEditor, self).__init__(parent)

        self.monofamily = "courier"
        self.sansfamily = "helvetica"
        self.seriffamily = "times"
        self.setTabChangesFocus(True)
        self.setAutoFillBackground(True)
        self.setStyleSheet('QTextEdit { border:none;background: rgba(0,0,0,0%)}')
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        fm = QtGui.QFontMetrics(self.font())
        self.h = int(fm.height() * (1.4 if platform.system() == "Windows"
                                    else 1.2))
        self.setMinimumHeight(self.h*3)
        self.setToolTip("Press <b>Ctrl+M</b> for the text effects "
                        "menu and <b>Ctrl+K</b> for the color menu")

        self.heightMin = 0
        self.heightMax = 65000

        self.document().contentsChanged.connect(self.sizeChange)

    def toggleItalic(self):
        self.setFontItalic(not self.fontItalic())

    def toggleUnderline(self):
        self.setFontUnderline(not self.fontUnderline())

    def toggleBold(self):
        self.setFontWeight(QtGui.QFont.Normal
                           if self.fontWeight() > QtGui.QFont.Normal else QtGui.QFont.Bold)

    def sizeHint(self):
        return QtCore.QSize(self.document().idealWidth() + 5,
                            self.maximumHeight())

    def minimumSizeHint(self):
        fm = QtGui.QFontMetrics(self.font())
        return QtCore.QSize(fm.width("WWWW"), self.minimumHeight())

    def contextMenuEvent(self, event):
        self.textEffectMenu()

    def keyPressEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            handled = False
            if event.key() == Qt.Key_B:
                self.toggleBold()
                handled = True
            elif event.key() == Qt.Key_I:
                self.toggleItalic()
                handled = True
            elif event.key() == Qt.Key_K:
                self.colorMenu()
                handled = True
            elif event.key() == Qt.Key_M:
                self.textEffectMenu()
                handled = True
            elif event.key() == Qt.Key_U:
                self.toggleUnderline()
                handled = True
            if handled:
                event.accept()
                return
        else:
            QtWidgets.QTextEdit.keyPressEvent(self, event)

    def colorMenu(self):
        pixmap = QtGui.QPixmap(22, 22)
        menu = QtWidgets.QMenu("Colour")
        for text, color in (
                ("&Black", Qt.black),
                ("B&lue", Qt.blue),
                ("Dark Bl&ue", Qt.darkBlue),
                ("&Cyan", Qt.cyan),
                ("Dar&k Cyan", Qt.darkCyan),
                ("&Green", Qt.green),
                ("Dark Gr&een", Qt.darkGreen),
                ("M&agenta", Qt.magenta),
                ("Dark Mage&nta", Qt.darkMagenta),
                ("&Red", Qt.red),
                ("&Dark Red", Qt.darkRed)):
            color = QtGui.QColor(color)
            pixmap.fill(color)
            action = menu.addAction(QtGui.QIcon(pixmap), text, self.setColor)
            action.setData(color)
        self.ensureCursorVisible()
        menu.exec_(self.viewport().mapToGlobal(
            self.cursorRect().center()))

    def sizeChange(self):
        docHeight = self.document().size().height()
        if self.heightMin <= docHeight <= self.heightMax:
            self.setMinimumHeight(docHeight)

    def setColor(self):
        action = self.sender()
        if action is not None and isinstance(action, QtWidgets.QAction):
            color = QtGui.QColor(action.data())
            if color.isValid():
                self.setTextColor(color)

    def textEffectMenu(self):
        format = self.currentCharFormat()
        menu = QtWidgets.QMenu("Text Effect")
        for text, shortcut, data, checked in (
                ("&Bold", "Ctrl+B", RichTextEditor.Bold, self.fontWeight() > QtGui.QFont.Normal),
                ("&Italic", "Ctrl+I", RichTextEditor.Italic, self.fontItalic()),
                ("Strike &out", None, RichTextEditor.StrikeOut, format.fontStrikeOut()),
                ("&Underline", "Ctrl+U", RichTextEditor.Underline, self.fontUnderline()),
                ("&Monospaced", None, RichTextEditor.Monospaced, format.fontFamily() == self.monofamily),
                ("&Serifed", None, RichTextEditor.Serif, format.fontFamily() == self.seriffamily),
                ("S&ans Serif", None, RichTextEditor.Sans, format.fontFamily() == self.sansfamily),
                ("&No super or subscript", None, RichTextEditor.NoSuperOrSubscript, format.verticalAlignment() == QtGui.QTextCharFormat.AlignNormal),
                ("Su&perscript", None, RichTextEditor.Superscript, format.verticalAlignment() == QtGui.QTextCharFormat.AlignSuperScript),
                ("Subs&cript", None, RichTextEditor.Subscript, format.verticalAlignment() == QtGui.QTextCharFormat.AlignSubScript)):
            action = menu.addAction(text, self.setTextEffect)
            if shortcut is not None:
                action.setShortcut(QtGui.QKeySequence(shortcut))
            action.setData(data)
            action.setCheckable(True)
            action.setChecked(checked)
        self.ensureCursorVisible()
        menu.exec_(self.viewport().mapToGlobal(
            self.cursorRect().center()))

    def setTextEffect(self):
        action = self.sender()
        if action is not None and isinstance(action, QtWidgets.QAction):
            what = int(action.data())
            if what == RichTextEditor.Bold:
                self.toggleBold()
                return
            if what == RichTextEditor.Italic:
                self.toggleItalic()
                return
            if what == RichTextEditor.Underline:
                self.toggleUnderline()
                return
            format = self.currentCharFormat()
            if what == RichTextEditor.Monospaced:
                format.setFontFamily(self.monofamily)
            elif what == RichTextEditor.Serif:
                format.setFontFamily(self.seriffamily)
            elif what == RichTextEditor.Sans:
                format.setFontFamily(self.sansfamily)
            if what == RichTextEditor.StrikeOut:
                format.setFontStrikeOut(not format.fontStrikeOut())
            if what == RichTextEditor.NoSuperOrSubscript:
                format.setVerticalAlignment(
                    QtGui.QTextCharFormat.AlignNormal)
            elif what == RichTextEditor.Superscript:
                format.setVerticalAlignment(
                    QtGui.QTextCharFormat.AlignSuperScript)
            elif what == RichTextEditor.Subscript:
                format.setVerticalAlignment(
                    QtGui.QTextCharFormat.AlignSubScript)
            self.mergeCurrentCharFormat(format)

    def toSimpleHtml(self):
        html = ""
        black = QtGui.QColor(Qt.black)
        block = self.document().begin()
        while block.isValid():
            iterator = block.begin()
            while iterator != block.end():
                fragment = iterator.fragment()
                if fragment.isValid():
                    format = fragment.charFormat()
                    family = format.fontFamily()
                    color = format.foreground().color()
                    text = html.escape(fragment.text())
                    if (format.verticalAlignment() ==
                            QtGui.QTextCharFormat.AlignSubScript):
                        text = "<sub>{}</sub>".format(text)
                    elif (format.verticalAlignment() ==
                              QtGui.QTextCharFormat.AlignSuperScript):
                        text = "<sup>{}</sup>".format(text)
                    if format.fontUnderline():
                        text = "<u>{}</u>".format(text)
                    if format.fontItalic():
                        text = "<i>{}</i>".format(text)
                    if format.fontWeight() > QtGui.QFont.Normal:
                        text = "<b>{}</b>".format(text)
                    if format.fontStrikeOut():
                        text = "<s>{}</s>".format(text)
                    if color != black or family:
                        attribs = ""
                        if color != black:
                            attribs += ' color="{}"'.format(color.name())
                        if family:
                            attribs += ' face="{}"'.format(family)
                        text = "<font{}>{}</font>".format(attribs, text)
                    html += text
                iterator += 1
            block = block.next()
        return html


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    lineedit = RichTextEditor()
    lineedit.show()
    lineedit.setWindowTitle("RichTextEdit")
    app.exec_()
    print(lineedit.toHtml())
    print(lineedit.toPlainText())
    print(lineedit.toSimpleHtml())


