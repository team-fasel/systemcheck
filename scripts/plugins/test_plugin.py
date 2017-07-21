from yapsy.IPlugin import IPlugin
import logging

class TestPlugin(IPlugin):

    #def __init__(self):
        #pass

    TYPE = 'ABAP'

    def print_name(self):
        print('This is a test plugin')


    def set_plugin_config(self, Core:dict,
                          Documentation:dict,
                          Parameters:dict,
                          RuntimeParameters:dict,
                          Path:dict):

        self.pluginConfig = dict(Core = Core, Documentation = Documentation, Parameters=Parameters, RuntimeParameters=RuntimeParameters, Path = Path)
        self.logger = logging.getLogger('systemcheck.plugins.CheckPlugin.{}.{}'.format(self.TYPE, self.pluginConfig['Core']['Name']))
