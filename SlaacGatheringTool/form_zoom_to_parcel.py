import os

from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox
from qgis.core import QgsDataSourceUri, QgsGeometry

import my_canvas
import my_map

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'FormZoomToParcel.ui'))

class FormZoomToParcel(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, canvas, parent=None):
        """Constructor."""
        super(FormZoomToParcel, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUi you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # https://doc.qt.io/qt-5/designer-using-a-ui-file.html#widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.setFixedSize(self.geometry().width(), self.geometry().height())
        self.pushButtonZoom.clicked.connect(self.zoomToParcel)
        self.canvas = canvas

    def zoomToParcel(self):
        # getParcelExtent
        layerPoint = my_canvas.getNodeLayer(self.canvas)
        uri = QgsDataSourceUri(layerPoint.source())

        barcode = self.lineBarcode.text()
        self.lineBarcode.setText("")
        ret = my_map.getParcelExtent(uri, barcode)
        if ret is None:
            QMessageBox.information(None, "Slaac Gathering Tool", f"Cannot zoom to parcel {barcode}")
        else:
            geom = QgsGeometry.fromWkt(ret)
            geom = my_map.transformToProjectSRID(self.canvas, layerPoint, geom)
            box = geom.boundingBox()
            self.canvas.setExtent(box)
            self.canvas.refresh()
