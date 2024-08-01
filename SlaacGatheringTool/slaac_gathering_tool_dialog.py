# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SlaacGatheringToolDialog
                                 A QGIS plugin
 Slaac Gathering Tool
                             -------------------
        begin                : 2017-05-31
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Herimiaina ANDRIA-NTOANINA, Jimmy ALANI, Joseph MIVULE
        email                : herimiaina@yahoo.ca
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4 import QtGui, uic

from PyQt4.QtGui import QDoubleValidator

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'slaac_gathering_tool_dialog_base.ui'))

class SlaacGatheringToolDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(SlaacGatheringToolDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.setFixedSize(self.geometry().width(), self.geometry().height())
        self.lineEditX.setValidator(QDoubleValidator(0, 100, 7, self))
        self.lineEditY.setValidator(QDoubleValidator(0, 100, 7, self))

        # http://zetcode.com/gui/pyqt4/eventsandsignals/
        self.pushButton1.clicked.connect(self.buttonClicked)
        self.pushButton2.clicked.connect(self.buttonClicked)
        self.pushButton3.clicked.connect(self.buttonClicked)
        self.pushButton4.clicked.connect(self.buttonClicked)
        self.pushButton5.clicked.connect(self.buttonClicked)
        self.pushButton6.clicked.connect(self.buttonClicked)
        self.pushButton7.clicked.connect(self.buttonClicked)
        self.pushButton8.clicked.connect(self.buttonClicked)
        self.pushButton9.clicked.connect(self.buttonClicked)
        self.pushButton0.clicked.connect(self.buttonClicked)
        self.pushButtonMinus.clicked.connect(self.minusClicked)
        self.pushButtonDot.clicked.connect(self.buttonClicked)
        self.pushButtonDel.clicked.connect(self.delClicked)
        self.pushButtonClearX.clicked.connect(self.clearXClicked)
        self.pushButtonClearY.clicked.connect(self.clearYClicked)

    def accept(self):
        if self.lineEditX.text()=="" or self.lineEditY.text()=="":
            QtGui.QMessageBox.information(None, "Error:", "Please insure that both X and Y have values")
            return
        QtGui.QDialog.accept(self)

    def buttonClicked(self):
        sender = self.sender()
        lineEdit = self.lineEditX
        if self.radioButtonY.isChecked():
            lineEdit = self.lineEditY
        try:
            newValue = lineEdit.text() + sender.text()
            float(newValue)
            lineEdit.setText(newValue)
        except ValueError:
            pass

    def delClicked(self):
        lineEdit = self.lineEditX
        if self.radioButtonY.isChecked():
            lineEdit = self.lineEditY
        value = lineEdit.text()
        if len(value)==0:
            return
        lineEdit.setText(value[:-1])

    def minusClicked(self):
        sender = self.sender()
        lineEdit = self.lineEditX
        if self.radioButtonY.isChecked():
            lineEdit = self.lineEditY
        try:
            newValue = lineEdit.text() + "-"
            lineEdit.setText(newValue)
        except ValueError:
            pass

    def clearXClicked(self):
        self.lineEditX.setText("")

    def clearYClicked(self):
        self.lineEditY.setText("")

    def getCoordinates(self):
        return self.lineEditX.text(), self.lineEditY.text()