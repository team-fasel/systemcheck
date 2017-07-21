from PyQt5 import QtWidgets, QtCore, Qt
from systemcheck import SESSION
from systemcheck.gui.models import CredentialModel
from systemcheck.gui.widgets import TreeView
from systemcheck.systems.ABAP.models.abap_model import AbapTreeNode

if __name__ == '__main__':
    import sys
    from pprint import pprint
    app=QtWidgets.QApplication(sys.argv)
    app.setStyle('plastique')

    model=CredentialModel()
    table=QtWidgets.QTableView()
    table.show()
    table.setModel(model)


    sys.exit(app.exec_())
