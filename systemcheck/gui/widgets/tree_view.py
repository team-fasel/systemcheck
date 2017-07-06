from PyQt5 import QtWidgets



class TreeView(QtWidgets.QTreeView):

    def __init__(self):
        super().__init__()

    def updateViewColumnsSetup(self):
        totalColumns = self.model().columnCount()
        print(self.model().hiddenSections())
        self.header().moveSection(0, 3)
        self.header().moveSection(0, 2)
#        self.header().setSectionHidden(2, True)
#        self.header().setSectionHidden(3, True)
