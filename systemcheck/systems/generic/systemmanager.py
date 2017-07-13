from PyQt5 import QtCore, QtWidgets
from systemcheck import SESSION
from typing import Any

class SystemManager:
    """ A Generic Class to manage all types of systems for the systemcheck application
    """

    TYPE = 'GENERIC'

    def __init__(self):
        pass

    def system(self, id):
        pass

    def connection_to(self, saobject:Any, credentials:dict =None):
        """ Attempts to connect to the system and returns the connection

        :param saobject: A SQLAlchemy Object
        """

        raise NotImplemented

    def all_systems(self):
        """ Return all systems """
        pass

