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
    sizeChanged = QtCore.pyqtSignal()
    returnPressed = QtCore.pyqtSignal()

    (Bold, Italic, Underline, StrikeOut, Monospaced, Sans, Serif,
     NoSuperOrSubscript, Subscript, Superscript) = range(10)

    def __init__(self, parent=None, fixedHeight=None):
        super(RichTextEditor, self).__init__(parent)

        self.monofamily = "courier"
        self.sansfamily = "helvetica"
        self.seriffamily = "times"
        self.setTabChangesFocus(True)
        self.setAutoFillBackground(True)
        self.setStyleSheet('QTextEdit { border:none;background: rgba(255,255,255,100%)}')
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        fm = QtGui.QFontMetrics(self.font())
        self.h = int(fm.height() * (1.4 if platform.system() == "Windows"
                                    else 1.2))
        self.setMinimumHeight(self.h)
        self.setToolTip("Press <b>Ctrl+M</b> for the text effects "
                        "menu, <b>Ctrl+K</b> for the color menu and <b>Ctrl+L</b> for the layout menu")

        self.heightMin = 0
        self.heightMax = 65000

        self._fixedHeight = fixedHeight
        if fixedHeight is None:
            self.document().contentsChanged.connect(self.sizeChange)
        else:
            self.setFixedHeight(self._fixedHeight)

        self.setupUi()


    def alignLeft(self):
        self.setAlignment(Qt.AlignLeft)

    def alignRight(self):
        self.setAlignment(Qt.AlignRight)

    def alignCenter(self):
        self.setAlignment(Qt.AlignCenter)

    def alignJustify(self):
        self.setAlignment(Qt.AlignJustify)

    def setupUi(self):

        self.cut_act = QtWidgets.QAction(QtGui.QIcon(":Cut"), "Cut to clipboard", self)
        self.cut_act.setStatusTip("Delete and copy text to clipboard")
        self.cut_act.setShortcut("Ctrl+X")
        self.cut_act.triggered.connect(self.cut)

        self.copy_act = QtWidgets.QAction(QtGui.QIcon(":Copy"), "Copy to clipboard", self)
        self.copy_act.setStatusTip("Copy text to clipboard")
        self.copy_act.setShortcut("Ctrl+C")
        self.copy_act.triggered.connect(self.copy)

        self.paste_act = QtWidgets.QAction(QtGui.QIcon(":Paste"), "Paste from clipboard", self)
        self.paste_act.setStatusTip("Paste text from clipboard")
        self.paste_act.setShortcut("Ctrl+V")
        self.paste_act.triggered.connect(self.paste)

        self.bullet_act = QtWidgets.QAction(QtGui.QIcon(":BulletedList"),"Insert bullet List",self)
        self.bullet_act.setStatusTip("Insert bullet list")
        self.bullet_act.setShortcut("Ctrl+Shift+B")
        self.bullet_act.triggered.connect(self.bulletedList)

        self.numbered_act = QtWidgets.QAction(QtGui.QIcon(":NumberedList"),"Insert numbered List",self)
        self.numbered_act.setStatusTip("Insert numbered list")
        self.numbered_act.setShortcut("Ctrl+Shift+L")
        self.numbered_act.triggered.connect(self.numberedList)

        self.indent_act = QtWidgets.QAction(QtGui.QIcon(":Indent"), "Indent Area", self)
        self.indent_act.setShortcut("Ctrl+Tab")
        self.indent_act.triggered.connect(self.indent)

        self.dedent_act = QtWidgets.QAction(QtGui.QIcon(":Outdent"), "Outdent Area", self)
        self.dedent_act.setShortcut("Shift+Tab")
        self.dedent_act.triggered.connect(self.dedent)

        self.alignLeft_act = QtWidgets.QAction(QtGui.QIcon(":AlignLeft"), "Align left", self)
        self.alignLeft_act.triggered.connect(self.alignLeft)

        self.alignCenter_act = QtWidgets.QAction(QtGui.QIcon(":AlignCenter"), "Align center", self)
        self.alignCenter_act.triggered.connect(self.alignCenter)

        self.alignRight_act = QtWidgets.QAction(QtGui.QIcon(":AlignRight"), "Align right", self)
        self.alignRight_act.triggered.connect(self.alignRight)

        self.alignJustify_act = QtWidgets.QAction(QtGui.QIcon(":AlignJustify"), "Align justify", self)
        self.alignJustify_act.triggered.connect(self.alignJustify)

        self.undo_act = QtWidgets.QAction(QtGui.QIcon(":Undo"), "Undo last action", self)
        self.undo_act.setStatusTip("Undo last action")
        self.undo_act.setShortcut("Ctrl+Z")
        self.undo_act.triggered.connect(self.undo)

        self.redo_act = QtWidgets.QAction(QtGui.QIcon(":Redo"), "Redo last undone action", self)
        self.undo_act.setStatusTip("Redo last undone action")
        self.undo_act.setShortcut("Ctrl+Y")
        self.undo_act.triggered.connect(self.redo)

    def toggleItalic(self):
        self.setFontItalic(not self.fontItalic())

    def toggleUnderline(self):
        self.setFontUnderline(not self.fontUnderline())

    def toggleBold(self):
        self.setFontWeight(QtGui.QFont.Normal
                           if self.fontWeight() > QtGui.QFont.Normal else QtGui.QFont.Bold)

    def sizeHint(self):

        return QtCore.QSize(self.document().idealWidth() + 5, self.height())

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
            elif event.key() == Qt.Key_L:
                self.textLayoutMenu()
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

    def bulletedList(self):
        """ Insert a Bullet List

        """
        cursor = self.textCursor()
        if cursor.hasSelection():
            return
        cursor.insertList(QtGui.QTextListFormat.ListDisc)

    def dedent(self):
        """ Dedent List """

        cursor = self.text_tedit.textCursor()
        if cursor.hasSelection():

            # Store the current line/block number
            temp = cursor.blockNumber()

            # Move to the selection's last line
            cursor.setPosition(cursor.anchor())

            # Calculate range of selection
            diff = cursor.blockNumber() - temp
            direction = QtGui.QTextCursor.Up if diff > 0 else QtGui.QTextCursor.Down

            # Iterate over lines
            for n in range(abs(diff) + 1):
                self.handleDedent(cursor)

                # Move up
                cursor.movePosition(direction)

        else:
            self.handleDedent(cursor)

    def handleDedent(self, cursor):
        """ Handle the Dedent
        :param cursor:
        :return:
        """
        cursor.movePosition(QtGui.QTextCursor.StartOfLine)

        # Grab the current line
        line = cursor.block().text()

        # If the line starts with a tab character, delete it
        if line.startswith("\t"):

            # Delete next character
            cursor.deleteChar()

        # Otherwise, delete all spaces until a non-space character is met
        else:
            for char in line[:8]:

                if char != " ":
                    break

                cursor.deleteChar()

    def indent(self):
        """ Indent Text

        """
        cursor = self.text_tedit.textCursor()

        if cursor.hasSelection():
            # Store the current line/block number
            temp = cursor.blockNumber()

            # Move to the selection's end
            cursor.setPosition(cursor.anchor())

            # Calculate range of selection
            diff = cursor.blockNumber() - temp

            direction = QtGui.QTextCursor.Up if diff > 0 else QtGui.QTextCursor.Down

            # Iterate over lines (diff absolute value)
            for n in range(abs(diff) + 1):
                # Move to start of each line
                cursor.movePosition(QtGui.QTextCursor.StartOfLine)

                # Insert tabbing
                cursor.insertText("\t")

                # And move back up
                cursor.movePosition(direction)

        # If there is no selection, just insert a tab
        else:
            cursor.insertText("\t")

    def numberedList(self):
        """ Insert a Numbered List

        """

        cursor = self.textCursor()
        if cursor.hasSelection():
            return

        cursor.insertList(QtGui.QTextListFormat.ListDecimal)

    def setColor(self):
        action = self.sender()
        if action is not None and isinstance(action, QtWidgets.QAction):
            color = QtGui.QColor(action.data())
            if color.isValid():
                self.setTextColor(color)

    def setTextEffect(self):
        """ Set Text Effect


        """
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

    def sizeChange(self):
        docHeight = self.document().size().height()
        if self.heightMin <= docHeight <= self.heightMax:
            self.setMinimumHeight(docHeight)

        self.sizeChanged.emit()

    def textLayoutMenu(self):
        menu=QtWidgets.QMenu('Text Layout')
        menu.addAction(self.bullet_act)
        menu.addAction(self.numbered_act)
        menu.addSeparator()
        menu.addAction(self.indent_act)
        menu.addAction(self.dedent_act)
        menu.addSeparator()
        menu.addAction(self.alignLeft_act)
        menu.addAction(self.alignCenter_act)
        menu.addAction(self.alignRight_act)
        menu.addAction(self.alignJustify_act)

        self.ensureCursorVisible()
        menu.exec_(self.viewport().mapToGlobal(
            self.cursorRect().center()))

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
    lineedit.setText("You should reimplement QAbstractItemDelegate::sizeHint method to return expected height when you create your editor. I don't think that it's necesary to emit QAbstractItemDelegate::sizeHintChanged signal after creating editor, but documentation doesn't say anything. If it doesn't work without it, you should emit sizeHintChanged after returning created editor widget to notify view of need to change row height.")
    lineedit.setWindowTitle("RichTextEdit")
    app.exec_()
    print(lineedit.toHtml())
    print(lineedit.toPlainText())
    print(lineedit.toSimpleHtml())


