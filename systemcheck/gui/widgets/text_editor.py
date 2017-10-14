# -*- coding: utf-8 -*-

import sys
from systemcheck.resources import icon_rc
# PYQT5 PyQt4’s QtGui module has been split into PyQt5’s QtGui, QtPrintSupport and QtWidgets modules

from PyQt5 import QtWidgets
# PYQT5 QMainWindow, QApplication, QAction, QFontComboBox, QSpinBox, QTextEdit, QMessageBox
# PYQT5 QFileDialog, QColorDialog, QDialog

from PyQt5 import QtPrintSupport
# PYQT5 QPrintPreviewDialog, QPrintDialog

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt


class TextEditor(QtWidgets.QMainWindow):

    editingFinished = QtCore.pyqtSignal()

    def __init__(self,
                 parent,
                 fileactions:bool=False,
                 showFormatBar:bool=False,
                 showToolBar:bool=False,
                 showStatusBar:bool=False,
                 showMenuBar:bool=False):
        """ Editor adapted from https://github.com/goldsborough/Writer-Tutorial/blob/master/PyQt5/Part-2/part-2.py

        Since the text data comes from the database, file actions are not required. The only file action that remains
        when the widget is called using with fileactions=True is the open action.

        :param fileactions: disables or enables file interface actions

        """

        #TODO: Add to credits

        super().__init__()
        self.setParent(parent)

        self.filename = ""
        self.fileactions = fileactions
        self.initUI()

        self.toolbar.setVisible(showToolBar)
        self.menuBar().setVisible(showMenuBar)
        self.formatbar.setVisible(showFormatBar)
        self.statusBar().setVisible(showStatusBar)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_textEditContextMenu)

    def _addCustomItemMenu(self, menu):
        menu.addSeparator()
        menu.addAction(self.toggleToolbar)


    def event(self, event):
        if event.type() == QtCore.QEvent.FocusOut:
            self.editingFinished.emit()
            return True

        return QtWidgets.QTextEdit.event(self, event)

    def on_textEditContextMenu(self, point):


        self._context_menu = self.text_tedit.createStandardContextMenu()
        self._context_menu.addSeparator()
        self._context_menu.addAction(self.toggleToolbar_act)
        self._context_menu.addAction(self.toggleFormatbar_act)

        self._context_menu.exec_(self.mapToGlobal(point))


    def alignLeft(self):
        self.text_tedit.setAlignment(Qt.AlignLeft)

    def alignRight(self):
        self.text_tedit.setAlignment(Qt.AlignRight)

    def alignCenter(self):
        self.text_tedit.setAlignment(Qt.AlignCenter)

    def alignJustify(self):
        self.text_tedit.setAlignment(Qt.AlignJustify)

    def bold(self):

        if self.text_tedit.fontWeight() == QtGui.QFont.Bold:

            self.text_tedit.setFontWeight(QtGui.QFont.Normal)

        else:

            self.text_tedit.setFontWeight(QtGui.QFont.Bold)

    def bulletList(self):

        cursor = self.text_tedit.textCursor()

        # Insert bulleted list
        cursor.insertList(QtGui.QTextListFormat.ListDisc)

    def cursorPosition(self):

        cursor = self.text_tedit.textCursor()

        # Mortals like 1-indexed things
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber()

        self.statusbar.showMessage("Line: {} | Column: {}".format(line, col))

    def dedent(self):

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

    def fontColorChanged(self):

        # Get a color from the text dialog
        color = QtWidgets.QColorDialog.getColor()

        # Set it as the new text color
        self.text_tedit.setTextColor(color)

    def handleDedent(self, cursor):

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

    def highlight(self):

        color = QtWidgets.QColorDialog.getColor()

        self.text_tedit.setTextBackgroundColor(color)

    def indent(self):

        # Grab the cursor
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

    def initFormatbar(self):

        fontBox = QtWidgets.QFontComboBox(self)
        fontBox.currentFontChanged.connect(lambda font: self.text_tedit.setCurrentFont(font))

        fontSize = QtWidgets.QSpinBox(self)

        # Will display " pt" after each value
        fontSize.setSuffix(" pt")

        fontSize.valueChanged.connect(lambda size: self.text_tedit.setFontPointSize(size))

        fontSize.setValue(14)

        fontColor = QtWidgets.QAction(QtGui.QIcon(":TextColor"), "Change text color", self)
        fontColor.triggered.connect(self.fontColorChanged)

        backColor = QtWidgets.QAction(QtGui.QIcon(":MarkerPen"), "Change background color", self)
        backColor.triggered.connect(self.highlight)

        boldAction = QtWidgets.QAction(QtGui.QIcon(":Bold"), "Bold", self)
        boldAction.triggered.connect(self.bold)

        italicAction = QtWidgets.QAction(QtGui.QIcon(":Italic"), "Italic", self)
        italicAction.triggered.connect(self.italic)

        underlAction = QtWidgets.QAction(QtGui.QIcon(":Underline"), "Underline", self)
        underlAction.triggered.connect(self.underline)

        strikeAction = QtWidgets.QAction(QtGui.QIcon(":Strikethrough"), "Strike-out", self)
        strikeAction.triggered.connect(self.strike)

        superAction = QtWidgets.QAction(QtGui.QIcon(":Superscript"), "Superscript", self)
        superAction.triggered.connect(self.superScript)

        subAction = QtWidgets.QAction(QtGui.QIcon(":Subscript"), "Subscript", self)
        subAction.triggered.connect(self.subScript)

        alignLeft = QtWidgets.QAction(QtGui.QIcon(":AlignLeft"), "Align left", self)
        alignLeft.triggered.connect(self.alignLeft)

        alignCenter = QtWidgets.QAction(QtGui.QIcon(":AlignCenter"), "Align center", self)
        alignCenter.triggered.connect(self.alignCenter)

        alignRight = QtWidgets.QAction(QtGui.QIcon(":AlignRight"), "Align right", self)
        alignRight.triggered.connect(self.alignRight)

        alignJustify = QtWidgets.QAction(QtGui.QIcon(":AlignJustify"), "Align justify", self)
        alignJustify.triggered.connect(self.alignJustify)

        indentAction = QtWidgets.QAction(QtGui.QIcon(":Indent"), "Indent Area", self)
        indentAction.setShortcut("Ctrl+Tab")
        indentAction.triggered.connect(self.indent)

        dedentAction = QtWidgets.QAction(QtGui.QIcon(":Outdent"), "Outdent Area", self)
        dedentAction.setShortcut("Shift+Tab")
        dedentAction.triggered.connect(self.dedent)

        self.formatbar = self.addToolBar("Format")

        self.formatbar.addWidget(fontBox)
        self.formatbar.addWidget(fontSize)

        self.formatbar.addSeparator()

        self.formatbar.addAction(fontColor)
        self.formatbar.addAction(backColor)

        self.formatbar.addSeparator()

        self.formatbar.addAction(boldAction)
        self.formatbar.addAction(italicAction)
        self.formatbar.addAction(underlAction)
        self.formatbar.addAction(strikeAction)
        self.formatbar.addAction(superAction)
        self.formatbar.addAction(subAction)

        self.formatbar.addSeparator()

        self.formatbar.addAction(alignLeft)
        self.formatbar.addAction(alignCenter)
        self.formatbar.addAction(alignRight)
        self.formatbar.addAction(alignJustify)

        self.formatbar.addSeparator()

        self.formatbar.addAction(indentAction)
        self.formatbar.addAction(dedentAction)

    def initMenubar(self):

        menubar = self.menuBar()

        file = menubar.addMenu("File")
        edit = menubar.addMenu("Edit")
        view = menubar.addMenu("View")

        if self.fileactions:
            file.addAction(self.new_act)
            file.addAction(self.save_act)
        file.addAction(self.open_act)
        file.addAction(self.print_act)
        file.addAction(self.preview_act)

        edit.addAction(self.undo_act)
        edit.addAction(self.redo_act)
        edit.addAction(self.cut_act)
        edit.addAction(self.copy_act)
        edit.addAction(self.paste_act)

        # Toggling actions for the various bars
        toolbarAction = QtWidgets.QAction("Toggle Toolbar", self)
        toolbarAction.triggered.connect(self.toggleToolbar)

        formatbarAction = QtWidgets.QAction("Toggle Formatbar", self)
        formatbarAction.triggered.connect(self.toggleFormatbar)

        statusbarAction = QtWidgets.QAction("Toggle Statusbar", self)
        statusbarAction.triggered.connect(self.toggleStatusbar)

        view.addAction(toolbarAction)
        view.addAction(formatbarAction)
        view.addAction(statusbarAction)

    def initToolbar(self):

        self.new_act = QtWidgets.QAction(QtGui.QIcon(":New"), "New", self)
        self.new_act.setShortcut("Ctrl+N")
        self.new_act.setStatusTip("Create a new document from scratch.")
        self.new_act.triggered.connect(self.new)

        self.open_act = QtWidgets.QAction(QtGui.QIcon(":Open"), "Open file", self)
        self.open_act.setStatusTip("Open existing document")
        self.open_act.setShortcut("Ctrl+O")
        self.open_act.triggered.connect(self.open)

        self.save_act = QtWidgets.QAction(QtGui.QIcon(":Save"), "Save", self)
        self.save_act.setStatusTip(":Save")
        self.save_act.setShortcut("Ctrl+S")
        self.save_act.triggered.connect(self.save)

        self.print_act = QtWidgets.QAction(QtGui.QIcon(":Print"), "Print document", self)
        self.print_act.setStatusTip(":Print")
        self.print_act.setShortcut("Ctrl+P")
        self.print_act.triggered.connect(self.printHandler)

        self.preview_act = QtWidgets.QAction(QtGui.QIcon(":PreviewPane"), "Page view", self)
        self.preview_act.setStatusTip("Preview page before printing")
        self.preview_act.setShortcut("Ctrl+Shift+P")
        self.preview_act.triggered.connect(self.preview)

        self.cut_act = QtWidgets.QAction(QtGui.QIcon(":Cut"), "Cut to clipboard", self)
        self.cut_act.setStatusTip("Delete and copy text to clipboard")
        self.cut_act.setShortcut("Ctrl+X")
        self.cut_act.triggered.connect(self.text_tedit.cut)

        self.copy_act = QtWidgets.QAction(QtGui.QIcon(":Copy"), "Copy to clipboard", self)
        self.copy_act.setStatusTip("Copy text to clipboard")
        self.copy_act.setShortcut("Ctrl+C")
        self.copy_act.triggered.connect(self.text_tedit.copy)

        self.paste_act = QtWidgets.QAction(QtGui.QIcon(":Paste"), "Paste from clipboard", self)
        self.paste_act.setStatusTip("Paste text from clipboard")
        self.paste_act.setShortcut("Ctrl+V")
        self.paste_act.triggered.connect(self.text_tedit.paste)

        self.undo_act = QtWidgets.QAction(QtGui.QIcon(":Undo"), "Undo last action", self)
        self.undo_act.setStatusTip("Undo last action")
        self.undo_act.setShortcut("Ctrl+Z")
        self.undo_act.triggered.connect(self.text_tedit.undo)

        self.redo_act = QtWidgets.QAction(QtGui.QIcon(":Redo"), "Redo last undone thing", self)
        self.redo_act.setStatusTip("Redo last undone thing")
        self.redo_act.setShortcut("Ctrl+Y")
        self.redo_act.triggered.connect(self.text_tedit.redo)

        self.bullet_act = QtWidgets.QAction(QtGui.QIcon(":BulletedList"),"Insert bullet List",self)
        self.bullet_act.setStatusTip("Insert bullet list")
        self.bullet_act.setShortcut("Ctrl+Shift+B")
        self.bullet_act.triggered.connect(self.bulletList)

        self.numbered_act = QtWidgets.QAction(QtGui.QIcon(":NumberedList"),"Insert numbered List",self)
        self.numbered_act.setStatusTip("Insert numbered list")
        self.numbered_act.setShortcut("Ctrl+Shift+L")
        self.numbered_act.triggered.connect(self.numberList)

        self.toolbar = self.addToolBar("Options")
        iconSize=QtCore.QSize(16, 16)
        self.toolbar.setIconSize(iconSize)

        if self.fileactions:
            self.toolbar.addAction(self.new_act)
            self.toolbar.addAction(self.save_act)

        self.toolbar.addAction(self.open_act)

        self.toolbar.addSeparator()

        self.toolbar.addAction(self.print_act)
        self.toolbar.addAction(self.preview_act)

        self.toolbar.addSeparator()

        self.toolbar.addAction(self.cut_act)
        self.toolbar.addAction(self.copy_act)
        self.toolbar.addAction(self.paste_act)
        self.toolbar.addAction(self.undo_act)
        self.toolbar.addAction(self.redo_act)

        self.toolbar.addSeparator()

        self.toolbar.addAction(self.bullet_act)
        self.toolbar.addAction(self.numbered_act)

        # Makes the next toolbar appear underneath this one
        self.addToolBarBreak()

    def initUI(self):

        self.text_tedit = QtWidgets.QTextEdit(self)

        self.initToolbar()
        self.initFormatbar()
        self.initMenubar()

        # Set the tab stop width to around 33 pixels which is
        # about 8 spaces
        self.text_tedit.setTabStopWidth(33)
        self.text_tedit.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.setCentralWidget(self.text_tedit)

        # Initialize a statusbar for the window
        self.statusbar = self.statusBar()

        # If the cursor position changes, call the function that displays
        # the line and column number
        self.text_tedit.cursorPositionChanged.connect(self.cursorPosition)
        self.text_tedit.customContextMenuRequested.connect(self.on_textEditContextMenu)

        # x and y coordinates on the screen, width, height
        #self.setGeometry(100, 100, 1030, 800)

        self.setWindowTitle("Writer")

        self.setWindowIcon(QtGui.QIcon(":Checked"))

        self.toggleToolbar_act = QtWidgets.QAction("Toggle Toolbar")
        self.toggleToolbar_act.triggered.connect(self.toggleToolbar)
        self.toggleFormatbar_act = QtWidgets.QAction("Toggle Formatbar")
        self.toggleFormatbar_act.triggered.connect(self.toggleFormatbar)

        self.setAutoFillBackground(True)
        self.setMouseTracking(True)


    def italic(self):

        state = self.text_tedit.fontItalic()

        self.text_tedit.setFontItalic(not state)

    def new(self):

        spawn = TextEditor(self)
        spawn.show()

    def numberList(self):

        cursor = self.text_tedit.textCursor()

        # Insert list with numbers
        cursor.insertList(QtGui.QTextListFormat.ListDecimal)

    def open(self):

        # Get filename and show only .writer files
        # PYQT5 Returns a tuple in PyQt5, we only need the filename
        self.filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', ".", "(*.writer)")[0]

        if self.filename:
            with open(self.filename, "rt") as file:
                self.text_tedit.setText(file.read())

    def preview(self):

        # Open preview dialog
        preview = QtPrintSupport.QPrintPreviewDialog()

        # If a print is requested, open print dialog
        preview.paintRequested.connect(lambda p: self.text_tedit.print_(p))

        preview.exec_()

    def printHandler(self):

        # Open printing dialog
        dialog = QtPrintSupport.QPrintDialog()

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.text_tedit.document().print_(dialog.printer())

    def save(self):

        # Only open dialog if there is no filename yet
        # PYQT5 Returns a tuple in PyQt5, we only need the filename
        if not self.filename:
            self.filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File')[0]

        if self.filename:

            # Append extension if not there yet
            if not self.filename.endswith(".writer"):
                self.filename += ".writer"

            # We just store the contents of the text file along with the
            # format in html, which Qt does in a very nice way for us
            with open(self.filename, "wt") as file:
                file.write(self.text_tedit.toHtml())

            self.changesSaved = True

    def setFormatbarVisible(self, status):
        self.formatbar.setVisible(status)

    def setToolbarVisible(self, status):
        self.toolbar.setVisible(status)

    def setStatusBarVisible(self, status):
        self.toolbar.setVisible(status)

    def setText(self, text):
        self.text_tedit.setText(text)

    def strike(self):

        # Grab the text's format
        fmt = self.text_tedit.currentCharFormat()

        # Set the fontStrikeOut property to its opposite
        fmt.setFontStrikeOut(not fmt.fontStrikeOut())

        # And set the next char format
        self.text_tedit.setCurrentCharFormat(fmt)

    def superScript(self):

        # Grab the current format
        fmt = self.text_tedit.currentCharFormat()

        # And get the vertical alignment property
        align = fmt.verticalAlignment()

        # Toggle the state
        if align == QtGui.QTextCharFormat.AlignNormal:

            fmt.setVerticalAlignment(QtGui.QTextCharFormat.AlignSuperScript)

        else:

            fmt.setVerticalAlignment(QtGui.QTextCharFormat.AlignNormal)

        # Set the new format
        self.text_tedit.setCurrentCharFormat(fmt)

    def subScript(self):

        # Grab the current format
        fmt = self.text_tedit.currentCharFormat()

        # And get the vertical alignment property
        align = fmt.verticalAlignment()

        # Toggle the state
        if align == QtGui.QTextCharFormat.AlignNormal:

            fmt.setVerticalAlignment(QtGui.QTextCharFormat.AlignSubScript)

        else:

            fmt.setVerticalAlignment(QtGui.QTextCharFormat.AlignNormal)

        # Set the new format
        self.text_tedit.setCurrentCharFormat(fmt)

    def toggleFormatbar(self, value:bool=None):

        state = self.formatbar.isVisible()

        # Set the visibility to its inverse
        self.formatbar.setVisible(not state)

    def toggleStatusbar(self, value:bool=None):

        state = self.statusbar.isVisible()

        # Set the visibility to its inverse
        self.statusbar.setVisible(not state)

    def toggleToolbar(self, value:bool=None):

        state = self.toolbar.isVisible()

        # Set the visibility to its inverse
        self.toolbar.setVisible(not state)

    def underline(self):

        state = self.text_tedit.fontUnderline()

        self.text_tedit.setFontUnderline(not state)


def main():
    app = QtWidgets.QApplication(sys.argv)

    main = TextEditor(fileactions=False, parent=None)
    main.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()