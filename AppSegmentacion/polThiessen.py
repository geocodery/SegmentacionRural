import arcpy
import os
from Generales import settings
from settings import conectionGDB_Monitoreo, conectionGDB_Monitoreo_pymmsql

arcpy.env.overwriteOutput = True

conn = settings.conectionDB_pymmsql()
conexionDB = settings.conectionDB_arcpy()

def polThiessen(ubigeo):
    arcpy.env.extent = r'D:\SegmentacionRuralV2\Insumos\CapasAuxiliares\CapasAuxiliares.gdb\TB_AREA'
    carpeta = r'D:\SegmentacionRuralV2\Procesamiento\Segmentacion'

    distritos_mql = arcpy.MakeQueryLayer_management(conexionDB, "DIST",
                                               "SELECT*FROM CPV_SEGMENTACION_GDB.sde.TB_LIMITE_DIS WHERE UBIGEO = '{}'".format(ubigeo), "UBIGEO",
                                               "POLYGON", '4326', arcpy.SpatialReference(4326))
    ccpp_mql = arcpy.MakeQueryLayer_management(conexionDB, "CCPP",
                                           "SELECT * FROM CPV_SEGMENTACION_GDB.SDE.TB_CCPP where UBIGEO = '{}' AND AREA = '2'".format(ubigeo),'LLAVE_CCPP',
                                           'POINT', '4326', arcpy.SpatialReference(4326))

    distritos_mfl = arcpy.MakeFeatureLayer_management(distritos_mql, "distritos_mfl")
    ccpp_mfl = arcpy.MakeFeatureLayer_management(ccpp_mql, "ccpp_mfl")

    distritos = arcpy.CopyFeatures_management(distritos_mfl, os.path.join(carpeta, 'PoligonosSCR.gdb', 'distritos'))
    ccpp = arcpy.CopyFeatures_management(ccpp_mfl, os.path.join(carpeta, 'PoligonosSCR.gdb', 'ccpp'))

    thiessenPol = arcpy.CreateThiessenPolygons_analysis(ccpp, os.path.join(carpeta, 'PoligonosSCR.gdb', 'thiessen1'), "ALL")
    ThiessenDissol = arcpy.Dissolve_management(thiessenPol, os.path.join(carpeta, 'PoligonosSCR.gdb', 'thiessen2'), "IDSCR;UBIGEO")
    Thiessen = arcpy.Clip_analysis(ThiessenDissol, distritos, os.path.join(carpeta, 'PoligonosSCR.gdb', 'thiessenFinal'))

    del distritos_mql
    del ccpp_mql

    return Thiessen

def cargarThiessenSCR(agregarPoligono, ubigeo):
    conexionGDB = conectionGDB_Monitoreo()
    conexion = conectionGDB_Monitoreo_pymmsql()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM CPV_MONITOREO_GIS.SDE.CARTO_R_SECCION WHERE UBIGEO = '{}'".format(ubigeo))
    conexion.commit()
    cursor.close()
    arcpy.Append_management(agregarPoligono,r'{}\CPV_MONITOREO_GIS.SDE.CPV2017\CPV_MONITOREO_GIS.SDE.CARTO_R_SECCION'.format(conexionGDB), "NO_TEST")

def actualizarTablasThiessen(ubigeo, fase):
    conexion = conectionGDB_Monitoreo_pymmsql()
    cursor = conexion.cursor()
    cursor.execute("UPDATE CPV_MONITOREO_GIS.SDE.CARTO_R_SECCION SET SECCION = substring(IDSCR,12,3), ZONA = '00000', FASE = '{}' WHERE UBIGEO = '{}'".format(fase, ubigeo))
    conexion.commit()
    cursor.close()

def crearThiessen(ubigeo, fase):
    areaSecciones = polThiessen(ubigeo)
    cargarThiessenSCR(areaSecciones, ubigeo)
    actualizarTablasThiessen(ubigeo, fase)

