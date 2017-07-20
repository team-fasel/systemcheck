

# define authorship information
__authors__     = ['Lars Fasel']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2017'
__license__     = 'MIT'

# maintanence information
__maintainer__  = 'Lars Fasel'
__email__       = 'systemcheck@team-fasel.com'


from systemcheck.systems.generic.gui.models import GenericTreeModel
from systemcheck.systems.ABAP.models import AbapTreeNode

class AbapTreeModel(GenericTreeModel):

    def __init__(self, rootnode, parent=None):
        super().__init__(rootnode, parent=None)
        self._treeNode = AbapTreeNode
