#!/usr/bin/python
# -*- coding: utf-8-*-

import arcpy
from Generales import settings, funcionesGenerales


arcpy.overwriteOutput = True
CALIDAD_CCPP_PRESEGM = r'Database Connections\CPV_SEGMENTACION_GDB.sde\CPV_SEGMENTACION_GDB.SDE.CALIDAD_RURAL\CPV_SEGMENTACION_GDB.SDE.CALIDAD_CCPP_PRESEGM'
CALIDAD_VIV_PRESEGM = r'Database Connections\CPV_SEGMENTACION_GDB.sde\CPV_SEGMENTACION_GDB.SDE.CALIDAD_RURAL\CPV_SEGMENTACION_GDB.SDE.CALIDAD_VIV_PRESEGM'
conn = settings.conectionDB_pymmsql()
conexionGDB = settings.conectionGDB_arcpy()
conexionDB = settings.conectionDB_arcpy()


def eliminarData(conn=conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM SEGM_CONTROL_CALIDAD_INPUT_R ")
    conn.commit()
    cursor.close()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM CPV_SEGMENTACION_GDB.sde.CALIDAD_CCPP_PRESEGM")
    conn.commit()
    cursor.close()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM CPV_SEGMENTACION_GDB.sde.CALIDAD_VIV_PRESEGM")
    conn.commit()
    cursor.close()

def ubigeosDisponibles(conn=conn):
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT UBIGEO FROM VW_SEGM_R_INSUMOS WHERE TB_AER = 1 AND TB_CCPP = 1 AND TB_VIVIENDA_R = 1 AND TB_CPV0301_VIVIENDA_R = 1 AND TB_TRACK = 1")
    ubigeos = [x[0] for x in cursor]
    return ubigeos


# CENTROS POBLADOS FUERA DEL DISTRITO

def ccpp_E1(expresion, conn=conn):
    cursor = conn.cursor()
    cursor.execute("SELECT LLAVE_CCPP FROM CPV_SEGMENTACION_GDB.sde.TB_CCPP WHERE ({}) AND IDAER IS NULL AND AREA = 2".format(expresion))
    print cursor
    informacion = [[x[0], 1] for x in cursor]
    cursor.close()
    return informacion


# CENTROS POBLADOS REPETIDOS POR CODIGO

def ccpp_E2(expresion, conn=conn):
    cursor = conn.cursor()
    cursor.execute("SELECT LLAVE_CCPP FROM CPV_SEGMENTACION_GDB.sde.TB_CCPP WHERE ({}) GROUP BY LLAVE_CCPP HAVING COUNT(LLAVE_CCPP) > 1".format(expresion))
    informacion = [[x[0], 2] for x in cursor]
    cursor.close()
    return informacion


# CENTROS POBLADOS REPETIDOS POR UBICACION ESPACIAL

def ccpp_E3(expresion, conn=conn):
    cursor = conn.cursor()
    cursor.execute("SELECT LLAVE_CCPP,  GEOM.Lat, GEOM.Long, COUNT(*) FROM CPV_SEGMENTACION_GDB.sde.TB_CCPP WHERE ({}) GROUP BY LLAVE_CCPP, GEOM.Lat, GEOM.Long HAVING COUNT(*) > 1".format(expresion))
    informacion = [[x[0], 3] for x in cursor]
    cursor.close()
    return informacion


def ccppCorregir(informacion):
    ccpps = [x[0] for x in informacion]
    expresion = funcionesGenerales.Expresion(ccpps, "#", "LLAVE_CCPP")
    return expresion


def cargarTabla(errores, expresion, CALIDAD_CCPP_PRESEGM, conexion=conexionDB, conn=conn):
    mfl = arcpy.MakeFeatureLayer_management(CALIDAD_CCPP_PRESEGM, "mfl", expresion)
    arcpy.DeleteRows_management(mfl)
    ccpps_mql = arcpy.MakeQueryLayer_management(conexion, "CCPPS", "SELECT*FROM CPV_SEGMENTACION_GDB.sde.TB_CCPP WHERE {}".format(expresion), "LLAVE_CCPP", 'POINT', '4326', arcpy.SpatialReference(4326))
    arcpy.Append_management(ccpps_mql, CALIDAD_CCPP_PRESEGM, "NO_TEST")
    for error in errores:
        cursor = conn.cursor()
        cursor.execute("UPDATE CPV_SEGMENTACION_GDB.SDE.CALIDAD_CCPP_PRESEGM SET E{} = 1 WHERE LLAVE_CCPP = '{}'".format(error[1], error[0]))
        conn.commit()
        cursor.close()


#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

# AGRUPA LAS DISTINTAS HERRAMIENTAS DE CONSISTENCIA Y DEVUELVE LOS HERRORES - MAIN

def consistenciaCCPP(CALIDAD_CCPP_PRESEGM, ubigeos_input=[]):
    informacion = []
    if len(ubigeos_input) == 0:
        ubigeos = ubigeosDisponibles()
    else:
        ubigeos = ubigeos_input
    expresion01 = funcionesGenerales.Expresion(ubigeos, "#", "UBIGEO")
    print ubigeos
    e1 = ccpp_E1(expresion01)
    e2 = ccpp_E2(expresion01)
    e3 = ccpp_E3(expresion01)
    for x in [e1, e2, e3]:
        informacion.extend(x)
    expresion02 = ccppCorregir(informacion)
    cargarTabla(informacion, expresion02, CALIDAD_CCPP_PRESEGM)


#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::


def ubigeosError(CALIDAD_CCPP_PRESEGM, CALIDAD_VIV_PRESEGM):
    eliminarData()
    ccpps = [x[0] for x in arcpy.da.SearchCursor(CALIDAD_CCPP_PRESEGM, ["UBIGEO"])]
    viviendas = [x[0] for x in arcpy.da.SearchCursor(CALIDAD_VIV_PRESEGM, ["UBIGEO"])]
    ubigeos = list(set(ccpps)|set(viviendas))
    return ubigeos



# DEFINE RESULTADOS EN LA BD

def generarTablaConsistencia(ubigeos_input=[], conn=conn):
    if len(ubigeos_input) == 0:
        ubigeos = ubigeosError(CALIDAD_CCPP_PRESEGM, CALIDAD_VIV_PRESEGM)
    else:
        ubigeos = ubigeos_input
    for ubigeo in ubigeos:
        cursor = conn.cursor()
        cursor.execute("EXEC USP_ACTUALIZA_CALIDAD_R_IMPUT '{}'".format(ubigeo))
        conn.commit()
        cursor.close()


#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::


# ACTUALIZA LOS UBIGEOS PARA SEGMENTAR



#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
