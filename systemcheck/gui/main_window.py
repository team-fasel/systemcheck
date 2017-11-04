from PyQt5 import QtCore, QtWidgets, QtGui
from systemcheck.resources import icon_rc
import systemcheck
from systemcheck.checks.models import Check
from systemcheck.gui.models import GenericTreeModel
from systemcheck.systems.generic.models import GenericSystem
from systemcheck.session import SESSION
from systemcheck import utils

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi()
        self.show()

    def addSystemType(self, object, name, icon=None):

        object.systemModel = self.system_model
        object.checkModel = self.check_model
        self.systemTypes_tabw.addTab(object, name)
        current=self.systemTypes_tabw.currentIndex()
        self.systemTypes_tabw.setTabIcon(current, QtGui.QIcon(icon))


    def setupUi(self):
        self.setWindowIcon(QtGui.QIcon(':Checked'))
        self.setWindowTitle('SystemCheck')
        self.systemTypes_tabw = QtWidgets.QTabWidget()
        self.systemTypes_tabw.setContentsMargins(0, 0, 0, 0)
        #self.systemTypes_tabw.setStyleSheet('QTabWidget::pane { border: 0 solid white; margin: -13px -9px -13px -9px;}')
        self.setMinimumHeight(768)
        self.setMinimumWidth(1366)

        self.setupActions()
        self.generateMenu()

        self.setCentralWidget(self.systemTypes_tabw)
        self.systemTypes_tabw.setTabPosition(QtWidgets.QTabWidget.West)

        self.program_toolbar=QtWidgets.QToolBar()
        self.program_toolbar.addAction(self.quit_act)
        self.program_toolbar.setToolTip('SystemCheck Tool Bar')

        self.addToolBar(self.program_toolbar)

        self.system_toolbar = QtWidgets.QToolBar()
        self.system_toolbar.addAction(self.systemsNewFolder_act)
        self.system_toolbar.setToolTip('System Toolbar')
        self.system_toolbar.addAction(self.systemsNew_act)
        self.system_toolbar.addAction(self.systemsDelete_act)
        self.system_toolbar.addSeparator()
        self.system_toolbar.addAction(self.systemsExport_act)
        self.system_toolbar.addAction(self.systemsImport_act)
        self.addToolBar(self.system_toolbar)

        self.checks_toolbar = QtWidgets.QToolBar()
        self.checks_toolbar.setToolTip('Checks Toolbar')
        self.checks_toolbar.addAction(self.checksRun_act)
        self.checks_toolbar.addAction(self.checksPause_act)
        self.checks_toolbar.addAction(self.checksStop_act)
        self.checks_toolbar.addSeparator()
        self.checks_toolbar.addAction(self.checksExport_act)
        self.checks_toolbar.addAction(self.checksImport_act)
        self.checks_toolbar.addSeparator()
        self.checks_toolbar.addAction(self.checksNew_act)
        self.checks_toolbar.addAction(self.checksNewFolder_act)
        self.checks_toolbar.addAction(self.checksDelete_act)
        self.addToolBar(self.checks_toolbar)

        system_root = utils.get_or_create(SESSION, GenericSystem, parent_id=None, name='RootNode')
        check_root = utils.get_or_create(SESSION, Check, parent_id=None, name='RootNode')

        self.system_model = GenericTreeModel(system_root)
        self.check_model = GenericTreeModel(check_root)

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
        checks_menu.addAction(self.checksDelete_act)
        checks_menu.addSeparator()
        checks_menu.addAction(self.checksImport_act)
        checks_menu.addAction(self.checksExport_act)
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

        self.systemsDisable_act = QtWidgets.QAction(QtGui.QIcon(':Hide'), 'Disable Systems')
        self.systemsDisable_act.triggered.connect(self.on_systemsDisable)
        self.systemsDisable_act.setEnabled(False)

        self.systemsEnable_act = QtWidgets.QAction(QtGui.QIcon(':Eye'), 'Enable Systems')
        self.systemsEnable_act.triggered.connect(self.on_systemsEnable)
        self.systemsEnable_act.setEnabled(False)

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

        self.checksExport_act = QtWidgets.QAction(QtGui.QIcon(':Export'), 'Export Checks...')
        self.checksExport_act.triggered.connect(self.on_checksExport)

        self.checksRun_act = QtWidgets.QAction(QtGui.QIcon(':Play'), 'Run Checks')
        self.checksRun_act.triggered.connect(self.on_checksRun)
        self.checksRun_act.setEnabled(True)

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

        self.resultsClear_act = QtWidgets.QAction(QtGui.QIcon(':ClearSymbol'), 'Clear Results')
        self.resultsClear_act.triggered.connect(self.on_resultsClear)
        self.resultsClear_act.setEnabled(False)


    def on_checksDelete(self):
        self.systemTypes_tabw.currentWidget().signals.checksDelete.emit()

    def on_checksExport(self):
        self.systemTypes_tabw.currentWidget().signals.checksExport.emit()

    def on_checksImport(self):
        self.systemTypes_tabw.currentWidget().signals.checksImport.emit()

    def on_checksNew(self):
        self.systemTypes_tabw.currentWidget().signals.checksNew.emit()

    def on_checksNewFolder(self):
        self.systemTypes_tabw.currentWidget().signals.checksNewFolder.emit()

    def on_checksPause(self):
        self.systemTypes_tabw.currentWidget().signals.checksPause.emit()

    def on_checksRun(self):
        self.systemTypes_tabw.currentWidget().signals.checksRun.emit()

    def on_checksStop(self):
        self.systemTypes_tabw.currentWidget().signals.checksStop.emit()

    def on_resultsClear(self):
        self.systemTypes_tabw.currentWidget().signals.resultClear.emit()

    def on_resultsExport(self):
        self.systemTypes_tabw.currentWidget().signals.resultExport.emit()

    def on_resultsImport(self):
        self.systemTypes_tabw.currentWidget().signals.resultImport_signal.emit()

    def on_systemsCheckLogon(self):
        self.systemTypes_tabw.currentWidget().signals.systemsCheckLogon.emit()

    def on_systemsDelete(self):
        self.systemTypes_tabw.currentWidget().signals.systemsDelete.emit()

    def on_systemsDisable(self):
        self.systemTypes_tabw.currentWidget().signals.systemsDisable.emit()

    def on_systemsEnable(self):
        self.systemTypes_tabw.currentWidget().signals.systemsEnable.emit()

    def on_systemsExport(self):
        self.systemTypes_tabw.currentWidget().signals.systemsExport.emit()

    def on_systemsImport(self):
        self.systemTypes_tabw.currentWidget().signals.systemsImport.emit()

    def on_systemsNew(self):
        self.systemTypes_tabw.currentWidget().signals.systemsNew.emit()

    def on_systemsNewFolder(self):
        self.systemTypes_tabw.currentWidget().signals.systemsNewFolder.emit()

