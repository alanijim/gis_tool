# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SlaacGatheringTool
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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis._core import QgsDataSourceURI
from qgis._gui import QgsMapTool
from qgis.core import *
from qgis.gui import *
import time
import my_map
import my_canvas
from form_context_dialog import *
from rubber import *
import psycopg2

class SlaacGatheringToolForms(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)
        self.settings = QSettings()
        self.canvas = canvas
        # our own fancy cursor
        self.cursor = QCursor(QPixmap(["16 16 3 1",
                                       "      c None",
                                       ".     c #FF0000",
                                       "+     c #1210f3",
                                       "                ",
                                       "       +.+      ",
                                       "      ++.++     ",
                                       "     +.....+    ",
                                       "    +.     .+   ",
                                       "   +.   .   .+  ",
                                       "  +.    .    .+ ",
                                       " ++.    .    .++",
                                       " ... ...+... ...",
                                       " ++.    .    .++",
                                       "  +.    .    .+ ",
                                       "   +.   .   .+  ",
                                       "   ++.     .+   ",
                                       "    ++.....+    ",
                                       "      ++.++     ",
                                       "       +.+      "]))

        self.dlg = FormContextDialog()

    def clear(self):
        pass

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Escape:
            my_canvas.refreshFormLayer(self.canvas)
            return

    def canvasPressEvent(self, event):
        layer = self.canvas.currentLayer()
        pointMap = self.toMapCoordinates(event.pos())
        layerPoint = self.toLayerCoordinates(layer, pointMap)


        nodeLayer = my_canvas.getNodeLayer(self.canvas)
        uri = QgsDataSourceURI(nodeLayer.source())
        toponame = str(uri.schema())

        srid = layer.crs().authid()[5:]

        try:
            formId = my_map.insertForm(uri, layerPoint.x(), layerPoint.y(),srid)
            self.dlg.setFormId(formId)
            self.dlg.my_init(self.canvas)
            self.dlg.exec_()
            time.sleep(1)

            my_canvas.refreshFormLayer(self.canvas)
        except psycopg2.Error as e:
            errors = "Handling Forms:\n" + str(e)
            QMessageBox.information(None, "Slaac Gathering Tool", errors)

    def canvasMoveEvent(self, event):
        pass

    def showSettingsWarning(self):
        pass

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def deactivate(self):
        my_canvas.refreshFormLayer(self.canvas)

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True
