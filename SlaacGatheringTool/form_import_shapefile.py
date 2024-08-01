import os
from PyQt5 import QtWidgets, uic
import psycopg2
from PyQt5.QtWidgets import QMessageBox
from qgis.core import QgsFeatureRequest, QgsRectangle, QgsPointXY, QgsDataSourceUri, QgsGeometry, QgsCoordinateTransform, QgsWkbTypes

import my_map
import my_canvas
import profile

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'FormImportShapefile.ui'))

class FormImportShapefile(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self, parent=None):
        """Constructor."""
        super(FormImportShapefile, self).__init__(parent)
        self.setupUi(self)
        self.setFixedSize(self.geometry().width(), self.geometry().height())
        self.btnImport.clicked.connect(self.importClicked)

    def myExec(self, canvas):
        self.parcelsLayerList = []
        self.comboBox.clear()
        self.node_layer = my_canvas.getNodeLayer(canvas)
        self.node_uri = QgsDataSourceUri(self.node_layer.source())
        self.edge_layer = my_canvas.getEdgeLayer(canvas)
        self.edge_uri = QgsDataSourceUri(self.edge_layer.source())
        self.canvas = canvas
        for layer in canvas.layers():
            if layer.geometryType() != QgsWkbTypes.PolygonGeometry:
                continue
            if "slaac_gathering_tool" in str(layer.source()).lower():
                continue
            self.comboBox.addItem(layer.name())
            self.parcelsLayerList.append(layer)
        self.exec_()

    def transformToLayerSRID(self, transformation, geomSrc):
        g = QgsGeometry.fromPointXY(QgsPointXY(geomSrc.x(), geomSrc.y()))
        g.transform(transformation)
        return g.asPoint()

    def getNodeByPoint(self, cur, toponame, srid, tolerance, x, y):
        cur.execute("SELECT topology.GetNodeByPoint(%s, ST_GeomFromText('POINT(%s %s)', %s), %s) As nodeId",
                    (toponame, x, y, srid, tolerance))
        return cur.fetchone()[0]

    def add_node(self, cur, toponame, srid, tolerance, point):
        id = self.getNodeByPoint(cur, toponame, srid, tolerance, point.x(), point.y())
        if id:
            return id
        cur.execute("SELECT ST_AddIsoNode(%s, NULL, ST_GeomFromText('POINT(%s %s)', %s)) As nodeId",
                    (toponame, point.x(), point.y(), srid))
        return cur.fetchone()[0]

    def createEdgeModifyingFace(self, cur, toponame, nodeId1, nodeId2):
        strQuery = "SELECT ST_AddEdgeModFace('{0}', {1}, {2}, ST_MakeLine((select geom from {0}.node where node_id={1}),(select geom from {0}.node where node_id={2})))"
        strQuery = strQuery.format(toponame, nodeId1, nodeId2)
        cur.execute(strQuery)

    def importClicked(self):
        # profile.runctx("self.importShapefile()", globals(), locals())
        parcelsLayer = self.parcelsLayerList[self.comboBox.currentIndex()]
        sridSrc = parcelsLayer.crs().authid().split(':')[1]
        sridDest = self.node_layer.crs().authid().split(':')[1]
        transformation = QgsCoordinateTransform(parcelsLayer.crs(), self.node_layer.crs(), QgsProject.instance())

        toponame = str(self.edge_uri.schema())
        conn = psycopg2.connect(self.edge_uri.connectionInfo())
        srid = my_map.getSrid(self.edge_uri)
        cur = conn.cursor()
        tolerance = 0
        errors = None
        try:
            for f in parcelsLayer.getFeatures():
                geometry = f.geometry()
                if geometry is None:
                    continue
                polygons = geometry.asPolygon()
                for polygon in polygons:
                    for start, end in zip(polygon[:-1], polygon[1:]):
                        start = self.transformToLayerSRID(transformation, start)
                        end = self.transformToLayerSRID(transformation, end)
                        start = self.add_node(cur, toponame, srid, tolerance, start)
                        conn.commit()
                        end = self.add_node(cur, toponame, srid, tolerance, end)
                        conn.commit()
                        try:
                            self.createEdgeModifyingFace(cur, toponame, start, end)
                            conn.commit()
                        except:
                            conn.rollback()
            cur.close()
            conn.close()
        except Exception as e:
            errors = e
            conn.rollback()
            cur.close()
        conn.close()
        if errors:
            raise errors
        my_canvas.refreshNodeLayer(self.canvas)
        my_canvas.refreshEdgeLayer(self.canvas)
        self.accept()
