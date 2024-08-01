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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QObject, SIGNAL
from PyQt4.QtGui import QAction, QIcon, QMessageBox
# Initialize Qt resources from file resources.py
from qgis._core import QgsDataSourceURI, QGis, QgsPoint, QgsVectorLayer, QgsGPSDetector, QgsCoordinateReferenceSystem, \
    QgsCsException

import resources
# Import the code for the dialog
from form_version import FormVersion
from form_zoom_to_parcel import FormZoomToParcel
from slaac_gathering_tool_add_node import *
from slaac_gathering_tool_add_edge import *
from slaac_gathering_tool_dialog import SlaacGatheringToolDialog
from slaac_gathering_tool_split_edge import *
from slaac_gathering_tool_remove_edge import *
from slaac_gathering_tool_remove_node import *
from slaac_gathering_tool_move_node import *
from slaac_gathering_tool_add_node_at_intersection import *
from slaac_gathering_tool_forms import *
from slaac_gathering_tool_draw_export_area import *
from slaac_gathering_tool_remove_export_area import *
from slaac_gathering_tool_export_area import *
from slaac_gathering_tool_solve_problem import *
from qgis.core import *
from qgis.gui import *
from form_export_cadastre import *
from form_import_shapefile import *
import rubber
import os.path
import webbrowser

class SlaacGatheringTool:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'SlaacGatheringTool_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Slaac Gathering Tool')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'SlaacGatheringTool')
        self.toolbar.setObjectName(u'SlaacGatheringTool')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('SlaacGatheringTool', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        checkable=False,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """


        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        action.setCheckable(checkable)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        # Create the dialog (after translation) and keep reference
        self.dlg = SlaacGatheringToolDialog()
        self.dlgAbout = FormVersion()
        self.dlgZoomToParcel = FormZoomToParcel(self.canvas)
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/SlaacGatheringTool/icons/48/'
        self.zoomTo = self.add_action(
            icon_path + 'ZoomToXY.png',
            text=self.tr(u'Zoom To'),
            callback=self.zoomToMethod,
            parent=self.iface.mainWindow(),
            enabled_flag=True,
            add_to_menu=False,
            checkable=False
        )
        self.hideZoomTo = self.add_action(
            icon_path + 'HideZoomPin.png',
            text=self.tr(u'Hide the Zoom To Pin'),
            callback=self.hideZoomToMethod,
            parent=self.iface.mainWindow(),
            enabled_flag=True,
            add_to_menu=False,
            checkable=False
        )
        self.addNodeToXY = self.add_action(
            icon_path + 'AddNodeXY.png',
            text=self.tr(u'Add Node To XY'),
            callback=self.addNodeToXYMethod,
            parent=self.iface.mainWindow(),
            enabled_flag=True,
            add_to_menu=False,
            checkable=False
        )
        self.addNodeMiddleCanvas = self.add_action(
            icon_path + 'addNodeMiddleCanvas.png',
            text=self.tr(u'Add Node to the middle of the canvas (scale less than 1:10,000)'),
            callback=self.addNodeMiddleCanvasMethod,
            parent=self.iface.mainWindow(),
            enabled_flag=True,
            add_to_menu=False,
            checkable=False
        )
        self.addNode = self.add_action(
            icon_path + 'AddNode.png',
            text=self.tr(u'Add Node'),
            callback=self.addNodeMethod,
            parent=self.iface.mainWindow(),
            enabled_flag=True,
            add_to_menu=False,
            checkable=True
            )

        self.moveNode = self.add_action(
            icon_path + 'MoveNode.png',
            text=self.tr(u'Move Node'),
            callback=self.moveNodeMethod,
            parent=self.iface.mainWindow(),
            enabled_flag=True,
            add_to_menu=False,
            checkable=True
            )
        self.removeNode = self.add_action(
            icon_path + 'RemoveNode.png',
            text=self.tr(u'Remove Node'),
            callback=self.removeNodeMethod,
            parent=self.iface.mainWindow(),
            enabled_flag=True,
            add_to_menu=False,
            checkable=True
            )
        self.addNodeAtIntersection = self.add_action(
            icon_path + 'AddNodeAtIntersection.png',
            text=self.tr(u'Add Node at Intersection'),
            callback=self.addNodeAtIntersectionMethod,
            parent=self.iface.mainWindow(),
            enabled_flag=True,
            add_to_menu=False,
            checkable=True
            )
        self.addEdge = self.add_action(
            icon_path + 'AddEdge.png',
            text=self.tr(u'Add Edge'),
            callback=self.addEdgeMethod,
            parent=self.iface.mainWindow(),
            enabled_flag=True,
            add_to_menu=False,
            checkable=True
            ) 
        self.splitEdge = self.add_action(
            icon_path + 'SplitEdge.png',
            text=self.tr(u'Split Edge'),
            callback=self.splitEdgeMethod,
            parent=self.iface.mainWindow(),
            enabled_flag=True,
            add_to_menu=False,
            checkable=True
            )
        self.removeEdge = self.add_action(
            icon_path + 'RemoveEdge.png',
            text=self.tr(u'Remove Edge'),
            callback=self.removeEdgeMethod,
            parent=self.iface.mainWindow(),
            enabled_flag=True,
            add_to_menu=False,
            checkable=True
            )
        self.forms = self.add_action(
            icon_path + 'Forms.png',
            text=self.tr(u'Forms'),
            callback=self.formsMethod,
            parent=self.iface.mainWindow(),
            enabled_flag=True,
            add_to_menu=False,
            checkable=True
            )
        self.formsZoomToParcel = self.add_action(
            icon_path + 'FormsZoomTo.png',
            text=self.tr(u'Zoom to a parcel given a barcode'),
            callback=self.formsZoomToParcelMethod,
            parent=self.iface.mainWindow(),
            enabled_flag=True,
            add_to_menu=False,
            checkable=False
            )

        self.drawExportArea = self.add_action(
            icon_path + 'DrawArea.png',
            text=self.tr(u'Draw Area To Export'),
            callback=self.drawExportAreaMethod,
            parent=self.iface.mainWindow(),
            enabled_flag=True,
            add_to_menu=False,
            checkable=True
            )

        self.editExportArea = self.add_action(
            icon_path + 'EditArea.png',
            text=self.tr(u'Edit Area To Export'),
            callback=self.editExportAreaMethod,
            parent=self.iface.mainWindow(),
            enabled_flag=True,
            add_to_menu=False,
            checkable=True
            )

        self.removeExportArea = self.add_action(
            icon_path + 'RemoveArea.png',
            text=self.tr(u'Remove Export Area'),
            callback=self.removeExportAreaMethod,
            parent=self.iface.mainWindow(),
            enabled_flag=True,
            add_to_menu=False,
            checkable=True)

        self.exportArea = self.add_action(
            icon_path + 'ExportArea.png',
            text=self.tr(u'Export Area'),
            callback=self.exportAreaMethod,
            parent=self.iface.mainWindow(),
            enabled_flag=True,
            add_to_menu=False,
            checkable=True)

        self.importArea = self.add_action(
            icon_path + 'ImportArea.png',
            text=self.tr(u'Import Area'),
            callback=self.importAreaMethod,
            parent=self.iface.mainWindow(),
            enabled_flag=True,
            add_to_menu=False,
            checkable=False)

        self.importShapefile = self.add_action(
            icon_path + 'ImportArea.png',
            text=self.tr(u'Import Shapefile'),
            callback=self.importShapefileMethod,
            parent=self.iface.mainWindow(),
            enabled_flag=True,
            add_to_menu=False,
            checkable=False)

        self.importArea = self.add_action(
            icon_path + 'ImportArea.png',
            text=self.tr(u'Import Forms'),
            callback=self.importFormsMethod,
            parent=self.iface.mainWindow(),
            enabled_flag=True,
            add_to_menu=False,
            checkable=False)

        self.about = self.add_action(
            icon_path + 'About.png',
            text=self.tr(u'About'),
            callback=self.aboutMethod,
            parent=self.iface.mainWindow(),
            enabled_flag=True,
            add_to_menu=False,
            checkable=False
        )

        QObject.connect(self.iface, SIGNAL("currentLayerChanged(QgsMapLayer*)"), self.toggle)
        QObject.connect(self.canvas, SIGNAL("mapToolSet(QgsMapTool*)"), self.deactivate)
        
        self.addNode_tool = SlaacGatheringToolAddNode(self.canvas)
        self.addEdge_tool = SlaacGatheringToolAddEdge(self.canvas)
        self.splitEdge_tool = SlaacGatheringToolSplitEdge(self.canvas)
        self.removeEdge_tool = SlaacGatheringToolRemoveEdge(self.canvas)
        self.removeNode_tool = SlaacGatheringToolRemoveNode(self.canvas)
        self.moveNode_tool = SlaacGatheringToolMoveNode(self.canvas)
        self.addNodeAtIntersection_tool = SlaacGatheringToolAddNodeAtIntersection(self.canvas)
        self.forms_tool = SlaacGatheringToolForms(self.canvas)
        self.zoomToMarker = rubber.myVertexMarker(self.canvas)
        self.drawExportArea_tool = SlaacGatheringToolDrawExportArea(self.iface, self.canvas)
        self.removeExportArea_tool = SlaacGatheringToolRemoveExportArea(self.canvas)
        self.exportArea_tool = SlaacGatheringToolExportArea(self.canvas)

        self.iface.actionNodeTool().toggled.connect(self.actionNodeToolToggled)

        self.export_layer = my_canvas.getExportLayer(self.canvas)
        if not self.export_layer:
            project = QgsProject.instance()
            project.layerLoaded.connect(self.layerLoaded)
        else:
            self.export_layer.layerModified.connect(self.layerModified)

        self.forms_layer = my_canvas.getFormLayer(self.canvas)
        if not self.forms_layer:
            project = QgsProject.instance()
            project.layerLoaded.connect(self.formsLayerLoaded)
        else:
            self.forms_layer.layerModified.connect(self.layerModified)
        # self.gpsConn = None
        # self.gpsDetector = None
        # self.initGPS()
        # self.wgs84CRS = QgsCoordinateReferenceSystem(4326)

        self.formExportCadastre = FormExportCadastre()
        self.formImportShapefile = FormImportShapefile()
        self.toggle()

    def layerLoaded(self,i, n):
        if self.export_layer:
            return
        export_layer = my_canvas.getExportLayer(self.canvas)
        if export_layer:
            self.export_layer = export_layer
            export_layer.layerModified.connect(self.layerModified)

    def formsLayerLoaded(self,i, n):
        if self.forms_layer:
            return
        forms_layer = my_canvas.getExportLayer(self.canvas)
        if forms_layer:
            self.forms_layer = forms_layer
            forms_layer.layerModified.connect(self.layerModified)

    def deactivate(self):
        self.addNode.setChecked(False)
        self.addEdge.setChecked(False)
        self.splitEdge.setChecked(False)
        self.addNodeMiddleCanvas.setChecked(False)
        self.removeEdge.setChecked(False)
        self.removeNode.setChecked(False)
        self.moveNode.setChecked(False)
        self.addNodeAtIntersection.setChecked(False)
        self.addNodeToXY.setChecked(False)
        self.zoomTo.setChecked(False)
        self.hideZoomTo.setChecked(False)
        self.forms.setChecked(False)
        self.drawExportArea.setChecked(False)
        self.editExportArea.setChecked(False)
        self.removeExportArea.setChecked(False)
        self.exportArea.setChecked(False)
        self.formsZoomToParcel.setChecked(False)
        self.importArea.setChecked(False)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Slaac Gathering Tool'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
    def toggle(self):
        mc = self.iface.mapCanvas()
        layer = mc.currentLayer()
        # mc = self.iface.mapCanvas()
        # layer = mc.currentLayer()
        # Decide whether the plugin button/menu is enabled or disabled
        node_layer = my_canvas.getNodeLayer(mc)
        export_layer = my_canvas.getExportLayer(mc)
        imported_layer = my_canvas.getImportedLayer(mc)
        form_layer = my_canvas.getFormLayer(mc)
        edge_layer = my_canvas.getEdgeLayer(mc)
        locked_layer = my_canvas.getLockedLayer(mc)
        enabled = layer in [node_layer, export_layer, form_layer, edge_layer, locked_layer, imported_layer]

        self.addNode.setVisible(enabled and layer == node_layer)
        self.addNodeMiddleCanvas.setVisible(enabled and layer == node_layer)
        self.addEdge.setVisible(enabled and layer == edge_layer)
        self.splitEdge.setVisible(enabled and layer == edge_layer)
        self.removeEdge.setVisible(enabled and layer == edge_layer)
        self.removeNode.setVisible(enabled and layer == node_layer)
        self.moveNode.setVisible(enabled and layer == node_layer)
        self.addNodeAtIntersection.setVisible(enabled and layer == edge_layer)
        self.addNodeToXY.setVisible(enabled and layer == node_layer)
        self.forms.setVisible(enabled and layer == form_layer)
        self.formsZoomToParcel.setVisible(enabled and layer == form_layer)
        self.drawExportArea.setVisible(enabled and layer == export_layer)
        self.editExportArea.setVisible(enabled and layer == export_layer)
        self.removeExportArea.setVisible(enabled and layer == export_layer)
        self.exportArea.setVisible(enabled and (layer == export_layer or layer == locked_layer))
        self.importArea.setVisible(enabled and (layer == imported_layer))


    def addNodeMethod(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.canvas.setMapTool(self.addNode_tool)
        self.addNode.setChecked(True)
        # this should call a MapTool
        # that map tool should be instantiated once under InitGUI and not every time the user is clicking on the button/menu
        # good resource is to analyze how CADDigitize.py (Can be installed as plugin and then source code will be available under the usual folder of plugin)
        # another good resource for fast understanding is http://www.lutraconsulting.co.uk/blog/2014/10/17/getting-started-writing-qgis-python-plugins/
    def addEdgeMethod(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.canvas.setMapTool(self.addEdge_tool)
        self.addEdge.setChecked(True)
    def splitEdgeMethod(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.canvas.setMapTool(self.splitEdge_tool)
        self.splitEdge.setChecked(True)
    def removeEdgeMethod(self):
        self.canvas.setMapTool(self.removeEdge_tool)
        self.removeEdge.setChecked(True)
    def removeNodeMethod(self):
        self.canvas.setMapTool(self.removeNode_tool)
        self.removeNode.setChecked(True)
    def moveNodeMethod(self):
        self.canvas.setMapTool(self.moveNode_tool)
        self.moveNode.setChecked(True)
    def addNodeAtIntersectionMethod(self):
        self.canvas.setMapTool(self.addNodeAtIntersection_tool)
        self.addNodeAtIntersection.setChecked(True)
    def zoomToMethod(self):
        self.dlg.setWindowTitle("Coordinates To Zoom To")
        #self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            coordinates = self.dlg.getCoordinates()
            self.zoomToCoordinates(coordinates)
    def zoomToCoordinates(self, coordinates):
        center = QgsPoint(float(coordinates[0]), float(coordinates[1]))
        self.canvas.setCenter(center)
        self.canvas.refresh()
        self.canvas.zoomScale(1000)
        self.zoomToMarker.setCenter(center)
        self.zoomToMarker.show()
    def aboutMethod(self, coordinates):
        self.dlgAbout.exec_()
    def addNodeToXYMethod(self):
        self.dlg.setWindowTitle("Coordinates of Node to Add")
        # self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            coordinates = self.dlg.getCoordinates()
            self.zoomToCoordinates(coordinates)
            try:
                layer = self.canvas.currentLayer()
                layerPoint = QgsPoint(float(coordinates[0]), float(coordinates[1]))
                layerPoint = my_map.transformToLayerSRID(self.canvas,layer, layerPoint)
                tolerance = my_canvas.getLayerSearchRadius(self.canvas, layer)
                uri = QgsDataSourceURI(layer.source())
                my_map.addNode(uri, layerPoint.x(), layerPoint.y(), tolerance)
                my_canvas.refreshNodeLayer(self.canvas)
            except psycopg2.Error as e:
                errors = "Add Node From Coordinates:\n" + str(e)
                QMessageBox.information(None, "Slaac Gathering Tool", errors)
            except Exception as e:
                errors = "Add Node From Coordinates:\n" + str(e)
                QMessageBox.information(None, "Slaac Gathering Tool", errors)
    def addNodeMiddleCanvasMethod(self):
        if(self.canvas.scale() > 10000):
            QMessageBox.information(None, "Slaac Gathering Tool", "Set the scale to below 10,000 prior to " + \
                                    "add a node to the middle of the screen.")
            return
        e = self.canvas.extent()
        coordinates=[(e.xMaximum()+e.xMinimum()) / 2, (e.yMaximum()+e.yMinimum()) / 2]
        try:
            layer = self.canvas.currentLayer()
            layerPoint = QgsPoint(float(coordinates[0]), float(coordinates[1]))
            layerPoint = my_map.transformToLayerSRID(self.canvas, layer, layerPoint)
            tolerance = my_canvas.getLayerSearchRadius(self.canvas, layer)
            uri = QgsDataSourceURI(layer.source())
            my_map.addNode(uri, layerPoint.x(), layerPoint.y(), tolerance)
            my_canvas.refreshNodeLayer(self.canvas)
            QMessageBox.information(None, "Slaac Gathering Tool", "A node was added at the middle of the canvas")
        except psycopg2.Error as e:
            errors = "Add Node at the middle of the canvas:\n" + str(e)
            QMessageBox.information(None, "Slaac Gathering Tool", errors)
        except Exception as e:
            errors = "Add Node at the middle of the canvas:\n" + str(e)
            QMessageBox.information(None, "Slaac Gathering Tool", errors)
    def hideZoomToMethod(self):
        self.zoomToMarker.hide()
    def formsMethod(self):
        # update the form
        # delete the form
        # print the form
        self.canvas.setMapTool(self.forms_tool)
        self.forms.setChecked(True)

    def drawExportAreaMethod(self):
        self.canvas.setMapTool(self.drawExportArea_tool)
        self.drawExportArea.setChecked(True)
    def editExportAreaMethod(self):
        layer = my_canvas.getExportLayer(self.canvas)
        #This value is changed once the user had clicked on the button
        #If the button was unchecked and the user click on it
        #Here it will be alread checked before this method is called

        checked = self.editExportArea.isChecked()
        if not checked:
            if layer.isEditable():
                self.iface.actionSaveEdits().trigger()
                self.iface.actionToggleEditing().trigger()
                self.iface.actionPan().trigger()
        else:
            if not layer.isEditable():
                self.iface.actionToggleEditing().trigger()
            if not self.iface.actionNodeTool().isChecked():
                self.iface.actionNodeTool().trigger()
        self.editExportArea.setChecked(checked)

    def formsZoomToParcelMethod(self):
        # this will activate the window
        self.dlgZoomToParcel.activateWindow()
        self.dlgZoomToParcel.show()

    def removeExportAreaMethod(self):
        self.canvas.setMapTool(self.removeExportArea_tool)
        self.removeExportArea.setChecked(True)

    def actionNodeToolToggled(self, checked):
        if not checked:
            self.editExportArea.setChecked(False)
            layer = my_canvas.getExportLayer(self.canvas)
            if layer.isEditable():
                self.iface.actionSaveEdits().trigger()
                self.iface.actionToggleEditing().trigger()

    def layerModified(self):
        self.iface.actionSaveEdits().trigger()

    def exportAreaMethod(self):
        self.canvas.setMapTool(self.exportArea_tool)
        self.exportArea.setChecked(True)

    def importAreaMethod(self):
        to_open = my_war.get_default_path(self.canvas) + "/export/import"
        webbrowser.open(to_open)

    def importShapefileMethod(self):
        self.formImportShapefile.myExec(self.canvas)

    def importFormsMethod(self):
        to_open = my_war.get_default_path(self.canvas) + "/export/importForms"
        webbrowser.open(to_open)

    def exportToCadastreMethod(self):
        self.formExportCadastre.myExec(self.canvas)

    def initGPS(self):
        self.gpsDetector = QgsGPSDetector("")
        def _connected(c):
            self.gpsConn = c
        self.gpsDetector.detected.connect(_connected)

    # https://github.com/NathanW2/qmap/blob/master/src/qmap/gps_action.py
    # https://gis.stackexchange.com/questions/188002/connect-disconnect-gps-device-via-pyqgis
    def addPointFromGPSMethod(self):
        self.gpsDetector.advance()
        if self.gpsConn.status() <> 3:
            QMessageBox.information(None, "Slaac Gathering Tool", "GPS Connection error " + str(self.gpsDetector.status()))
            return
        y = self.gpsConn.currentGPSInformation().latitude
        x = self.gpsConn.currentGPSInformation().longitude
        myPosition = QgsPoint(x, y)

        layerPoint = my_canvas.getNodeLayer()
        transform = QgsCoordinateTransform(self.wgs84CRS, layerPoint.crs())
        uri = QgsDataSourceURI(layerPoint.source())
        try:
            transformed = transform.transform(myPosition)

            tolerance = my_canvas.getLayerSearchRadius(self.canvas, layerPoint)
            my_map.addNode(uri, transformed.x(), transformed.y(), tolerance)
            my_canvas.refreshNodeLayer(self.canvas)
            QMessageBox.information(None, "Slaac Gathering Tool", "Point added")
        except psycopg2.Error as e:
            errors = "Add Node from GPS:\n" + str(e)
            QMessageBox.information(None, "Slaac Gathering Tool", errors)
        except QgsCsException as e:
            QMessageBox.information(None, "Slaac Gathering Tool",str(e))
            return