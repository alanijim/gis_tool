# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CADDigitize
                                 A QGIS plugin
 CAD like tools for QGis
 Fork of Rectangles Ovals Digitizing. Inspired by CadTools, LibreCAD/AutoCAD.
                              -------------------
        begin                : 2015-24-09
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Loïc BARTOLETTI
        email                : l.bartoletti@free.fr
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
from qgis._core import QgsPoint, QGis
from qgis._gui import QgsVertexMarker, QgsRubberBand
from qgis.gui import *
from qgis.core import *
from PyQt4.QtGui import *
from PyQt4.QtCore import QSettings

def getQgisDigitizingColor():
    r = QSettings().value("/qgis/digitizing/line_color_red", 255, type=int)
    g = QSettings().value("/qgis/digitizing/line_color_green", 0, type=int)
    b = QSettings().value("/qgis/digitizing/line_color_blue", 0, type=int)
    a = QSettings().value("/qgis/digitizing/line_color_alpha", 200, type=int)

    return QColor(r,g,b,a)

def myRubberLine(canvas):
    w = QSettings().value("/qgis/digitizing/line_width", 1, type=int)

    rb = QgsRubberBand(canvas, False)
    rb.setColor(getQgisDigitizingColor())
    rb.setWidth(w)

    return rb

def myRubberPointSnap(canvas):
    w = QSettings().value("/qgis/digitizing/line_width", 1, type=int)
    rb = QgsRubberBand(canvas, QGis.Point)
    rb.setColor(getQgisDigitizingColor())
    rb.setWidth(w)
    rb.setIcon(2)
    return rb

def myVertexMarker(canvas):
    m = QgsVertexMarker(canvas)
    m.setCenter(QgsPoint(0, 0))
    m.setColor(QColor(255, 255, 0))
    m.setIconSize(20)
    m.setIconType(QgsVertexMarker.ICON_X)  # or ICON_CROSS, ICON_X
    m.setPenWidth(2)
    m.hide()
    return m

def myRubberPolygon(canvas):
    w = QSettings().value("/qgis/digitizing/line_width", 1, type=int)

    rb = QgsRubberBand(canvas, QGis.Polygon)
    rb.setColor(getQgisDigitizingColor())
    rb.setWidth(w)

    return rb