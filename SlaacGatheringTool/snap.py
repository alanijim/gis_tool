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
this file was taken from CADDigitize plugin
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis._core import QgsVectorLayer, QgsSnapper, QgsGeometry, QgsCoordinateTransform, QgsProject
from qgis._gui import QgsMapTool
from qgis.gui import *
from qgis.core import *

def changegeomSRID(canvas, geom):
    layer = canvas.currentLayer()
    renderer = canvas.mapRenderer()
    layerCRSSrsid = layer.crs().srsid()
    projectCRSSrsid = renderer.destinationCrs().srsid()
    if layerCRSSrsid != projectCRSSrsid:
        g = QgsGeometry.fromPoint(geom)
        g.transform(QgsCoordinateTransform(projectCRSSrsid, layerCRSSrsid))
        retPoint = g.asPoint()
    else:
        retPoint = geom

    return retPoint

def snappedAbility(snap):
    """
    Check if you can snap or not.
    You can if snap != -1 
    """
    if snap == -1:
        return False

    return True

def snappedPoint(canvas, event, returnResultSnapped=False):
    mapTool = QgsMapTool(canvas)
    # get QgsSnappingUtils
    qsu = canvas.snappingUtils()
    #qsu = QgsMapCanvasSnappingUtils(iface.mapCanvas())
    point = mapTool.toMapCoordinates(event.pos())

    #point = changegeomSRID(canvas, currpoint)
#mapTool.toMapCoordinates(qsu.currentLayer(), currpoint))
    snapped = False

    snapper = QgsSnapper(canvas.mapSettings())
    snapper.setSnapMode(0)

    # 3 modes
    # 0 : SnapCurrentLayer, 1 : SnapAllLayers, 2 : SnapAdvanced
    mode = qsu.snapToMapMode()

    if mode == 0:
        g = snapper.SnapLayer()
        g.mLayer = qsu.currentLayer()
        g.mSnapTo, g.mTolerance, g.mUnitType = qsu.defaultSettings()
        g.mSnapTo -= 1 # Off : 0, but enum is normally sommet : 0, segment :1, both : 2

        if snappedAbility(g.mSnapTo):
            snapper.setSnapLayers([g])
            retval, result = snapper.snapMapPoint(point)
            if result != []:
                point = result[0].snappedVertex
                snapped = True

    elif mode == 1:
        allLayers = canvas.layers()
        listSnapLayers = []

        snap, tol, unit = qsu.defaultSettings()
        snap -= 1

        if snappedAbility(snap):
            for i in allLayers:
                if not type(i) is QgsVectorLayer:
                    continue
                g = snapper.SnapLayer()
                g.mLayer = i
                g.mSnapTo, g.mTolerance, g.mUnitType = snap, tol, unit
                listSnapLayers.append(g)

            snapper.setSnapLayers(listSnapLayers)
            retval, result = snapper.snapMapPoint(point)
            if result != []:
                point = result[0].snappedVertex
                snapped = True

    elif mode == 2:
        allLayers = canvas.layers()
        listSnapLayers = []

        for i in allLayers:
            if not type(i) is QgsVectorLayer:
                continue
            (layerid, enabled, snapType, tolUnits, tol, avoidInt) = QgsProject.instance().snapSettingsForLayer(i.id())
            if enabled and snappedAbility(snapType):
                g = snapper.SnapLayer()
                g.mLayer = i
                g.mSnapTo, g.mTolerance, g.mUnitType = snapType, tol, tolUnits
                listSnapLayers.append(g)

        snapper.setSnapLayers(listSnapLayers)
        retval, result = snapper.snapMapPoint(point)
        if result != []:
            point = result[0].snappedVertex
            snapped = True

    return snapped, point

