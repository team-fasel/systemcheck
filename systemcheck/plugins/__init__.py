from systemcheck.plugins.base_type import BasePlugin
from systemcheck.plugins.action_types import ActionBasePlugin
from systemcheck.plugins.system_type import SystemBasePlugin
from systemcheck.plugins.manager import SysCheckPM
from systemcheck.systems.ABAP.plugins.action_types import CheckAbapFoundationAction


categories = {'check_ABAP':CheckAbapFoundationAction,
              'systems':SystemBasePlugin}

