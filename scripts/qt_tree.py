from PyQt5 import QtWidgets, QtCore, Qt
from systemcheck.session import SESSION
from systemcheck.systems.ABAP.gui.models import AbapTreeModel
from systemcheck.gui.widgets import TreeView
from systemcheck.systems.ABAP.models.abap_model import AbapTreeNode

if __name__ == '__main__':
    import sys
    from pprint import pprint
    app=QtWidgets.QApplication(sys.argv)
    app.setStyle('plastique')

    rootnode=SESSION.query(AbapTreeNode).filter_by(parent_id=None).one()
    pprint(rootnode._dump())

    model=AbapTreeModel(rootnode)
    treeView=QtWidgets.QTreeView()
    treeView.show()
    treeView.setModel(model)


    sys.exit(app.exec_())
