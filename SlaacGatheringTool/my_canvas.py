import psycopg2
from qgis.core import QgsRectangle, QgsDataSourceUri, QgsFeatureRequest, QgsGeometry, QgsWkbTypes
from qgis.gui import QgsMapTool
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QPoint

# -*- coding: utf-8 -*-
"""
Created on Sat Jul  8 14:50:47 2017

@author: herimiaina
"""

def refreshLayer(canvas, layer):
    if canvas.isCachingEnabled():
        if layer:
            layer.setCacheImage(None)
    else:
        canvas.refresh()

def getExportLayer(canvas):
    for layer in canvas.layers():
        uri = QgsDataSourceUri(layer.source())
        if layer.providerType() == 'postgres' and \
            uri.table() == 'export_area' and uri.schema() == 'public' \
                and layer.wkbType() == QgsWkbTypes.Polygon and layer.name() == 'to export':
            return layer
    return None

def getImportedLayer(canvas):
    for layer in canvas.layers():
        uri = QgsDataSourceUri(layer.source())
        if layer.providerType() == 'postgres' and \
            uri.table() == 'import_log' and uri.schema() == 'public':
            return layer
    return None

def getLockedLayer(canvas):
    for layer in canvas.layers():
        uri = QgsDataSourceUri(layer.source())
        if layer.providerType() == 'postgres' and \
            uri.table() == 'export_area' and uri.schema() == 'public' \
                and layer.wkbType() == QgsWkbTypes.Polygon and layer.name() == 'locked area':
            return layer
    return None

def getFormLayer(canvas):
    for layer in canvas.layers():
        uri = QgsDataSourceUri(layer.source())
        if layer.providerType() == 'postgres' and \
            uri.table() == 'forms' and uri.schema() == 'public' \
                and layer.wkbType() == QgsWkbTypes.Point:
            return layer
    return None

def getEdgeLayer(canvas):
    for layer in canvas.layers():
        uri = QgsDataSourceUri(layer.source())
        if layer.providerType() == 'postgres' and \
            uri.table() == 'edge_data' and uri.schema() == 'uganda' \
                and layer.wkbType() == QgsWkbTypes.LineString:
            return layer
    return None

def getNodeLayer(canvas):
    for layer in canvas.layers():
        uri = QgsDataSourceUri(layer.source())
        if layer.providerType() == 'postgres' and \
            uri.table() == 'node' and uri.schema() == 'uganda' \
                and layer.wkbType() == QgsWkbTypes.Point:
            return layer
    return None

def getPixelToDistance(canvas, layer, pixel):
    point1 = QPoint(0, 0)
    point2 = QPoint(pixel, 0)
    mapTool = QgsMapTool(canvas)
    map_point1 = mapTool.toLayerCoordinates(layer, point1)
    map_point2 = mapTool.toLayerCoordinates(layer, point2)
    return abs(map_point1.x() - map_point2.x())

PIXEL_TOL = 10

def getSearchRadius(canvas):
    point1 = QPoint(0, 0)
    point2 = QPoint(PIXEL_TOL, PIXEL_TOL)
    mapTool = QgsMapTool(canvas)
    map_point1 = mapTool.toMapCoordinates(point1)
    map_point2 = mapTool.toMapCoordinates(point2)
    return abs(map_point1.x() - map_point2.x())

def getLayerSearchRadius(canvas, layer):
    point1 = QPoint(0, 0)
    point2 = QPoint(PIXEL_TOL, PIXEL_TOL)
    mapTool = QgsMapTool(canvas)
    map_point1 = mapTool.toLayerCoordinates(layer, point1)
    map_point2 = mapTool.toLayerCoordinates(layer, point2)
    return abs(map_point1.x() - map_point2.x())

def getSelectedFeature(canvas, layer, pointMap):
    searchRadius = getSearchRadius(canvas)

    rect = QgsRectangle()
    rect.setXMinimum(pointMap.x() - searchRadius)
    rect.setYMinimum(pointMap.y() - searchRadius)
    rect.setXMaximum(pointMap.x() + searchRadius)
    rect.setYMaximum(pointMap.y() + searchRadius)

    mapTool = QgsMapTool(canvas)
    rect = mapTool.toLayerCoordinates(layer, rect)
    rq = QgsFeatureRequest(rect)
    rq.setFlags(QgsFeatureRequest.ExactIntersect)
    f = None
    try:
        f = next(layer.getFeatures(rq))
    except StopIteration:
        return None
    return f

def getSelectedFeatureId(canvas, layer, pointMap, field):
    f = getSelectedFeature(canvas, layer, pointMap)
    if f is None: return None
    return f[field]

def getSelectedEdge(canvas, layer, pointMap):
    return getSelectedFeatureId(canvas, layer, pointMap, 'edge_id')

def getSelectedNode(canvas, layer, pointMap):
    return getSelectedFeatureId(canvas, layer, pointMap, 'node_id')

def refreshEdgeLayer(canvas):
    edge_layer = getEdgeLayer(canvas)
    refreshLayer(canvas, edge_layer)
    refreshInconsistencies(canvas)

def refreshNodeLayer(canvas):
    layer = getNodeLayer(canvas)
    refreshLayer(canvas, layer)
    refreshInconsistencies(canvas)

def refreshExportLayer(canvas):
    layer = getExportLayer(canvas)
    refreshLayer(canvas, layer)

def refreshLockedLayer(canvas):
    layer = getLockedLayer(canvas)
    refreshLayer(canvas, layer)

def refreshFormLayer(canvas):
    layer = getFormLayer(canvas)
    refreshLayer(canvas, layer)
    refreshInconsistencies(canvas)

def refreshInconsistencies(canvas):
    table_name = ['node_hanging', 'forms_without_parcels', 'edge_hanging', 'parcels_without_form']
    temp = [layer for layer in canvas.layers() if layer.providerType() == 'postgres' and \
            QgsDataSourceUri(layer.source()).table() in table_name and QgsDataSourceUri(layer.source()).schema() == 'public']
    for layer in temp:
        refreshLayer(canvas, layer)
