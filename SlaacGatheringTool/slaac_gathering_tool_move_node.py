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
import my_map
import psycopg2
import my_canvas


class SlaacGatheringToolMoveNode(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.nbPoints = 0
        self.rb = myRubberLine(self.canvas)
        self.rb.hide()
        self.rb_snap = myRubberPointSnap(self.canvas)
        self.rb_snap.hide()
        self.nodeToMove = None
        self.point1, self.point2 = None, None
        # our own fancy cursor
        self.cursor = QCursor(QPixmap(["16 16 3 1",
                                       "      c None",
                                       ".     c #FF0000",
                                       "+     c #17a51a",
                                       "                ",
                                       "       +.+      ",
                                       "      ++.++     ",
                                       "     +.....+    ",
                                       "    +.  .  .+   ",
                                       "   +.   .   .+  ",
                                       "  +.    .    .+ ",
                                       " ++.    .    .++",
                                       " ... ...+... ...",
                                       " ++.    .    .++",
                                       "  +.    .    .+ ",
                                       "   +.   .   .+  ",
                                       "   ++.  .  .+   ",
                                       "    ++.....+    ",
                                       "      ++.++     ",
                                       "       +.+      "]))

    def clear(self):
        self.nodeToMove = None
        self.nbPoints = 0
        self.point1, self.point2 = None, None
        self.rb_snap.reset(True)
        self.rb_snap.hide()
        self.rb.reset(True)
        self.rb.hide()

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.clear()
            my_canvas.refreshNodeLayer(self.canvas)
            return

    def canvasPressEvent(self, event):
        layer = self.canvas.currentLayer()
        if self.nbPoints == 0:
            self.rb.show()
        else:
            self.rb.reset(True)
            self.rb.hide()
            my_canvas.refreshNodeLayer(self.canvas)

        snapped, pointMap = snappedPoint(self.canvas, event)

        uri = QgsDataSourceURI(layer.source())
        layerPoint = my_map.transformToCurrentLayerSRID(self.canvas, pointMap)

        nodeId = my_canvas.getSelectedNode(self.canvas, layer, pointMap)
        if self.nbPoints == 0:
            if (nodeId == None):
                QMessageBox.information(None, "Error:", "Please select a valid node")
                return
            self.nodeToMove = nodeId
            self.point1 = pointMap
        else:
            if (nodeId != None):
                QMessageBox.information(None, "Error:", "Please do not put the node on top of another node")
                return
            self.point2 = pointMap

        self.nbPoints += 1

        if self.nbPoints == 2:
            try:
                layerPoint2 = my_map.transformToCurrentLayerSRID(self.canvas, self.point2)
                my_map.attemptMovingNode(uri,self.nodeToMove, layerPoint2.x(), layerPoint2.y())
            except psycopg2.Error as e:
                errors = "Moving Node :\n" + str(e)
                QMessageBox.information(None, "Slaac Gathering Tool", errors)
            self.clear()
            my_canvas.refreshNodeLayer(self.canvas)
        self.rb_snap.reset(True)
        self.rb_snap.hide()

    def canvasMoveEvent(self, event):
        self.rb_snap.reset(True)

        snapped, point = snappedPoint(self.canvas, event)
        if snapped:
            self.rb_snap = myRubberPointSnap(self.canvas)
            self.rb_snap.setToGeometry(QgsGeometry().fromPoint(point), None)
            self.rb_snap.show()
        if self.point1:
            # points = [QgsPoint(self.x1, self.y1), point]
            points = [self.point1, point]
            geom = QgsGeometry.fromPolyline(points)
            self.rb.setToGeometry(geom, None)
            self.rb.show()

    def showSettingsWarning(self):
        pass

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def deactivate(self):
        self.clear()
        my_canvas.refreshNodeLayer(self.canvas)

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True
