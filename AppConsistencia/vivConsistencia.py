#!/usr/bin/python
# -*- coding: utf-8-*-

import arcpy
from Generales import settings, funcionesGenerales

arcpy.overwriteOutput = True
CALIDAD_VIV_PRESEGM = r'Database Connections\CPV_SEGMENTACION_GDB.sde\CPV_SEGMENTACION_GDB.SDE.CALIDAD_RURAL\CPV_SEGMENTACION_GDB.SDE.CALIDAD_VIV_PRESEGM'
conn = settings.conectionDB_pymmsql()
conexionGDB = settings.conectionGDB_arcpy()
conexionDB = settings.conectionDB_arcpy()


def ubigeosDisponibles(conn=conn):
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT UBIGEO FROM VW_SEGM_R_INSUMOS WHERE TB_AER = 1 AND CPV_SEGMENTACION_GDB.sde.TB_CCPP = 1 AND TB_VIVIENDA_R = 1 AND TB_CPV0301_VIVIENDA_R = 1")
    ubigeos = [x[0] for x in cursor]
    return ubigeos


def viv_E1(expresion, conn=conn):
    cursor = conn.cursor()
    cursor.execute("SELECT IDVIV FROM TB_VIVIENDA_R WHERE ({}) GROUP BY IDVIV HAVING COUNT(IDVIV) > 1".format(expresion))
    informacion = [[x[0], 1] for x in cursor]
    cursor.close()
    return informacion


def viv_E2(expresion, conn=conn):
    cursor = conn.cursor()
    cursor.execute("SELECT IDVIV , GEOM.Lat, GEOM.Long, COUNT(*) FROM TB_VIVIENDA_R WHERE ({}) GROUP BY IDVIV , GEOM.Lat, GEOM.Long HAVING COUNT(*) > 1".format(expresion))
    informacion = [[x[0], 2] for x in cursor]
    cursor.close()
    return informacion


def vivCorregir(informacion):
    viviendas = [x[0] for x in informacion]
    expresion = funcionesGenerales.Expresion(viviendas, "#", "IDVIV")
    return expresion


def cargarTabla(errores, expresion, CALIDAD_VIV_PRESEGM, conexion=conexionDB, conn=conn):
    mfl = arcpy.MakeFeatureLayer_management(CALIDAD_VIV_PRESEGM, "mfl", expresion)
    arcpy.DeleteRows_management(mfl)
    viv_mql = arcpy.MakeQueryLayer_management(conexion, "CCPPS", "SELECT*FROM TB_VIVIENDA_R WHERE {}".format(expresion), "IDVIV", 'POINT', '4326', arcpy.SpatialReference(4326))
    arcpy.Append_management(viv_mql, CALIDAD_VIV_PRESEGM, "NO_TEST")
    for error in errores:
        cursor = conn.cursor()
        cursor.execute("UPDATE CPV_SEGMENTACION_GDB.SDE.CALIDAD_VIV_PRESEGM SET E{} = 1 WHERE IDVIV= '{}'".format(error[1], error[0]))
        conn.commit()
        cursor.close()


def consistenciaVIV(CALIDAD_VIV_PRESEGM, ubigeos_input=[]):
    informacion = []
    if len(ubigeos_input) == 0:
        ubigeos = ubigeosDisponibles()
    else:
        ubigeos = ubigeos_input
    expresion01 = funcionesGenerales.Expresion(ubigeos, "#", "UBIGEO")
    e1 = viv_E1(expresion01)
    e2 = viv_E2(expresion01)
    for x in [e1, e2]:
        informacion.extend(x)
    if len(informacion) > 0:
        expresion02 = vivCorregir(informacion)
        cargarTabla(informacion, expresion02, CALIDAD_VIV_PRESEGM)
    else:
        pass