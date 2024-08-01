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
from qgis._gui import QgsMapTool
from qgis.core import *
from qgis.gui import *
import my_canvas
import my_war
import webbrowser
from rubber import *

class SlaacGatheringToolSolveProblem(QgsMapTool):
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
        if feature:
            self.exportArea(export_layer, feature)
            return

        locked_layer = my_canvas.getLockedLayer(self.canvas)
        locked_feature = my_canvas.getSelectedFeature(self.canvas,locked_layer,point_map)
        if locked_feature:
            self.reExportArea(locked_feature)
            return
        QMessageBox.information(None, "Slaac Gathering Tool", \
                                "Please select an area 'to be exported' or an area 'to export again' ")


    def exportArea(self, export_layer, feature):
        reply = QMessageBox.question(None, "Slaac Gathering Tool", "Once started, the problem solver" + \
                                                                   " will lock the form and cannot be cancelled. Please confirm",
                                     QMessageBox.Yes, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        to_open = my_war.get_default_path(self.canvas) + "/solve/" + str(feature.id())
        webbrowser.open(to_open)

        idx = export_layer.fieldNameIndex('exported')
        attr = {idx: 'exported'}
        export_layer.dataProvider().changeAttributeValues({feature.id(): attr})

        my_canvas.refreshExportLayer(self.canvas)
        my_canvas.refreshLockedLayer(self.canvas)

    def reExportArea(self, locked_feature):
        to_open = my_war.get_default_path(self.canvas) + "/solve/" + str(locked_feature.id())
        webbrowser.open(to_open)

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
