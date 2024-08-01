import psycopg2
from qgis._core import QgsGeometry, QgsCoordinateTransform, QgsMapLayerRegistry, QgsMapLayer
from qgis.core import *
from PyQt4.QtGui import QMessageBox

def transformToCurrentLayerSRID(canvas, geom):
    return transformToLayerSRID(canvas, canvas.currentLayer(), geom)

def transformToLayerSRID(canvas, layer, geom):
    renderer = canvas.mapRenderer()
    layerCRSSrsid = layer.crs().srsid()
    projectCRSSrsid = renderer.destinationCrs().srsid()
    if layerCRSSrsid != projectCRSSrsid:
        g = QgsGeometry.fromPoint(geom)
        g.transform(QgsCoordinateTransform(projectCRSSrsid, layerCRSSrsid, QgsProject.instance()))
        retPoint = g.asPoint()
    else:
        retPoint = geom
    return retPoint

def transformToProjectSRID(canvas, layer, geom):
    renderer = canvas.mapRenderer()
    layerCRSSrsid = layer.crs().srsid()
    projectCRSSrsid = renderer.destinationCrs().srsid()
    if layerCRSSrsid != projectCRSSrsid:
        geom.transform(QgsCoordinateTransform(layerCRSSrsid, projectCRSSrsid, QgsProject.instance()))
    return geom

const_slaac_srid = None

def getSrid(uri):
    global const_slaac_srid
    if const_slaac_srid:
        return const_slaac_srid
    toponame = str(uri.schema())
    conn = psycopg2.connect(str(uri.connectionInfo()))
    errors = None
    try:
        cur = conn.cursor()
        cur.execute("SELECT topology.topologysummary('{}')".format(toponame))
        ret = cur.fetchone()[0]
        const_slaac_srid = ret.split("SRID ")[1].split(",")[0].strip()
        cur.close()
    except psycopg2.Error as e:
        errors = e
        conn.rollback()
        cur.close()
    conn.close()
    if errors:
        raise errors
    return const_slaac_srid

def addNode(uri, x, y, tolerance):
    if getNodeByPoint(uri, x, y, tolerance):
        raise Exception('A node already exists')
    toponame = str(uri.schema())
    conn = psycopg2.connect(str(uri.connectionInfo()))
    errors = None
    srid = getSrid(uri)
    ret = None
    try:
        cur = conn.cursor()
        cur.execute("SELECT ST_AddIsoNode(%s, NULL, ST_GeomFromText('POINT(%s %s)', %s)) As nodeId",
                    (toponame, x, y, srid))
        ret = cur.fetchone()[0]
        conn.commit()
        cur.close()
    except psycopg2.Error as e:
        errors = e
        conn.rollback()
        cur.close()
    conn.close()
    if errors:
        raise errors
    return ret

def getNodeByPoint(uri, x, y, tolerance=0.1):
    toponame = str(uri.schema())
    conn = psycopg2.connect(str(uri.connectionInfo()))
    ret = None
    errors = None
    srid = getSrid(uri)
    try:
        cur = conn.cursor()
        cur.execute("SELECT topology.GetNodeByPoint(%s, ST_GeomFromText('POINT(%s %s)', %s), %s) As nodeId",
                    (toponame, x, y, srid, tolerance))
        if cur.rowcount != 0:
            ret = cur.fetchone()[0]
        conn.commit()
        cur.close()
    except psycopg2.Error as e:
        errors = e
        conn.rollback()
        cur.close()
    conn.close()
    if errors:
        raise errors
    return ret

def createEdgeModifyingFace(uri, x1, y1, x2, y2):
    nodeId1 = getNodeByPoint(uri, x1, y1)
    if nodeId1 <= 0:
        raise Exception("There is no node at the first point")
    nodeId2 = getNodeByPoint(uri, x2, y2)
    if nodeId2 <= 0:
        raise Exception("There is no node at the second point")
    createEdgeModifyingFaceFromNodeId(uri, nodeId1, nodeId2)

def createEdgeModifyingFaceFromNodeId(uri, nodeId1, nodeId2):
    assert nodeId1 is not None, 'the node 1 is None'
    assert nodeId2 is not None, 'the node 2 is None'
    toponame = str(uri.schema())
    conn = psycopg2.connect(str(uri.connectionInfo()))
    errors = None
    try:
        cur = conn.cursor()
        strQuery = "SELECT ST_AddEdgeModFace(%s, %s, %s, ST_Makeline((select geom from {}.node where node_id=%s)," \
                   "(select geom from {}.node where node_id=%s)))"
        strQuery = strQuery.format(toponame, toponame)
        cur.execute(strQuery, (toponame, nodeId1, nodeId2))
        conn.commit()
        cur.close()
    except psycopg2.Error as e:
        errors = e
        conn.rollback()
        cur.close()
    conn.close()
    if errors:
        raise errors

def createNodeBySplitingEdge(uri, edgeId, x, y):
    toponame = str(uri.schema())
    conn = psycopg2.connect(str(uri.connectionInfo()))
    errors = None
    try:
        cur = conn.cursor()
        strQuery = "WITH edge AS (SELECT geom line FROM {}.edge_data WHERE edge_id=%s), " \
                   "point AS (SELECT ST_ClosestPoint(e.line, ST_GeomFromText('POINT(%s %s)', %s)) point FROM edge e) " \
                   "SELECT ST_AsText(point) FROM point"
        srid = getSrid(uri)
        strQuery = strQuery.format(toponame)
        cur.execute(strQuery, (edgeId, x, y, srid))
        result = cur.fetchone()[0]
        nearestPointOnEdge = result.replace("(", "").replace(")", "").replace("POINT", "")
        nodeMiddleX = float(nearestPointOnEdge.split(" ")[0])
        nodeMiddleY = float(nearestPointOnEdge.split(" ")[1])
        strQuery = "SELECT start_node, end_node FROM {}.edge_data WHERE edge_id=%s"
        strQuery = strQuery.format(toponame)
        cur.execute(strQuery, (edgeId,))
        result = cur.fetchone()
        node1 = result[0]
        node2 = result[1]
        removeEdgeModifyingFace(uri, edgeId)
        nodeMiddle = addNode(uri, nodeMiddleX, nodeMiddleY, 0)
        assert nodeMiddle is not None, "the ID of the node in the middle is not known"
        createEdgeModifyingFaceFromNodeId(uri, node1, nodeMiddle)
        createEdgeModifyingFaceFromNodeId(uri, node2, nodeMiddle)
        conn.commit()
        cur.close()
    except psycopg2.Error as e:
        errors = e
        conn.rollback()
        cur.close()
    conn.close()
    if errors:
        raise errors

def removeEdgeModifyingFace(uri, edgeId):
    toponame = str(uri.schema())
    conn = psycopg2.connect(str(uri.connectionInfo()))
    errors = None
    try:
        cur = conn.cursor()
        strQuery = "SELECT ST_RemEdgeModFace(%s, %s)"
        cur.execute(strQuery, (toponame, edgeId))
        conn.commit()
        cur.close()
    except psycopg2.Error as e:
        errors = e
        conn.rollback()
        cur.close()
    conn.close()
    if errors:
        raise errors

def removeIsolatedNode(uri, nodeId):
    toponame = str(uri.schema())
    conn = psycopg2.connect(str(uri.connectionInfo()))
    errors = None
    try:
        cur = conn.cursor()
        strQuery = "SELECT ST_RemoveIsoNode(%s, %s)"
        cur.execute(strQuery, (toponame, nodeId))
        conn.commit()
        cur.close()
    except psycopg2.Error as e:
        errors = e
        conn.rollback()
        cur.close()
    conn.close()
    if errors:
        raise errors

def attemptMovingNode(uri, nodeId, x, y):
    toponame = str(uri.schema())
    conn = psycopg2.connect(str(uri.connectionInfo()))
    errors = None
    try:
        cur = conn.cursor()
        strQuery = "SELECT topology.ST_MoveIsoNode(%s, %s, ST_GeomFromText('POINT(%s %s)', %s))"
        srid = getSrid(uri)
        cur.execute(strQuery, (toponame, nodeId, x, y, srid))
        conn.commit()
        cur.close()
    except psycopg2.Error as e:
        errors = e
        conn.rollback()
        cur.close()
    conn.close()
    if errors:
        raise errors

def addNodeAtIntersection(uri, segment1, segment2):
    toponame = str(uri.schema())
    conn = psycopg2.connect(str(uri.connectionInfo()))
    errors = None
    ret = None
    try:
        cur = conn.cursor()
        strQuery = "SELECT CASE WHEN ST_Intersects('LINESTRING(%s %s,%s %s)'::geometry, " \
                   "'LINESTRING(%s %s,%s %s)'::geometry) THEN " \
                   " ST_AddIsoNode(%s, NULL, ST_SetSRID(ST_Intersection('LINESTRING(%s %s,%s %s)'::geometry, " \
                   "'LINESTRING(%s %s,%s %s)'::geometry), %s)) ELSE NULL END"
        srid = getSrid(uri)
        cur.execute(strQuery, (segment1[0].x(), segment1[0].y(), segment1[1].x(), segment1[1].y(),
                               segment2[0].x(), segment2[0].y(), segment2[1].x(), segment2[1].y(),
                               toponame,
                               segment1[0].x(), segment1[0].y(), segment1[1].x(), segment1[1].y(),
                               segment2[0].x(), segment2[0].y(), segment2[1].x(), segment2[1].y(),
                               srid))
        ret = cur.fetchone()[0]
        conn.commit()
        cur.close()
    except psycopg2.Error as e:
        errors = e
        conn.rollback()
        cur.close()
    conn.close()
    if errors:
        raise errors
    return ret

def findFaceByPoint(uri, x, y, srid):
    toponame = str(uri.schema())
    conn = psycopg2.connect(str(uri.connectionInfo()))
    errors = None
    ret = None
    try:
        cur = conn.cursor()
        strQuery = "SELECT topology.GetFaceByPoint(%s, ST_GeomFromText('POINT(%s %s)', %s), 0) As face_id"
        cur.execute(strQuery, (toponame, x, y, srid))
        ret = cur.fetchone()[0]
        conn.commit()
        cur.close()
    except psycopg2.Error as e:
        errors = e
        conn.rollback()
        cur.close()
    conn.close()
    if errors:
        raise errors
    if ret == 0:
        return None
    return ret

def findFormUnderFace(uri, face_id):
    toponame = str(uri.schema())
    conn = psycopg2.connect(str(uri.connectionInfo()))
    errors = None
    ret = None
    try:
        cur = conn.cursor()
        strQuery = "SELECT id FROM forms WHERE " \
                   " ST_CONTAINS(topology.st_getfacegeometry(%s, %s), point) ORDER BY id LIMIT 1"
        cur.execute(strQuery, (toponame, face_id))
        ret = cur.fetchone()
        if ret is not None:
            ret = ret[0]
        conn.commit()
        cur.close()
    except psycopg2.Error as e:
        errors = e
        conn.rollback()
        cur.close()
    conn.close()
    if errors:
        raise errors
    return ret

def insertForm(uri, x, y, srid):
    face_id = findFaceByPoint(uri, x, y, srid)
    if face_id is None:
        raise psycopg2.Error("Forms can be located only on top of a valid parcel")
    form_id = findFormUnderFace(uri, face_id)
    if form_id:
        return form_id
    conn = psycopg2.connect(str(uri.connectionInfo()))
    errors = None
    ret = None
    try:
        cur = conn.cursor()
        strQuery = "INSERT INTO forms (id, version, point, approximate_area, " \
                   "current_use_of_land, holdlandas, is_the_land_occupied, " \
                   "number_of_dependants, tenure_type) " \
                   "VALUES (nextval('hibernate_sequence'), " \
                   "0, ST_GeomFromText('POINT(%s %s)', %s), 0, 'Unknown', " \
                   "'Unknown', TRUE, 0, 'Unknown') RETURNING id"
        cur.execute(strQuery, (x, y, srid))
        ret = cur.fetchone()[0]

        strQuery = "UPDATE forms SET parcel_no = 'TMP_' || currval('hibernate_sequence') " \
                   "WHERE id = currval('hibernate_sequence')"
        cur.execute(strQuery)
        conn.commit()
        cur.close()
    except psycopg2.Error as e:
        errors = e
        conn.rollback()
        cur.close()
    conn.close()
    if errors:
        raise errors
    return ret

def getParcelExtent(uri, guid):
    toponame = str(uri.schema())
    conn = psycopg2.connect(str(uri.connectionInfo()))
    errors = None
    ret = None
    try:
        cur = conn.cursor()
        strQuery = "SELECT ST_ASTEXT(ST_BUFFER(ST_EXTENT(mbr), 10)) FROM uganda.face WHERE " \
                   "EXISTS (SELECT 1 FROM forms WHERE " \
                   "ST_CONTAINS(topology.st_getfacegeometry(%s, face.face_id), " \
                   "forms.point) AND LOWER(guid)=LOWER(%s)) " \
                   "AND face.mbr IS NOT NULL LIMIT 1"
        cur.execute(strQuery, (toponame, guid))
        ret = cur.fetchone()[0]
        if ret is None:
            strQuery = "SELECT ST_ASTEXT(ST_BUFFER(forms.point, 20)) FROM forms WHERE " \
                       "LOWER(guid)=LOWER(%s) LIMIT 1"
            cur.execute(strQuery, (guid,))
            ret = cur.fetchone()[0]
        cur.close()
    except psycopg2.Error as e:
        errors = e
        conn.rollback()
        cur.close()
    conn.close()
    if errors:
        raise errors
    return ret
