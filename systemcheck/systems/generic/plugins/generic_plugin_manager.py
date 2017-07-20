from systemcheck.utils import Result, Fail, get_absolute_systemcheck_path
from systemcheck.config import CONFIG
from yapsy import PluginManager, PluginInfo
from pprint import pformat
import logging
import sys
import os
from configparser import ConfigParser




class CheckPluginManager(PluginManager):
    """ Manages the the check plugins.

    setupPluginSystem        : initializes the plugin system
    initializeDataModel      : initializes the data models for the plugins.
    executePlugin            : executes a single plugin. GIL is not taken into account.
    executePluginsInParallel : executes a number of plugins in parallel processes. Yields the return
    """

    def __init__(self, pluginFolder):
        super().__init__()
        self.setPluginInfoExtension('syscheck-plugin')
        self.logger=logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))

        checkPluginDir=get_absolute_systemcheck_path(pluginFolder)
        self.setPluginPlaces([checkPluginDir])
        self.locatePlugins()
        self.loadPlugins(callback_after=self.callback_after_load)

    def executePlugin(self, pluginName, logonInfo, sysInfo):
        """ Execute Plugin"""
        self.logger.debug('trying to execute plugin {} on system {}'.format(pluginName, pformat(sysInfo)))

        plugin=self.getPluginByName(pluginName)
        result = plugin.plugin_object.execute_plugin(logonInfo=logonInfo, sysInfo=sysInfo,
                                                     pluginConfigParam=plugin.details)
        if result:
            return result
        else:
            return Fail('Plugin not found')

    # def executePluginsInParallel(self, pluginExecutionInfo, processes=config['pluginsystem'].getint('pluginsystem.parallel_processes')):
    #     self.logger.debug('starting plugins in parallel using {} processes'.format(self.config['pluginsystem']['pluginsystem.parallel_processes']))
    #     pool=Pool(processes)
    #     for x in pool.imap(worker_execute_plugin, pluginExecutionInfo):
    #         yield x

    def callback_after_load(self, pluginInfoObject:PluginInfo):
        """ Callback after loading to initialize the plugin configuration

        The main reason for this callback is the implementation of the custom configurations for plugins. Custom
        configurations will start out with a complete copy of the [Parameters] section. Should an .ini file exist, it
        will become the runtime configuration.

        :param pluginInfoObject: The yapsy plugin info object for the respective plugin

        """

        pluginInfoObject.details.add_section('RuntimeParameters')
        pluginInfoObject.details['RuntimeParameters'] = pluginInfoObject.details['Parameters']
        file = pluginInfoObject.path + '.ini'
        if os.path.exists(file):
            config = ConfigParser()
            config.read(file)
            if config.has_section('Parameters'):
                pluginInfoObject.details['RuntimeParameters'] = config['Parameters']
                pluginInfoObject.plugin_object.set_plugin_config(Core=pluginInfoObject.details['Core'],
                                               Documentation=pluginInfoObject.details['Documentation'],
                                               Parameters=pluginInfoObject.details['Parameters'],
                                               Path=pluginInfoObject.path,
                                               RuntimeParameters=pluginInfoObject.details['RuntimeParameters'])

    @property
    def pluginNames(self):
        result=[]
        for plugin in self.getAllPlugins():
            result.append(plugin.name)
        return result
