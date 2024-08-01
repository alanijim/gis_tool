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
from qgis._core import QgsDataSourceURI
from qgis.core import *
from qgis.gui import *
from snap import *
from rubber import *
import my_map
import my_canvas
import psycopg2
import math


class SlaacGatheringToolAddNodeAtIntersection(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.nbEdges = 0
        self.rb = myRubberLine(self.canvas)
        self.rb.hide()
        self.rb_edge_1 = myRubberLine(self.canvas)
        self.rb_edge_1.hide()
        self.edge1, self.edge2 = None, None
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
        self.nbEdges = 0
        self.edge1, self.edge2 = None, None
        self.rb.reset(True)
        self.rb.hide()
        self.rb_edge_1.reset(True)
        self.rb_edge_1.hide()
    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.clear()
            my_canvas.refreshNodeLayer(self.canvas)
            return

    def canvasPressEvent(self, event):
        edge, edge_feature = self.drawProjectedLine(self.rb_edge_1, event)

        if edge == None:
            self.edge1 = None

            return

        if self.edge1 == None:
            self.edge1 = edge
            return

        uri = QgsDataSourceURI(self.canvas.currentLayer().source())
        try:
            nodeId = my_map.addNodeAtIntersection(uri, self.edge1, edge)
            if nodeId == None:
                raise Exception("No intersection was found")
            my_canvas.refreshNodeLayer(self.canvas)
        except psycopg2.Error as e:
            errors = "Adding Node at intersection:\n" + str(e)
            QMessageBox.information(None, "Slaac Gathering Tool", errors)
        except Exception as e:
            errors = "Adding Node at intersection:\n" + str(e)
            QMessageBox.information(None, "Slaac Gathering Tool", errors)

        self.clear()
        # Make the point at the intersection

    def getExtendedLine(self, point1, point2, length):
        """
        :param point1: point in layer coordinate
        :param point2: targeted point in layer coordinate
        :param length: length to be extended
        :return: polyline
        """
        vector_x, vector_y = point2.x() - point1.x(), point2.y() - point1.y()
        current_length = math.sqrt(vector_x**2 + vector_y**2)
        ratio = length / current_length
        vector_x, vector_y = vector_x * ratio, vector_y * ratio
        point3 = QgsPoint(point1.x()+vector_x,point1.y()+vector_y)
        return QgsGeometry.fromPolyline([point1,point3])
    def getSimplifiedDistance(self, point1, point2):
        return (point2.x() - point1.x())**2 + (point2.y()-point1.y())**2
    def drawProjectedLine(self,rubber_to_change, event):
        """
        :param rubber_to_change: the rubber
        :return: nothing
        """
        layer = self.canvas.currentLayer()

        snapped, pointMap = snappedPoint(self.canvas, event)
        uri = QgsDataSourceURI(layer.source())

        edge_feature = my_canvas.getSelectedFeature(self.canvas, layer, pointMap)
        if edge_feature == None:
            rubber_to_change.hide()
            return None, None
        polyline = edge_feature.geometry().asPolyline()
        # to layer coordinates
        point1 = polyline[0]
        point2 = polyline[1]
        pointLayer = my_map.transformToLayerSRID(self.canvas, layer, pointMap)

        if self.getSimplifiedDistance(point1, pointLayer) < self.getSimplifiedDistance(point2, pointLayer):
            temp = point2
            point2 = point1
            point1 = temp

        length = my_canvas.getPixelToDistance(self.canvas, layer, 1024)
        lineToDraw = self.getExtendedLine(point1, point2, length)
        rubber_to_change.setToGeometry(lineToDraw, layer)
        rubber_to_change.show()
        return lineToDraw.asPolyline(), edge_feature
    def canvasMoveEvent(self, event):
        self.drawProjectedLine(self.rb, event)
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
