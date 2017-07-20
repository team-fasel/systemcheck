from systemcheck.config import CONFIG
import getpass
import re

def get_snc_name()->str:
    """ Generate SNC Name
    The template is stored in parameter snc.name_template in section abap_functions.
    """

    username=getpass.getuser()

    if CONFIG['systemtype_ABAP']['snc.username_case']=='upper':
        username=username.upper()
    elif CONFIG['systemtype_ABAP']['snc.username_case']=='lower':
        username=username.lower()

    sncTemplate = CONFIG['systemtype_ABAP']['snc.user_template']
    sncTemplate = sncTemplate.replace('{{username}}', username)
    searchstring = '{{.*}}'
    stringlist = re.findall(searchstring, sncTemplate)
    for string in stringlist:
        config_string = string.replace('{{', '').replace('}}', '')
        sncTemplate = sncTemplate.replace(string, CONFIG['systemtype_ABAP'][config_string])

    return sncTemplate


