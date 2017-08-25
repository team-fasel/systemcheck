from PyQt5 import QtWidgets, QtCore


class ProgressBar(QtWidgets.QWidget):


    complete = QtCore.pyqtSignal()
    initalize = QtCore.pyqtSignal(int, int)
    increase = QtCore.pyqtSignal(int)
    set = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()



