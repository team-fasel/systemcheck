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


class TextLineEdit(QtWidgets.QWidget):
    returnPressed = QtCore.pyqtSignal()
    textChanged = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        stylesheet = 'border: 0px transparent'
        layout=QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self._line_edit = QtWidgets.QLineEdit()
        self._line_edit.setStyleSheet(stylesheet)
        layout.addWidget(self._line_edit)
        self.setLayout(layout)
        self._line_edit.textChanged.connect(self.textChanged)
        self._line_edit.returnPressed.connect(self.returnPressed)

    def setBackgroundRole(self, *args, **kwargs):
        self._line_edit.setBackgroundRole(*args, **kwargs)

    def setText(self, text):
        self._line_edit.setText(text)

    def text(self):
        return self._line_edit.text()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    lineedit = TextLineEdit()
    lineedit.show()
    lineedit.setWindowTitle("RichTextEdit")
    app.exec_()
    print(lineedit.toHtml())
    print(lineedit.toPlainText())
    print(lineedit.toSimpleHtml())


