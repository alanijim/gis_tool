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
import webbrowser

from PyQt5 import QtWidgets, uic
import my_war

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'FormContextDialogBase.ui'))

class FormContextDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(FormContextDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect

        self.setupUi(self)
        self.setFixedSize(self.geometry().width(), self.geometry().height())

        self.pushButtonCaptureData.clicked.connect(self.captureDataClicked)
        self.pushButtonTakePicture.clicked.connect(self.takePictureClicked)
        self.pushButtonDeleteData.clicked.connect(self.deletedDataClicked)
        self.pushButtonLinkBarcode.clicked.connect(self.linkBarcodeClicked)
        self.pushButtonCancel.clicked.connect(self.cancelClicked)
        
        self.canvas = None
        self._base_url = None
        self._camera_base_url = None
        self._tracking_url = None
        
    def my_init(self, canvas):
        default_url = my_war.get_default_path(canvas)
        self._applicant_base_url = default_url + "/persons/list/"
        self._base_url = default_url + "/formses/"
        self._camera_base_url = default_url + "/camera/"
        self._tracking_url = default_url + "/tracking/"
        
    @property
    def form_id(self):
        return self._form_id

    def setFormId(self, form_id):
        self._form_id = form_id

    def captureDataClicked(self):
        url = self._applicant_base_url + str(self.form_id)
        webbrowser.open(url)
        self.accept()

    def takePictureClicked(self):
        url = self._camera_base_url + str(self.form_id)
        webbrowser.open(url)
        self.accept()

    def deletedDataClicked(self):
        url = self._base_url + "remove?form=" + str(self.form_id)
        webbrowser.open(url)
        self.accept()

    def cancelClicked(self):
        self.accept()

    def linkBarcodeClicked(self):
        url = self._tracking_url + "linkForm/" + str(self.form_id)
        webbrowser.open(url)
        self.accept()
