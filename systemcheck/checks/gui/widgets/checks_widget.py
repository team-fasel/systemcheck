from PyQt5 import QtWidgets, QtCore, QtGui
import systemcheck
import logging
#from systemcheck.checks.gui.widgets import CheckParameterEditorWidget
#from systemcheck.checks.gui.widgets import CheckSettingsWidget
from collections import OrderedDict
from typing import Any
from pprint import pprint
import functools
from systemcheck.resources import icon_rc
from os.path import expanduser

class CheckHandler(QtCore.QObject):
    """ Check Handler

    The handler contains manages the plugins and their execution.

    """
    def __init__(self):
        super().__init__()
        self.pm = systemcheck.plugins.SysCheckPM()

    def runCheck(self, logons, checks):

        for check in checks:
            plugin=self.pm.getPluginByName(check.__name__)
            result = plugin.plugin_object.execute_plugin()

    def parameterForm(self, check_name):

        plugin = self.pm.getPlugin(check_name)
        form = plugin.plugin_object.parameterForm
        return form


    def checkActions(self):
        pass


class ChecksWidget(QtWidgets.QWidget):


    checksNewFolder_signal = QtCore.pyqtSignal()
    checksNew_signal = QtCore.pyqtSignal('PyQt_PyObject')
    checksDelete_signal = QtCore.pyqtSignal()
    checksImport_signal = QtCore.pyqtSignal()
    checksExport_signal = QtCore.pyqtSignal()
    checksPause_signal = QtCore.pyqtSignal()
    checksRun_signal = QtCore.pyqtSignal('PyQt_PyObject')
    checksStop_signal = QtCore.pyqtSignal()
    pauseChecks_signal = QtCore.pyqtSignal()
    stopChecks_signal = QtCore.pyqtSignal()

    #TODO: Enable Drag&Drop for Tree View

    def __init__(self, systemtype, model = None):
        super().__init__()
        self.logger = logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))
        self.setupUi()
        self.systemType=systemtype
        self.checkHandler = CheckHandler()
        if model is not None:
            self.setModel(model)
        self.show()
        self.saFolderClass=systemcheck.checks.models.Check
        self.actions = OrderedDict()

        for check in self.availableChecks.values():
            description=check.get('description')
            classobj = check.get('saclass')
            self.actions[description] = QtWidgets.QAction(QtGui.QIcon(':Checkmark'), description)
            self.actions[description].triggered.connect(functools.partial(self.on_checkNew, classobj, description))

    def exportChecks(self):
        """ Export all Checks

        Export all checks in yaml format
        """

        result = systemcheck.checks.utils.exportChecks(session=systemcheck.session.SESSION)
        if result.fail:
            systemcheck.gui.utils.message(icon=QtWidgets.QMessageBox.Warning,
                                          title='Checks Export Failed', text=result.message)
        else:
            systemcheck.gui.utils.message(icon=QtWidgets.QMessageBox.Information,
                                          title='Checks Export Successful', text=result.message)

    def importChecks(self):
        """ Import all Checks

        Import all checks in yaml format
        """

        fileName, mask=QtWidgets.QFileDialog.getOpenFileName(self, 'Open Import File', expanduser('~'))

        if fileName is not None:
            result = systemcheck.checks.utils.importChecks(session=systemcheck.session.SESSION)
            if result.fail:
                systemcheck.gui.utils.message(icon=QtWidgets.QMessageBox.Warning,
                                              title='Checks Import', text='Error During Import',
                                              details=result.message)
            else:
                self.checks_model.modelReset.emit()
                self.checks_model.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())
                systemcheck.gui.utils.message(icon=QtWidgets.QMessageBox.Information,
                                              title='Checks Import', text='Checks Import Successful. Please restart the application')


    def setupUi(self):
        vlayout = QtWidgets.QVBoxLayout()
        vlayout.setContentsMargins(0, 0, 0, 0)
        treewidget=QtWidgets.QWidget()
        treewidget.setLayout(vlayout)
        label = QtWidgets.QLabel('Checks:')
        vlayout.addWidget(label)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.setContentsMargins(0,0,0,0)
        hlayout.setSpacing(0)
        self.setWindowTitle('SystemCheck Checks')
        self.setWindowIcon(QtGui.QIcon(':Checked'))
        self.checksTreeAtrributes_splitter = QtWidgets.QSplitter()
        self.checksTreeAtrributes_splitter.setOrientation(QtCore.Qt.Horizontal)
        self.tree = QtWidgets.QTreeView()
        self.tree.setContentsMargins(0, 0, 0, 0)
        self.tree.setHeaderHidden(True)
        self.tree.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.tree.setSortingEnabled(True)
        self.tree.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tree.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tree.header().setStretchLastSection(True)
        vlayout.addWidget(self.tree)
        self.checksTreeAtrributes_splitter.addWidget(treewidget)

        self.checkAttributes_tabw = QtWidgets.QTabWidget()
        self.checksTreeAtrributes_splitter.addWidget(self.checkAttributes_tabw)

        self.checkDescription_widget=systemcheck.checks.gui.widgets.CheckSettingsWidget()
        self.checkAttributes_tabw.addTab(self.checkDescription_widget, 'Generic Configuration')


        self.checkParameters_widget = systemcheck.checks.gui.widgets.CheckParameterEditorWidget()
        self.checkAttributes_tabw.addTab(self.checkParameters_widget, 'Detailed Configuration')
        self.checkAttributes_tabw.setTabEnabled(1, False)
        self.checksTreeAtrributes_splitter.setContentsMargins(0, 0, 0, 0)

        widget=self.checksTreeAtrributes_splitter.widget(0)
        widget.setMaximumWidth(350)

        hlayout.addWidget(self.checksTreeAtrributes_splitter)
        self.setLayout(hlayout)
        self.setupActions()

        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.openContextMenu)

    def setupActions(self):

        self.checksNewFolder_act = QtWidgets.QAction(QtGui.QIcon(':AddFolder'), 'Add Folder')
        self.checksNewFolder_act.triggered.connect(self.on_checkNewFolder)
        self.checksNewFolder_act.setEnabled(True)

        self.checksNew_act = QtWidgets.QAction(QtGui.QIcon(':AddFile'), 'Add New Check...')
        self.checksNew_act.triggered.connect(self.on_checkNew)
        self.checksNew_act.setEnabled(False)

        self.checksDelete_act =  QtWidgets.QAction(QtGui.QIcon(':Trash'), 'Delete Selected Checks')
        self.checksDelete_act.triggered.connect(self.on_checkDelete)
        self.checksDelete_act.setEnabled(True)

        self.checksImport_act = QtWidgets.QAction(QtGui.QIcon(':Import'), 'Import Checks...')
        self.checksImport_act.triggered.connect(self.on_checkImport)
        self.checksImport_act.setEnabled(False)

        self.checksExport_act = QtWidgets.QAction(QtGui.QIcon(':Export'), 'Export Checks...')
        self.checksExport_act.triggered.connect(self.on_checkExport)
        self.checksExport_act.setEnabled(False)

        self.checksRun_act = QtWidgets.QAction(QtGui.QIcon(':Play'), 'Run Checks')
        self.checksRun_act.triggered.connect(self.on_checkRun)
        self.checksRun_act.setEnabled(True)

        self.checksPause_act = QtWidgets.QAction(QtGui.QIcon(':Pause'), 'Pause Checks')
        self.checksPause_act.triggered.connect(self.on_checkPause)
        self.checksPause_act.setEnabled(False)

        self.checksStop_act = QtWidgets.QAction(QtGui.QIcon(':Stop'), 'Stop Checks')
        self.checksStop_act.triggered.connect(self.on_checkPause)
        self.checksStop_act.setEnabled(False)



    @property
    def systemType(self):
        return self.__systemType

    @systemType.setter
    def systemType(self, systemType:str):
        self.__systemType=systemType

    @property
    def availableChecks(self):
        """ Determine the available checks for the context Menu


        """

        available = OrderedDict()
        for plugin in self.checkHandler.pm.getPlugins(category='check', systemtype=self.systemType):
            for saclass in plugin.plugin_object.alchemyObjects:
                if plugin.name==saclass.__name__:
                    available[plugin.name]={'saclass':saclass, 'description':plugin.description}

        return available

    def menu(self):
        menu = QtWidgets.QMenu('&Checks')
        menu.addActions([self.checksNewFolder_act, self.checksNew_act])
        menu.addSeparator()
        menu.addActions([self.checksDelete_act, self.checksImport_act, self.checksExport_act])
        menu.addSeparator()
        menu.addActions([self.checksRun_act, self.checksStop_act, self.checksPause_act])

    def on_tree_selectionChanged(self):
        """ Click on a different Check in the Checks tree

        In this case, the following happens:

            - the clicked SQLAlchemy Node is analyzed. If it has subparameters, a second tab will be displayed.

        """

        print('selection changed')
        current = self.tree.currentIndex()
        node = self.tree.model().getNode(current)

        if node.name != 'RootNode':
            self.checkDescription_widget.setVisible(True)
            self.checkDescription_widget.updateCheck.emit(node, None)
            if hasattr(node, 'params'):
                self.checkAttributes_tabw.setTabEnabled(1, True)
                form = self.checkHandler.parameterForm(node.__class__.__name__)
                self.checkParameters_widget.updateCheck.emit(node, form)
            else:
                self.checkAttributes_tabw.setTabEnabled(1, False)
        else:
            self.checkDescription_widget.setVisible(False)

    def on_checkNew(self, classobject, description):
        """ Create a new Check

        :param classobject: The SQLAlchemy Model that represents the check
        :param description: The description of the check

        """

        if len(self.tree.selectionModel().selectedIndexes())==0:
            parent_index=QtCore.QModelIndex()
        else:
            parent_index = self.tree.currentIndex()


        node=classobject(name='<< {} >>'.format(description))

        self.checks_model.insertRow(position=0, parent=parent_index, nodeObject=node)
        #self.tree.expand(parent_index)

    def getCheckFolderClass(self):
        self.logger.debug('Trying to determine Checks Folder Class')
        self.logger.debug('System Type: %s', self.systemType)



    def on_checkNewFolder(self):
        """ Create a new folder """

        self.logger.debug('Creating new folder')
        self.logger.debug('System Type: %s', self.systemType)

        systemtype=self.systemType.lower().title()
        classname='Action'+systemtype+'Folder'
        self.logger.debug('Folder Class Name: %s', classname)

        folderclass = systemcheck.models.get_class_by_name(class_name=classname, Base=systemcheck.models.meta.Base)

        if len(self.tree.selectionModel().selectedIndexes())==0:
            # That means, somebody right clicked in the white area that doesn't belong to any check
            parent_index=QtCore.QModelIndex()
        else:
            parent_index = self.tree.currentIndex()




        folder = folderclass(name='new Check')


        self.checks_model.insertRow(position=0, parent=parent_index, nodeObject=folder)
        self.tree.expand(parent_index)

    def on_checkDelete(self):
        """ Delete a tree item and all its children """
        index = self.tree.currentIndex()

        if len(self.tree.selectedIndexes()) == 0:
            currentProxyIndex = self.tree.currentIndex()
            currentProxyParentIndex = currentProxyIndex.parent()
            self.system_model.removeRows(row=currentProxyIndex.row(), count=1, parent=currentProxyParentIndex)
        else:
            for index in self.tree.selectedIndexes():
                proxyPoxyParentIndex = index.parent()
                self.checks_model.removeRows(row=index.row(), count=1, parent=proxyPoxyParentIndex)

    def on_checkRun(self, logonInfos:list):
        for info in logonInfos:
            pprint(info)

    def on_checkExport(self):
        self.exportChecks()

    def on_checkImport(self):
        self.importChecks()

    def on_checkStop(self):
        raise NotImplemented

    def on_checkPause(self):
        raise NotImplemented

    def openContextMenu(self, position):

        menu=QtWidgets.QMenu()
        menu = self.systemSpecificContextMenu(position, menu)
        menu.exec_(self.tree.viewport().mapToGlobal(position))

    def setModel(self, checks_model):
        self.checks_model = checks_model
        self.tree.setModel(checks_model)
        self.tree.setColumnHidden(1, True)
        self.tree.setColumnHidden(2, True)
        self.tree.setColumnHidden(3, True)
        self.tree.selectionModel().selectionChanged.connect(self.on_tree_selectionChanged)

    def systemSpecificContextMenu(self, position, menu):
        index = self.tree.indexAt(position)
        node = self.checks_model.getNode(index)

        if node is None:
            menu.addAction(self.checksNewFolder_act)
            menu.addSeparator()
            for action in self.actions.values():
                menu.addAction(action)
        elif type(node).__mapper_args__.get('polymorphic_identity').endswith('Folder') or \
                        type(node).__mapper_args__.get('polymorphic_identity') == 'Check':
            menu.addAction(self.checksNewFolder_act)
            menu.addAction(self.checksDelete_act)
            menu.addSeparator()
            for action in self.actions.values():
                menu.addAction(action)
        else:
            menu.addAction(self.checksDelete_act)

        return menu