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

class SlaacGatheringToolRemoveExportArea(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)
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

    def clear(self):
        pass

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Escape:
            my_canvas.refreshExportLayer(self.canvas)
            return

    def canvasPressEvent(self, event):
        export_layer = my_canvas.getExportLayer(self.canvas)
        point_map = self.toMapCoordinates(event.pos())

        feature = my_canvas.getSelectedFeature(self.canvas,export_layer,point_map)
        if not feature:
            QMessageBox.information(None, "Slaac Gathering Tool", "Please select an area 'to be exported' to delete")
            return

        export_layer.dataProvider().deleteFeatures([feature.id()])
        my_canvas.refreshExportLayer(self.canvas)

    def canvasMoveEvent(self, event):
        pass

    def showSettingsWarning(self):
        pass

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def deactivate(self):
        my_canvas.refreshExportLayer(self.canvas)

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True
