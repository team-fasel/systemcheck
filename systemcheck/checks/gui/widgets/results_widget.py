from PyQt5 import QtWidgets, QtCore, QtGui
from systemcheck.resources import icon_rc
import logging


class CheckResultsWidget(QtWidgets.QWidget):

    addResult_signal = QtCore.pyqtSignal('PyQt_PyObject')

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))
        self.setupUi()
        self.show()

    def setupUi(self):

        self.results_tabw = QtWidgets.QTabWidget()
        self.setWindowTitle('SystemCheck Results')
        self.setWindowIcon(QtGui.QIcon(':Checked'))
        self.resultsDetails_splitter = QtWidgets.QSplitter()
        self.resultsDetails_splitter.setOrientation(QtCore.Qt.Vertical)
        self.resultsDetails_splitter.addWidget(self.results_tabw)

        self.overview=QtWidgets.QTreeView()

        self.results_tabw.addTab(self.overview, 'Overview')

        self.details=QtWidgets.QTableView()
        self.resultsDetails_splitter.addWidget(self.details)

        layout=QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.resultsDetails_splitter)
        self.setLayout(layout)

    def setupActions(self):
        self.addResult_signal.triggered.connect(self.addResult)

    @QtCore.pyqtSlot('PyQt_PyObject')
    def addResult(self):
        pass

    def exportResults(self):
        """ Exports the retrieved Results


        """
        pass


class CheckDetailResultsWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))

    def setupUi(self):
        self.table = QtWidgets.QTableView()
