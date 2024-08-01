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
from qgis._core import QgsGeometry, QgsDataSourceURI
from qgis.core import *
from qgis.gui import *
from snap import *
import my_map
import my_canvas
from rubber import *
import psycopg2

class SlaacGatheringToolAddNode(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)
        self.settings = QSettings()
        self.canvas = canvas
        self.rb_snap = myRubberPointSnap(self.canvas)
        self.rb_snap.hide()
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
        # self.rb_temp = None

    def clear(self):
        self.rb_snap.reset(True)
        self.rb_snap.hide()

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Escape:
            my_canvas.refreshNodeLayer(self.canvas)
            return

    def canvasPressEvent(self, event):
        layer = self.canvas.currentLayer()

        snapped, pointMap = snappedPoint(self.canvas, event)
        # try:
        layerPoint = self.toLayerCoordinates(layer, pointMap)
        uri = QgsDataSourceURI(layer.source())

        try:
            #layerPoint = my_map.transformToLayerSRID(self.canvas, layer, pointMap)
            tolerance = my_canvas.getLayerSearchRadius(self.canvas, layer)
            my_map.addNode(uri, layerPoint.x(), layerPoint.y(), tolerance)
            my_canvas.refreshNodeLayer(self.canvas)
        except psycopg2.Error as e:
            errors = "Add Node:\n" + str(e)
            QMessageBox.information(None, "Slaac Gathering Tool", errors)

    def canvasMoveEvent(self, event):
        self.rb_snap.reset(True)
        snapped, point = snappedPoint(self.canvas, event)
        if snapped:
            self.rb_snap = myRubberPointSnap(self.canvas)
            self.rb_snap.setToGeometry(QgsGeometry().fromPoint(point), None)
            self.rb_snap.show()

    def showSettingsWarning(self):
        pass

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def deactivate(self):
        my_canvas.refreshNodeLayer(self.canvas)

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True
