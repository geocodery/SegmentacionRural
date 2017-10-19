from Generales import settings, funcionesGenerales
import arcpy

SEGM_R_CCPPRUTA = r'Database Connections\CPV_SEGMENTACION.sde\CPV_SEGMENTACION.dbo.SEGM_R_CCPPRUTA'
SEGM_R_RUTA = r'Database Connections\CPV_SEGMENTACION.sde\CPV_SEGMENTACION.dbo.SEGM_R_RUTA'
RUTA = r'Database Connections\CPV_SEGMENTACION_GDB.sde\CPV_SEGMENTACION_GDB.SDE.MODULO_SEGM_RURAL\CPV_SEGMENTACION_GDB.SDE.SEGM_R_RUTA'
CCPPRUTA = r'Database Connections\CPV_SEGMENTACION_GDB.sde\CPV_SEGMENTACION_GDB.SDE.MODULO_SEGM_RURAL\CPV_SEGMENTACION_GDB.SDE.SEGM_R_CCPPRUTA'

conn = settings.conectionDB_pymmsql()
settings.conectionGDB_arcpy()
settings.conectionDB_arcpy()

def actualizaRutas(ubigeo):
    cursorsql2 = conn.cursor()
    cursorsql2.execute("EXEC ACTUALIZAR_RUTAS '{}'".format(ubigeo))
    conn.commit()
    cursorsql2.close()


def agregarCategoria(conn=conn):
    cursor = conn.cursor()
    cursor.execute("UPDATE A SET A.CAT_CCPP = B.CATEGORIA_O FROM CPV_SEGMENTACION_GDB.SDE.SEGM_R_CCPPRUTA AS A INNER JOIN CPV_SEGMENTACION_GDB.sde.TB_CCPP AS B ON A.IDCCPP COLLATE DATABASE_DEFAULT = B.LLAVE_CCPP COLLATE DATABASE_DEFAULT WHERE A.CAT_CCPP IS NULL")
    conn.commit()
    cursor.close()


def agregarAers(conn=conn):
    cursor = conn.cursor()
    cursor.execute("UPDATE A SET A.IDAER = B.IDAER, A.AER_INI = B.AER_INI, A.AER_FIN = B.AER_FIN FROM CPV_SEGMENTACION_GDB.sde.SEGM_R_CCPPRUTA  AS A INNER JOIN CPV_SEGMENTACION_GDB.sde.TB_CCPP AS B ON A.IDCCPP COLLATE DATABASE_DEFAULT = B.LLAVE_CCPP COLLATE DATABASE_DEFAULT WHERE A.AER_INI IS NULL")
    conn.commit()
    cursor.close()
    cursor2 = conn.cursor()
    cursor2.execute("UPDATE CPV_SEGMENTACION_GDB.SDE.SEGM_R_CCPPRUTA SET AER_INI = SUBSTRING(IDAER, 7, 3), AER_FIN = SUBSTRING(IDAER, 10, 3) WHERE IDAER IS NOT NULL AND(AER_INI IS NULL)")
    conn.commit()
    cursor2.close()


# CAMBIAR EL VALOR A 4 PARA LA FASE REAL DE SEGMENTACION

def ubigeosProcesar(conn=conn):
    cursor = conn.cursor()
    cursor.execute("SELECT UBIGEO FROM TB_MODULO_ASIGN_R WHERE UBIGEO NOT IN ('110205', '160104', '120704', '130501') AND ESTADO = 3")
    informacion = [x[0] for x in cursor]
    cursor.close()
    return informacion

def eliminarRegistrosCcppruta(ubigeos, conn=conn):
    sql = funcionesGenerales.Expresion(ubigeos, "#", "UBIGEO")
    cursor = conn.cursor()
    # cursor.execute("DELETE FROM SEGM_R_CCPPRUTA WHERE {}".format(sql)) # FLUJO NORMAL
    cursor.execute("DELETE FROM SEGM_R_CCPPRUTA WHERE {} AND FLAG_NUEVO = 1".format(sql)) # FLUJO CCPP NUEVOS
    conn.commit()
    informacion = [x[0] for x in cursor]
    cursor.close()
    return informacion


def eliminarRegistrosRuta(ubigeos, conn = conn):
    sql = funcionesGenerales.Expresion(ubigeos, "#", "UBIGEO")
    cursor = conn.cursor()
    # cursor.execute("DELETE FROM SEGM_R_RUTA WHERE {}".format(sql))                    # FLUJO NORMAL
    cursor.execute("DELETE FROM SEGM_R_RUTA WHERE {} AND FLAG_NUEVO = 1".format(sql))   # FLUJO CCPP NUEVOS
    conn.commit()
    informacion = [x[0] for x in cursor]
    cursor.close()
    return informacion


def dataccppruta(ubigeos, CCPPRUTA):
    sql = funcionesGenerales.Expresion(ubigeos, "#", "UBIGEO")
    # mfl = arcpy.MakeFeatureLayer_management(CCPPRUTA, "ccppruta_mfl", sql)                        # FLUJO NORMAL
    # tb = arcpy.TableToTable_conversion(mfl, 'in_memory', 'ccppruta', sql)                         # FLUJO NORMAL
    mfl = arcpy.MakeFeatureLayer_management(CCPPRUTA, "ccppruta_mfl", sql + "AND FLAG_NUEVO = 1")  # FLUJO CCPP NUEVOS
    tb = arcpy.TableToTable_conversion(mfl, 'in_memory', 'ccppruta', sql + "AND FLAG_NUEVO = 1 ")   # FLUJO CCPP NUEVOS
    return tb


def dataruta(ubigeos, RUTA):
    sql = funcionesGenerales.Expresion(ubigeos, "#", "UBIGEO")
    # mfl = arcpy.MakeFeatureLayer_management(RUTA, "ruta_mfl", sql)        # FLUJO NORMAL
    # tb = arcpy.TableToTable_conversion(mfl, 'in_memory', 'ruta', sql)     # FLUJO NORMAL
    mfl = arcpy.MakeFeatureLayer_management(RUTA, "ruta_mfl", sql + "AND FLAG_NUEVO = 1 ")          # FLUJO CCPP NUEVOS
    tb = arcpy.TableToTable_conversion(mfl, 'in_memory', 'ruta', sql + "AND FLAG_NUEVO = 1 ")       # FLUJO CCPP NUEVOS
    return tb



def insertarDataCcppruta(tabla, SEGM_R_CCPPRUTA):
    arcpy.Append_management(tabla, SEGM_R_CCPPRUTA, "NO_TEST")


def insertarDataruta(tabla, SEGM_R_RUTA):
    arcpy.Append_management(tabla, SEGM_R_RUTA, "NO_TEST")


def insertarInformacion(ubigeos_input=[]):
    agregarCategoria()
    agregarAers()
    if len(ubigeos_input) == 0:
        ubigeos = ubigeosProcesar()
        print ubigeos
    else:
        ubigeos = ubigeos_input
    eliminarRegistrosCcppruta(ubigeos)
    eliminarRegistrosRuta(ubigeos)
    tbccppruta = dataccppruta(ubigeos, CCPPRUTA)
    tbruta = dataruta(ubigeos, RUTA)

    insertarDataCcppruta(tbccppruta, SEGM_R_CCPPRUTA)
    insertarDataruta(tbruta, SEGM_R_RUTA)
