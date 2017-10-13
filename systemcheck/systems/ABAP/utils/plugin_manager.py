from systemcheck.plugins import SysCheckPM
import os
from configparser import ConfigParser
import logging

from systemcheck.config import CONFIG
from systemcheck.utils import get_absolute_systemcheck_path, Result, Fail

class CheckPluginManager:
    """ The Plugin Manager of the SystemCheck Tool


    """

    TYPE = 'ABAP'

    def __init__(self):
        self.logger = logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))
        self.pm = SysCheckPM()



        for plugin in self.pm.pm.getAllPlugins():
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


        def plugin_count()->int:
            """ Returns the number of plugins """
            count = len(self.pm.pm.getAllPlugins())
            self.logger.debug('Identified %i plugins', count)
            return count

