from PyQt5 import QtCore, QtWidgets, QtGui
from systemcheck.resources import icon_rc
import systemcheck



class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(QtWidgets.QMainWindow, self).__init__()
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
        self.systemTypes_tabw.setTabPosition(QtWidgets.QTabWidget.West)

    def generateMenu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(self.quit_act)

        systems_menu = menubar.addMenu('&Systems')
        systems_menu.addAction(self.systemsCheckLogon_act)
        systems_menu.addSeparator()
        systems_menu.addAction(self.systemsNewFolder_act)
        systems_menu.addAction(self.systemsNew_act)
        systems_menu.addAction(self.systemsImport_act)
        systems_menu.addAction(self.systemsExport_act)
        systems_menu.addSeparator()
        systems_menu.addAction(self.systemsDelete_act)

        checks_menu = menubar.addMenu('&Checks')
        checks_menu.addAction(self.checksNewFolder_act)
        checks_menu.addAction(self.checksNew_act)
        checks_menu.addAction(self.checksImport_act)
        checks_menu.addAction(self.checksImport_act)
        checks_menu.addAction(self.checksDelete_act)
        checks_menu.addSeparator()
        checks_menu.addAction(self.checksRun_act)
        checks_menu.addAction(self.checksPause_act)
        checks_menu.addAction(self.checksStop_act)

        results_menu = menubar.addMenu('&Results')
        results_menu.addAction(self.resultsExport_act)
        results_menu.addAction(self.resultsImport_act)


        help_menu = menubar.addMenu('&Help')
        help_menu.addAction(self.about_act)

    def setModel(self, system=None, check=None):
        if system is not None:
            self.system_model = system
            self.abap_tab.setModel(system=self.system_model)

        if check is not None:
            self.checks_model = check
            self.abap_tab.setModel(check=self.checks_model)

    def setupActions(self):
        """ Define Actions in the Main Widget

        THe main window will consist for the most part of a single QTabWidget. The QTabWidget has a tab for each system
        type (ABAP, HANA, Windows, Linux, ...

        Many of the functions that need to get executed are common for all system types. For example creating a new system
        or adding a new check.

        Many of these functions are identical across all system specific tab widgets. The actions will emit the
        corresponding signals implemented in the system specific widget.

        """

        self.quit_act = QtWidgets.QAction(QtGui.QIcon(':ExitSign'), 'Quit')
        self.quit_act.setShortcut(QtGui.QKeySequence.Quit)
        self.quit_act.setStatusTip('Quit the application')
        self.quit_act.triggered.connect(QtWidgets.QApplication.quit)

        self.about_act = QtWidgets.QAction(QtGui.QIcon(':Information'), 'About...')

        self.systemsCheckLogon_act = QtWidgets.QAction(QtGui.QIcon(':Login'), 'Test Login')
        self.systemsCheckLogon_act.triggered.connect(self.on_systemsCheckLogon)
        self.systemsCheckLogon_act.setEnabled(False)

        self.systemsNewFolder_act = QtWidgets.QAction(QtGui.QIcon(':AddFolder'), 'Add Folder')
        self.systemsNewFolder_act.triggered.connect(self.on_systemsNewFolder)
        self.systemsNewFolder_act.setEnabled(False)

        self.systemsNew_act = QtWidgets.QAction(QtGui.QIcon(':AddFile'), 'Add New System')
        self.systemsNew_act.triggered.connect(self.on_systemsNew)
        self.systemsNew_act.setEnabled(False)

        self.systemsDelete_act = QtWidgets.QAction(QtGui.QIcon(':Trash'), 'Delete Selected Systems')
        self.systemsDelete_act.triggered.connect(self.on_systemsDelete)
        self.systemsDelete_act.setEnabled(False)

        self.systemsImport_act = QtWidgets.QAction(QtGui.QIcon(':Import'), '&Import Systems')
        self.systemsImport_act.triggered.connect(self.on_systemsImport)
        self.systemsImport_act.setEnabled(False)

        self.systemsExport_act = QtWidgets.QAction(QtGui.QIcon(':Export'), '&Export Systems')
        self.systemsExport_act.triggered.connect(self.on_systemsExport)
        self.systemsExport_act.setEnabled(False)

        self.checksNewFolder_act = QtWidgets.QAction(QtGui.QIcon(':AddFolder'), 'Add Folder')
        self.checksNewFolder_act.triggered.connect(self.on_checksNewFolder)
        self.checksNewFolder_act.setEnabled(False)

        self.checksNew_act = QtWidgets.QAction(QtGui.QIcon(':AddFile'), 'Add New Check...')
        self.checksNew_act.triggered.connect(self.on_checksNew)
        self.checksNew_act.setEnabled(False)

        self.checksDelete_act =  QtWidgets.QAction(QtGui.QIcon(':Trash'), 'Delete Selected Checks')
        self.checksDelete_act.triggered.connect(self.on_checksDelete)
        self.checksDelete_act.setEnabled(False)

        self.checksImport_act = QtWidgets.QAction(QtGui.QIcon(':Import'), 'Import Checks...')
        self.checksImport_act.triggered.connect(self.on_checksImport)
        self.checksImport_act.setEnabled(False)

        self.checksExport_act = QtWidgets.QAction(QtGui.QIcon(':Export'), 'Export Checks...')
        self.checksExport_act.triggered.connect(self.on_checksExport)
        self.checksExport_act.setEnabled(False)

        self.checksRun_act = QtWidgets.QAction(QtGui.QIcon(':Play'), 'Run Checks')
        self.checksRun_act.triggered.connect(self.on_checksRun)
        self.checksRun_act.setEnabled(False)

        self.checksPause_act = QtWidgets.QAction(QtGui.QIcon(':Pause'), 'Pause Checks')
        self.checksPause_act.triggered.connect(self.on_checksPause)
        self.checksPause_act.setEnabled(False)

        self.checksStop_act = QtWidgets.QAction(QtGui.QIcon(':Stop'), 'Stop Checks')
        self.checksStop_act.triggered.connect(self.on_checksPause)
        self.checksStop_act.setEnabled(False)

        self.resultsExport_act = QtWidgets.QAction(QtGui.QIcon(':Export'), 'Export Results...')
        self.resultsExport_act.triggered.connect(self.on_resultsExport)
        self.resultsExport_act.setEnabled(False)

        self.resultsImport_act = QtWidgets.QAction(QtGui.QIcon(':Import'), 'Import Results...')
        self.resultsImport_act.triggered.connect(self.on_resultsImport)
        self.resultsImport_act.setEnabled(False)

    def on_checksNew(self):
        self.systemTypes_tabw.currentWidget().checksNew.emit()

    def on_checksNewFolder(self):
        self.systemTypes_tabw.currentWidget().checksNewFolder.emit()

    def on_checksDelete(self):
        self.systemTypes_tabw.currentWidget().checksDelete.emit()

    def on_checksImport(self):
        self.systemTypes_tabw.currentWidget().checksImport.emit()

    def on_checksExport(self):
        self.systemTypes_tabw.currentWidget().checksExport.emit()

    def on_checksRun(self):
        self.systemTypes_tabw.currentWidget().checksRun.emit()

    def on_checksPause(self):
        self.systemTypes_tabw.currentWidget().checksPause.emit()

    def on_checksStop(self):
        self.systemTypes_tabw.currentWidget().checksStop.emit()

    def on_resultsExport(self):
        self.systemTypes_tabw.currentWidget().resultsExport.emit()

    def on_resultsImport(self):
        self.systemTypes_tabw.currentWidget().resultsImport.emit()

    def on_systemsCheckLogon(self):
        self.systemTypes_tabw.currentWidget().systemsCheckLogon.emit()

    def on_systemsNewFolder(self):
        self.systemTypes_tabw.currentWidget().systemsNewFolder.emit()

    def on_systemsNew(self):
        self.systemTypes_tabw.currentWidget().systemsNew.emit()

    def on_systemsDelete(self):
        self.systemTypes_tabw.currentWidget().systems.Delete.emit()

    def on_systemsImport(self):
        self.systemTypes_tabw.currentWidget().systemsImport.emit()

    def on_systemsExport(self):
        self.systemTypes_tabw.currentWidget().systemsExport.emit()

