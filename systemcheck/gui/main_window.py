from PyQt5 import QtCore, QtWidgets, QtGui
from systemcheck.resources import icon_rc
import systemcheck



class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi()
        self.show()


    def setupUi(self):
        self.setWindowIcon(QtGui.QIcon(':Checked'))
        self.setWindowTitle('SystemCheck')
        self.systemTypes_tabw = QtWidgets.QTabWidget()
        self.setMinimumHeight(768)
        self.setMinimumWidth(1024)

        self.setupActions()
        self.generateMenu()

        self.setCentralWidget(self.systemTypes_tabw)

        self.abap_tab=systemcheck.systems.ABAP.gui.AbapWidget()
        self.systemTypes_tabw.addTab(self.abap_tab, 'ABAP')
        self.systemTypes_tabw.setTabPosition(QtWidgets.QTabWidget.West)

    def setupActions(self):

        self.quit_act = QtWidgets.QAction(QtGui.QIcon(':ExitSign'), 'Quit')
        self.quit_act.setShortcut(QtGui.QKeySequence.Quit)
        self.quit_act.setStatusTip('Quit the application')
        self.quit_act.triggered.connect(QtWidgets.QApplication.quit)

        self.about_act = QtWidgets.QAction(QtGui.QIcon(':Information'), 'About...')

    def generateMenu(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        systemsMenu = menubar.addMenu('&Systems')
        helpMenu = menubar.addMenu('&Help')
        fileMenu.addAction(self.quit_act)
        helpMenu.addAction(self.about_act)


    def setModel(self, system=None, check=None):
        if system is not None:
            self.system_model = system
            self.abap_tab.setModel(system=self.system_model)

        if check is not None:
            self.checks_model = check
            self.abap_tab.setModel(check=self.checks_model)

