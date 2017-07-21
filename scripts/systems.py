import systemcheck

from PyQt5 import QtWidgets, QtCore, Qt
from systemcheck.session import SESSION
from systemcheck.systems.ABAP.gui.widgets import AbapSystemsWidget
from systemcheck.systems.ABAP.models import AbapTreeNode
from systemcheck.systems.ABAP.gui.models import AbapTreeModel

import sys
sys._excepthook = sys.excepthook


def exception_hook(exctype, value, traceback):
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


if __name__ == '__main__':
    import logging

    logging.basicConfig(level='DEBUG')


    from pprint import pprint
    app=QtWidgets.QApplication(sys.argv)
    #app.setStyle('plastique')

    rootnode=SESSION.query(AbapTreeNode).filter_by(parent_id=None).first()
    pprint(rootnode._dump())

    model=AbapTreeModel(rootnode)
    systems=AbapSystemsWidget(model)
    systems.show()

    sys.exit(app.exec_())
