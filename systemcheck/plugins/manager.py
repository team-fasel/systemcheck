import systemcheck
from systemcheck.config import CONFIG
from systemcheck.utils import get_absolute_systemcheck_path
from pprint import pprint
from yapsy.PluginManager import PluginManager


class SysCheckPM(PluginManager):

    def __init__(self):
        super().__init__()
        self.setPluginInfoExtension('syscheck-plugin')
        self.setCategoriesFilter(systemcheck.plugins.categories)


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
