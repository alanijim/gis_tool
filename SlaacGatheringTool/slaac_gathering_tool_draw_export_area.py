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
from qgis._core import QgsGeometry, QgsMessageLog, QgsFeature
from qgis._gui import QgsMapTool
from qgis.core import *
from qgis.gui import *
from snap import *
from rubber import *
import my_map
import my_canvas
import psycopg2
import uuid

class SlaacGatheringToolDrawExportArea(QgsMapTool):
    def __init__(self, iface, canvas):
        self.iface = iface
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.rb = myRubberPolygon(self.canvas)
        self.rb.hide()
        self.rb_snap = myRubberPointSnap(self.canvas)
        self.rb_snap.hide()
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
        self.rb_snap.reset(QGis.Point)
        self.rb_snap.hide()
        self.rb.reset(QGis.Polygon)
        self.rb.hide()

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.clear()
            self.canvas.refresh()
            return

    def canvasPressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.rb.removePoint(-2)
            self.rb.show()
            return

        snapped, pointMap = snappedPoint(self.canvas, event)
        # This second one is the point to move when the cursor is moving
        if self.rb.numberOfVertices() == 0:
            self.rb.addPoint(pointMap)
        self.rb.addPoint(pointMap)
        self.rb.update()

    def canvasDoubleClickEvent(self, event):
        nb_vertices = self.rb.numberOfVertices()
        if nb_vertices > 3:
            mc = self.canvas
            layer = mc.currentLayer()
            renderer = mc.mapSettings()
            layerCRSSrsid = layer.crs().srsid()
            projectCRSSrsid = renderer.destinationCrs().srsid()
            f = QgsFeature()
            self.rb.removeLastPoint()
            geom = self.rb.asGeometry()
            if layerCRSSrsid != projectCRSSrsid:
                geom.transform(QgsCoordinateTransform(projectCRSSrsid, layerCRSSrsid))

            f.setGeometry(geom)
            # add attribute fields to feature
            fields = layer.pendingFields()

            # vector api change update
            provider = layer.dataProvider()
            f.initAttributes(fields.count())
            for i in range(fields.count()):
                f.setAttribute(i, provider.defaultValue(i))
            
            idx = layer.fieldNameIndex('guid')
            f.setAttribute(idx, str(uuid.uuid1()))

            layer.dataProvider().addFeatures([f])
            my_canvas.refreshLayer(self.canvas,layer)
        self.clear()

    def canvasMoveEvent(self, event):
        nb_vertices = self.rb.numberOfVertices()
        #QgsMessageLog.logMessage("Nbr Vertices " + str(nb_vertices), level=QgsMessageLog.WARNING)

        snapped, point = snappedPoint(self.canvas, event)
        self.rb.show()
        self.rb_snap.setToGeometry(QgsGeometry().fromPoint(point), None)
        self.rb_snap.show()
        if nb_vertices > 0:
            self.rb.movePoint(nb_vertices - 1,point)

    def showSettingsWarning(self):
        pass

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def deactivate(self):
        self.clear()
        my_canvas.refreshExportLayer(self.canvas)

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True
