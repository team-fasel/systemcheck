from systemcheck import  CONFIG, SESSION
from systemcheck.gui.widgets.credentials import CredentialsEditor
from PyQt5 import QtWidgets



if __name__ == '__main__':
    import sys
    from pprint import pprint
    app=QtWidgets.QApplication(sys.argv)
    app.setStyle('plastique')

    editor = CredentialsEditor()

    sys.exit(app.exec_())
