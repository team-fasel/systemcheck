import logging
from pprint import pprint
from yapsy.PluginManager import PluginManager
from yapsy.IPluginLocator import IPluginLocator

from yapsy.PluginFileLocator import PluginFileLocator
from configparser import ConfigParser
import os



def main():

        manager = PluginManager(plugin_info_ext='syscheck-plugin')
        manager.setPluginPlaces(['plugins'])
        manager.collectPlugins()

        for plugin in manager.getAllPlugins():
            plugin.details.add_section('RuntimeParameters')
            plugin.details['RuntimeParameters'] = plugin.details['Parameters']
            path = plugin.path
            file = path+'.ini'
            if os.path.exists(file):
                config = ConfigParser()
                config.read(file)
                if config.has_section('Parameters'):
                    plugin.details['RuntimeParameters'] = config['Parameters']
            plugin.plugin_object.set_plugin_config(Core=plugin.details['Core'],
                                     Documentation=plugin.details['Documentation'],
                                     Parameters=plugin.details['Parameters'],
                                     Path = plugin.path,
                                     RuntimeParameters=plugin.details['RuntimeParameters'])


if __name__ == '__main__':
    logging.basicConfig(level='DEBUG')
    main()