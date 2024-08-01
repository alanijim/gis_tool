import os
import uuid
import webbrowser

from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox
from qgis.core import QgsFeatureRequest, QgsRectangle, QgsPointXY, QgsWkbTypes

import my_war

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'FormExportCadastre.ui'))

class FormExportCadastre(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(FormExportCadastre, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.setFixedSize(self.geometry().width(), self.geometry().height())
        self.pushButtonExport.clicked.connect(self.exportClicked)

        self.pointsLayerList = []
        self.parcelsLayerList = []

    def myExec(self, canvas):
        self.comboBoxPointsLayer.clear()
        self.comboBoxParcelsLayer.clear()
        for layer in canvas.layers():
            if layer.geometryType() == QgsWkbTypes.PointGeometry:
                self.comboBoxPointsLayer.addItem(layer.name())
                self.pointsLayerList.append(layer)
                continue
            if layer.geometryType() == QgsWkbTypes.PolygonGeometry:
                self.comboBoxParcelsLayer.addItem(layer.name())
                self.parcelsLayerList.append(layer)
                continue
        self.exec_()

    def exportClicked(self):
        pointsLayer = self.pointsLayerList[self.comboBoxPointsLayer.currentIndex()]
        parcelsLayer = self.parcelsLayerList[self.comboBoxParcelsLayer.currentIndex()]
        pointNameColumn = self.lineEditPointNameColumn.text()
        plotNameColumn = self.lineEditPlotNameColumn.text()
        exportTo = self.lineEditExportTo.text()
        result = self.checkDuplicates(parcelsLayer, plotNameColumn)
        if result != '':
            QMessageBox.information(None, "Error", "The following plot numbers are having duplicates " + result)
            return

        result = self.checkMissingPoints(parcelsLayer, plotNameColumn, pointsLayer)
        if result != '':
            QMessageBox.information(None, "Error", "The following plots are having a missing point details " + result)
            return

        for f in parcelsLayer.getFeatures():
            points, traverses = self.read(f, pointsLayer, pointNameColumn)
            # content = self.generateContent(points,traverses)
            content = self.generateCSV(points)
            filename = os.path.join(exportTo, parcelsLayer.name() + '-' + self.getPlotName(f, plotNameColumn) + '.txt')
            with open(filename, "w") as text_file:
                text_file.write(content)

    def generateCSV(self, points):
        lines = []
        lines.append('CM, X, Y, Z')
        for point in points:
            lines.append(f"{point['NAME']}, {point['X']}, {point['Y']}, 0")
        return '\n'.join(lines)

    def generateContent(self, points, traverses):
        content = '<?xml version="1.0" encoding="utf-8"?>\n'
        content += '<ROOT>\n'
        content += '<SURVEYPLAN />\n'
        content += '<PARCEL/>\n'
        content += '<CONTROLPOINTS />\n'
        content += '<POINTS>\n'
        oid = 0
        for point in points:
            oid += 1
            content += f'<ROW{oid} OID="{oid}" NPOINT="{point["NPOINT"]}" TEMPID="{point["TEMPID"]}" NAME="{point["NAME"]}" TYPE="_Station" CATEGORY="_PointCategory1" X="{point["X"]}" Y="{point["Y"]}" Z="0" UNITS="_METER" WEIGHT="0" GEOX="{point["X"]}" GEOY="{point["Y"]}" NJOBID="5d66d046-81cd-48fe-83a0-720d5d0dd84c" CONTROLPOINTID="00000000-0000-0000-0000-000000000000" N="{oid}" />\n'
        content += '</POINTS>\n'
        content += '<Traverses>\n'
        for traverse in traverses:
            oid += 1
            content += f'<ROW{oid} OID="{oid}" LINK="" FROM="{traverse["FROM"]}" FROMTMPID="{traverse["FROMTMPID"]}" DIRECTION="" DISTANCE="" TO="{traverse["TO"]}" TOTMPID="{traverse["TOTMPID"]}" TANGENTDIRECTION="" RADIUS="" ARCLENGTH="" TURN="_NONE" RADIALDIRECTION="" UNITS="_METER" DIRECTIONUNIT="_DegreesMinutesSeconds" DIRECTIONTYPE="_NorthAzimuth" />\n'
        content += '</Traverses>\n'
        content += '</ROOT>'
        return content

    def read(self, f, pointsLayer, pointNameColumn):
        points_to_return = []
        traverses = []
        geometry = f.geometry()
        if geometry is None:
            return points_to_return, traverses
        polygon = geometry.asPolygon()
        points = polygon[0][:-1]

        uuids = {i: str(uuid.uuid4()) for i in range(len(points))}
        for i in uuids:
            point = self.getPointFeature(points[i], pointsLayer)
            name = point[pointNameColumn]
            x = points[i].x()
            y = points[i].y()
            points_to_return.append({"NPOINT": uuids[i], "TEMPID": i + 1, "NAME": name, "X": x, "Y": y})

        for i in uuids:
            j = 0
            if i < len(points) - 1:
                j = i + 1
            point1 = points[i]
            point2 = points[j]
            uuid1 = uuids[i]
            uuid2 = uuids[j]
            traverses.append({"FROM": uuid1, "TO": uuid2, "FROMTMPID": i + 1, "TOTMPID": j + 1})

        return points_to_return, traverses

    def getPlotName(self, feature, plotNameColumn):
        return str(feature[plotNameColumn])

    def checkMissingPoints(self, parcelsLayer, plotNameColumn, pointsLayer):
        polygon_with_missing_points = []
        for f in parcelsLayer.getFeatures():
            geometry = f.geometry()
            if geometry is None:
                continue
            polygon = geometry.asPolygon()
            points = polygon[0]

            missing_point = False
            for point in points:
                pointFeature = self.getPointFeature(point, pointsLayer)
                if pointFeature is None:
                    missing_point = True
                    break
            if missing_point:
                polygon_with_missing_points.append(self.getPlotName(f, plotNameColumn))
        return ', '.join(polygon_with_missing_points)

    def getPointFeature(self, point, pointsLayer):
        searchRadius = 0.1
        rect = QgsRectangle()
        rect.setXMinimum(point.x() - searchRadius)
        rect.setYMinimum(point.y() - searchRadius)
        rect.setXMaximum(point.x() + searchRadius)
        rect.setYMaximum(point.y() + searchRadius)

        rq = QgsFeatureRequest(rect)
        rq.setFlags(QgsFeatureRequest.ExactIntersect)
        f = None
        try:
            f = next(pointsLayer.getFeatures(rq))
        except StopIteration:
            return None
        return f

    def checkDuplicates(self, parcelsLayer, plotNameColumn):
        counter = {}
        for f in parcelsLayer.getFeatures():
            plot = self.getPlotName(f, plotNameColumn)
            if plot not in counter:
                counter[plot] = 1
            else:
                counter[plot] += 1
        counter = [plot for plot in counter if counter[plot] > 1]
        if len(counter) > 0:
            return ", ".join(counter)
        return ""
