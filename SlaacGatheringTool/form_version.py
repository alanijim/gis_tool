import os
from PyQt5 import QtWidgets, uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'FormVersion.ui'))

class FormVersion(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(FormVersion, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUi you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # https://doc.qt.io/qt-5/designer-using-a-ui-file.html#widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.setFixedSize(self.geometry().width(), self.geometry().height())
        self.lineVersion.setText("2018-12-15 11:53:12.396000")
