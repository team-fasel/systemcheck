from systemcheck.utils import get_absolute_systemcheck_path
from systemcheck.config import CONFIG
from yapsy.PluginManager import  PluginManager
import logging
from pprint import pformat

class CheckPluginManager(PluginManager):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.setPluginInfoExtension('syscheck-plugin')

        locations=[]

        for section in CONFIG:
            if section.startswith('systemtype_'):
                location = CONFIG[section].get('pluginlocation')
                if location:
                    abs_location=get_absolute_systemcheck_path(location)
                    locations.append(abs_location)
        self.setPluginPlaces(locations)
        self.collectPlugins()

