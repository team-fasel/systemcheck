from PyQt5 import QtWidgets, QtGui, QtCore
from systemcheck.gui.models import PolyMorphicFilterProxyModel
from systemcheck.systems.generic.gui.widgets import GenericSystemWidget
from systemcheck.checks.gui.widgets.checks_widget import ChecksWidget
from systemcheck.results.gui.widgets.result_widget import ResultWidget
from systemcheck.resources import icon_rc
import logging
import systemcheck.plugins
from pprint import pprint, pformat
from typing import Union
from collections import namedtuple

class Signals(QtCore.QObject):
    
    checksDelete = QtCore.pyqtSignal()
    checksExport = QtCore.pyqtSignal()
    checksImport = QtCore.pyqtSignal()
    checksNew = QtCore.pyqtSignal()
    checksNewFolder = QtCore.pyqtSignal()
    checksPause = QtCore.pyqtSignal()
    checksRun = QtCore.pyqtSignal()
    checksStop = QtCore.pyqtSignal()
    resultClear = QtCore.pyqtSignal()
    resultExport = QtCore.pyqtSignal()
    resultImport = QtCore.pyqtSignal()
    systemsCheckLogon = QtCore.pyqtSignal()
    systemsDelete = QtCore.pyqtSignal()
    systemsDisable = QtCore.pyqtSignal()
    systemsEnable = QtCore.pyqtSignal()
    systemsExport = QtCore.pyqtSignal()
    systemsImport = QtCore.pyqtSignal()
    systemsNew = QtCore.pyqtSignal()
    systemsNewFolder = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

class GenericSystemMainWidget(QtWidgets.QWidget):

    def __init__(self, systemType:str='generic', systemFilter:list = None, systemsWidget:QtWidgets.QWidget=None):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.signals = Signals()
        self.systemType=systemType
        self.initializePluginManager()
        self.setupCommonUi(systemsWidget)

        self.systemFilter = systemFilter

        self.__checkModel = None
        self.__systemType = None
        self.__systemModel = None


    def buildTaskList(self, systems:set, checks:set)->set:
        """ Build the Task List

        :param systems: A set of Systems that were checked
        :param checks: A set of Checks that were checked

        """

        Task = namedtuple('Task', 'system check')

        taskList = set()

        if systems and checks:
            for system in systems:
                for check in checks:
                    task = Task(system=system, check=check)
                    taskList.add(task)

        return taskList

    def checkedChecks(self)->set:
        """ Get List of checked Checks """

        pluginNames = {plugin.name
                       for plugin in self.pm.getPlugins(category='check', systemtype=self.systemType)}

        checkedChecks = {node
                         for node in self.checks.tree.model().checkedNodes()
                         if node.type in pluginNames}

        return checkedChecks

    def checkedSystems(self)->set:
        """ Get List of checked Systems """

        checkedSystems = {node
                          for node in self.systems.tree.model().checkedNodes()
                          if node.logon_info() is not None}

        return checkedSystems

    @property
    def checkFilter(self):
        """ Return the Relevant Check Objects for the system type """
        self.logger.debug('Building Check Filter')
        checksFilterList = set()
        pm = systemcheck.plugins.SysCheckPM()

        for plugin in pm.getPlugins(category='check', systemtype=self.systemType):
            for object in plugin.plugin_object.alchemyObjects:
                checksFilterList.add(object)

        self.logger.debug('CheckFilter determined: %s', pformat(checksFilterList))
        return checksFilterList

    @property
    def checkModel(self):
        """ The QAbstractItem Model for Checks """
        return self.__checkModel

    @checkModel.setter
    def checkModel(self, model):
        """ Sets the data model for the checks


        By default the checks are restricted using a QSortFilterProxyModel. The filter is generated from the plugin
        manager based on the system type

        """

        self.__checkModel = model

        self.checkSortFilterProxyModel = PolyMorphicFilterProxyModel(self.checkFilter)
        self.checkSortFilterProxyModel.setSourceModel(self.checkModel)
        self.checks.setModel(self.checkSortFilterProxyModel)

    @property
    def checkSortFilterProxyModel(self):
        return self.__checkSortFilterProxyModel

    @checkSortFilterProxyModel.setter
    def checkSortFilterProxyModel(self, model):
        self.__checkSortFilterProxyModel = model

    def initializePluginManager(self):
        self.pm = systemcheck.plugins.SysCheckPM()

    def on_checksRun(self):

        systems=self.checkedSystems()
        checks=self.checkedChecks()

        tasklist = self.buildTaskList(systems=systems, checks=checks)

        for task in tasklist:
            plugin=self.pm.getPlugin(task.check.type)
            result = plugin.plugin_object.executeAction(task.system, task.check)
            self.results.resultAdd_signal.emit(result)

    def setupCommonUi(self, systemsWidget:QtWidgets.QWidget=None):

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        self.setWindowTitle('Generic Main Widget')
        self.setWindowIcon(QtGui.QIcon(':Checked'))

        self.checksResults_splitter = QtWidgets.QSplitter()
        self.checksResults_splitter.setOrientation(QtCore.Qt.Vertical)
        self.systemsChecks_splitter = QtWidgets.QSplitter()
        self.systemsChecks_splitter.setOrientation(QtCore.Qt.Horizontal)

        # Verify whether the plugin provides a systems widget. If not, use the generic.
        if systemsWidget:
            self.logger.debug('systems widget provided by systems plugin')
            self.systems = systemsWidget()
        else:
            self.logger.debug('systems widget not provided by systems plugin, using generic widget')
            self.systems = GenericSystemWidget()
        self.systemsChecks_splitter.addWidget(self.systems)
        self.systemsChecks_splitter.addWidget(self.checksResults_splitter)

        self.checks = ChecksWidget(self.systemType)
        self.checksResults_splitter.addWidget(self.checks)

        self.results = ResultWidget()
        self.checksResults_splitter.addWidget(self.results)

        layout.addWidget(self.systemsChecks_splitter)

        self.show()

        self.signals.checksDelete.connect(self.checks.on_checkDelete)
        self.signals.checksExport.connect(self.checks.on_checkExport)
        self.signals.checksImport.connect(self.checks.on_checkImport)
        self.signals.checksNew.connect(self.checks.on_checkNew)
        self.signals.checksNewFolder.connect(self.checks.on_checkNewFolder)
        self.signals.checksPause.connect(self.checks.on_checkPause)
        self.signals.checksRun.connect(self.on_checksRun)
        self.signals.checksStop.connect(self.checks.on_checkStop)
        self.signals.resultClear.connect(self.results.on_resultClear)
        self.signals.resultExport.connect(self.results.resultHandler.on_resultExport)
        self.signals.resultImport.connect(self.results.resultHandler.on_resultImport)
        self.signals.systemsCheckLogon.connect(self.systems.on_checkLogon)
        self.signals.systemsNewFolder.connect(self.systems.on_newFolder)
        self.signals.systemsNew.connect(self.systems.on_new)
        self.signals.systemsDelete.connect(self.systems.on_delete)
        self.signals.systemsImport.connect(self.systems.on_import)
        self.signals.systemsExport.connect(self.systems.on_export)
        self.signals.systemsDisable.connect(self.systems.on_disable)
        self.signals.systemsEnable.connect(self.systems.on_enable)

    @property
    def systemModel(self)->QtCore.QAbstractItemModel:
        """ Get the System QAbstractItemModel """
        return self.__systemModel

    @systemModel.setter
    def systemModel(self, model:QtCore.QAbstractItemModel)->bool:
        """ Set the System QAbstractItemModel """
        self.__systemModel = model
        sm = PolyMorphicFilterProxyModel(self.systemFilter)
        sm.setSourceModel(self.systemModel)
        self.systemSortFilterProxyModel = sm
        self.systems.setModel(self.systemSortFilterProxyModel)
        return True


    @property
    def systemSortFilterProxyModel(self):
        return self.__systemSortFilterProxyModel

    @systemSortFilterProxyModel.setter
    def systemSortFilterProxyModel(self, proxymodel):
        self.__systemSortFilterProxyModel = proxymodel

    @property
    def systemFilter(self):
        return self.__systemFilter

    @systemFilter.setter
    def systemFilter(self, systemFilter:list):
        self.__systemFilter = systemFilter

    @property
    def systemType(self):
        return self.__systemType

    @systemType.setter
    def systemType(self, systemType:str):
        self.__systemType = systemType



