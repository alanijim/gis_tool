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
from qgis.core import *
from qgis.gui import *
from snap import *
from rubber import *
import my_canvas
import my_map
import psycopg2

class SlaacGatheringToolSplitEdge(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self,canvas)
        self.settings = QSettings()
        self.canvas=canvas
        self.rb_snap = myRubberPointSnap(self.canvas)
        self.rb_snap.hide()
        #our own fancy cursor
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
        #self.rb_temp = None
    def clear(self):
        self.rb_snap.reset(True)
        self.rb_snap.hide()
    def keyReleaseEvent(self,  event):
        if event.key() == Qt.Key_Escape:
            my_canvas.refreshEdgeLayer(self.canvas)
            return

    def canvasPressEvent(self,event):
        layer = self.canvas.currentLayer()
        
        snapped, pointMap = snappedPoint(self.canvas, event)
        edge_id = my_canvas.getSelectedEdge(self.canvas, layer, pointMap)
        if not edge_id:
            QMessageBox.information(None, "Error:", "Please select a point within a edge" ) 
            return
        #try:
        pointMap = self.toLayerCoordinates(layer, pointMap)
        uri = QgsDataSourceURI(layer.source())
        my_map.createNodeBySplitingEdge(uri,edge_id,pointMap.x(),pointMap.y())

        my_canvas.refreshEdgeLayer(self.canvas)
        my_canvas.refreshNodeLayer(self.canvas)
        
    def canvasMoveEvent(self,event):
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
        my_canvas.refreshEdgeLayer(self.canvas)

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True
