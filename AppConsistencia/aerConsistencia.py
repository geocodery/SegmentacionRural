#!/usr/bin/python
# -*- coding: utf-8-*-

import arcpy
from Generales import settings, funcionesGenerales


arcpy.overwriteOutput = True
CALIDAD_AER_PRESEGM = r'Database Connections\GEODB_CPV_SEGM.sde\GEODB_CPV_SEGM.SDE.CALIDAD_RURAL\GEODB_CPV_SEGM.SDE.CALIDAD_AER_PRESEGM'
conn = settings.conectionDB_pymmsql()
conexionGDB = settings.conectionGDB_arcpy()
conexionDB = settings.conectionDB_arcpy()


def ubigeosDisponibles(conn=conn):
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT UBIGEO FROM VW_SEGM_R_INSUMOS WHERE TB_AER = 1 AND TB_CCPP = 1 AND TB_VIVIENDA_R = 1 AND TB_CPV0301_VIVIENDA_R = 1")
    ubigeos = [x[0] for x in cursor]
    return ubigeos


def aer_E1(expresion, conexionBD=conexionDB):
    informacion = []
    aer_mql = arcpy.MakeQueryLayer_management(conexionBD, "AERS_mql", "SELECT*FROM TB_AER WHERE {}".format(expresion), 'UBIGEO;AER_INI;AER_FIN', 'POLYGON', '4326', arcpy.SpatialReference(4326))
    dist_mql = arcpy.MakeQueryLayer_management(conexionBD, "dist_mql", "SELECT*FROM VW_DISTRITO WHERE {}".format(expresion), 'UBIGEO', 'POLYGON', '4326', arcpy.SpatialReference(4326))
    aer = arcpy.CopyFeatures_management(aer_mql, "in_memory\AER_mfl")
    dist = arcpy.CopyFeatures_management(dist_mql, "in_memory\dist_mfl")
    for m in arcpy.da.SearchCursor(dist, ["SHAPE@", "UBIGEO"]):
        mfl = arcpy.MakeFeatureLayer_management(aer, "mfl", "UBIGEO = '{}'".format(m[1]))
        seleccion = arcpy.SelectLayerByLocation_management(mfl, "BOUNDARY_TOUCHES", m[0], "#", "NEW_SELECTION", "NOT_INVERT")
        if (arcpy.GetCount_management(seleccion))[0] == 1:
            pass
        else:
            aerError = [[x[0], 1] for x in arcpy.da.SearchCursor(mfl, ["IDAER"])]
            informacion.extend(aerError)
    return informacion


def aerCorregir(informacion):
    aer = [x[0] for x in informacion]
    expresion = funcionesGenerales.Expresion(aer, "#", "IDAER")
    return expresion


def cargarTabla(errores, expresion, CALIDAD_AER_PRESEGM, conexion=conexionDB, conn=conn):
    mfl = arcpy.MakeFeatureLayer_management(CALIDAD_AER_PRESEGM, "mfl", expresion)
    arcpy.DeleteRows_management(mfl)
    aer_mql = arcpy.MakeQueryLayer_management(conexion, "AERS", "SELECT*FROM TB_AER WHERE {}".format(expresion), "IDAER", 'POLYGON', '4326', arcpy.SpatialReference(4326))
    arcpy.Append_management(aer_mql, CALIDAD_AER_PRESEGM, "NO_TEST")
    for error in errores:
        cursor = conn.cursor()
        cursor.execute("UPDATE GEODB_CPV_SEGM.SDE.CALIDAD_AER_PRESEGM SET E{} = 1 WHERE IDAER = '{}'".format(error[1], error[0]))
        conn.commit()
        cursor.close()


def consistenciaCCPP(CALIDAD_AER_PRESEGM):
    informacion = []
    ubigeos = ubigeosDisponibles()
    expresion01 = funcionesGenerales.Expresion(ubigeos, "#", "UBIGEO")
    e1 = aer_E1(expresion01)
    informacion.extend(e1)
    expresion02 = aerCorregir(informacion)
    cargarTabla(informacion, expresion02, CALIDAD_AER_PRESEGM)


consistenciaCCPP(CALIDAD_AER_PRESEGM)