import systemcheck
from systemcheck.config import CONFIG
from systemcheck.utils import get_absolute_systemcheck_path
from yapsy.PluginManager import PluginManager
from pprint import pprint
import logging
from pprint import pformat

class SysCheckPM(PluginManager):

    def __init__(self):

        super().__init__()
        self.logger=logging.getLogger(self.__class__.__name__)
        self.setPluginInfoExtension('syscheck-plugin')
#        self.setCategoriesFilter(systemcheck.plugins.categories)
        locations = []

        for section in CONFIG:
            if section.startswith('systemtype_'):
                location = CONFIG[section].get('pluginlocation')
                if location:
                    abs_location = get_absolute_systemcheck_path(location)
                    locations.append(abs_location)

        self.setPluginPlaces(locations)
        self.locatePlugins()
        self.collectPlugins()

    def getPlugins(self, category=None, systemtype=None):
        """ Get Plugins


        :param category: The plugin category as specified in the class variable CATEGORY
        :param systemtype: the system type as specified in the class variable SYSTEMTYPE


        """

        if category is None and systemtype is None:
            self.logger.debug('looking for plugins of all categories for any system type')
            return self.getAllPlugins()

        result=[]

        #return the plugins of the specified category for the specified system type
        if category and systemtype:
            self.logger.debug('looking for plugins of category %s for system type %s', category, systemtype)
            for plugin in self.getAllPlugins():
                if plugin.plugin_object.category==category and plugin.plugin_object.systemType==systemtype:
                    result.append(plugin)
        # Return all plugins for the specific system type
        elif category is None and systemtype is not None:
            self.logger.debug('looking for plugins of any category for system type', systemtype)
            for plugin in self.getAllPlugins():
                if plugin.plugin_object.systemType==systemtype:
                    result.append(plugin)

        # Return the plugins of a category for all system types
        elif category is not None and systemtype is None:
            self.logger.debug('looking for plugins any category for system type %s', systemtype)
            for plugin in self.getAllPlugins():
                if plugin.plugin_object.category==category:
                    result.append(plugin)

        self.logger.debug('Identified plugins:')
        for plugin in result:
            self.logger.debug(' -'+plugin.name)
        return result

    def getPlugin(self, name):
        """ Get Plugins


        :param category: The plugin category as specified in the class variable CATEGORY
        :param systemtype: the system type as specified in the class variable SYSTEMTYPE


        """

        for plugin in self.getAllPlugins():
            if plugin.name==name:
                return plugin

        return None