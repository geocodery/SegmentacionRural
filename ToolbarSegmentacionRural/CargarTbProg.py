import arcpy
import pymssql
import os
import re
from datetime import datetime
startTime = datetime.now()


arcpy.env.overwriteOutput = True
agregarGDB = arcpy.GetParameter(0)
arcpy.env.workspace = agregarGDB
nomubigeo = str(agregarGDB)[-10:-4]

def conectionGDB_arcpy(ip="172.18.1.93"):
    if arcpy.Exists("CPV_SEGMENTACION.sde") == False:
        arcpy.CreateDatabaseConnection_management("Database Connections",
                                                  'CPV_SEGMENTACION.sde',
                                                  'SQL_SERVER',
                                                  ip,
                                                  'DATABASE_AUTH',
                                                  'sde',
                                                  "$deDEs4Rr0lLo",
                                                  "#",
                                                  'GEODB_CPV_SEGM',
                                                  "#",
                                                  '#',
                                                  '#',
                                                  "#")
    conexionGDB = r'Database Connections\CPV_SEGMENTACION_GDB.sde'
    return conexionGDB

def conectionDB_pymmsql(user_sde="us_arcgis_seg_2", password_sde="MBs0p0rt301", ip="172.18.1.93", nombre='CPV_SEGMENTACION'):
    conexion = pymssql.connect(ip, user_sde, password_sde, nombre)
    return conexion

#Terminar Tabla Rutas
def compilarTablaRutas(gdb):
    listaTablas = arcpy.ListTables()
    list = []
    pattern = r"RUTA_"
    for i in listaTablas:
        if re.match(pattern, i):
            list.append(i)
    for i in list:
        campos = arcpy.ListFields(i)
        if "IDRUTA" not in [x.name for x in campos]:
            arcpy.AddField_management(i, "IDRUTA", "TEXT", '#', '#', "20", '#', 'NULLABLE', 'NON_REQUIRED', '#')
        with arcpy.da.UpdateCursor(i, ["IDRUTA"]) as cursor:
            for x in cursor:
                x[0] = str(i)[5:]
                cursor.updateRow(x)

        if "FEC_CARGA" not in [x.name for x in campos]:
            arcpy.AddField_management(i, "FEC_CARGA", "TEXT", '#', '#', "30", '#', 'NULLABLE', 'NON_REQUIRED', '#')
        with arcpy.da.UpdateCursor(i, ["FEC_CARGA"]) as cursor:
            for x in cursor:
                x[0] = startTime
                cursor.updateRow(x)

        if "FLAG_NUEVO" not in [x.name for x in campos]:
            arcpy.AddField_management(i, "FLAG_NUEVO", "SHORT", '1', '#', "#", '#', 'NULLABLE', 'NON_REQUIRED', '#')
        with arcpy.da.UpdateCursor(i, ["FLAG_NUEVO"]) as cursor:
            for x in cursor:
                x[0] = 1
                cursor.updateRow(x)

    TabRuta = arcpy.Copy_management(os.path.join(str(gdb), listaTablas[0]), "TabRuta_{}".format(nomubigeo))
    arcpy.DeleteRows_management(TabRuta)
    arcpy.Append_management(list, TabRuta, "NO_TEST")
    arcpy.AddField_management(TabRuta, "UBIGEO", "TEXT", '#', '#', "6", '#', 'NULLABLE', 'NON_REQUIRED', '#')
    arcpy.CalculateField_management(TabRuta, "UBIGEO", "'{}'".format(nomubigeo), "PYTHON_9.3")
    return TabRuta

# Terminar Tabla SCR
def compilarTablaSCR(gdb):
    listaTablas = arcpy.ListTables()
    list = []
    pattern = r"SCR_"
    for i in listaTablas:
        if re.match(pattern, i):
            list.append(i)
        else:
            pass
    for i in list:
        campos = arcpy.ListFields(i)
        if "IDSCR" in [x.name for x in campos]:
            pass
        else:
            arcpy.AddField_management(i, "IDSCR", "TEXT", '#', '#', "20", '#', 'NULLABLE', 'NON_REQUIRED', '#')
        with arcpy.da.UpdateCursor(i, ["IDSCR"]) as cursor:
            for x in cursor:
                x[0] = str(i)[4:]
                cursor.updateRow(x)
        if "FEC_CARGA" not in [x.name for x in campos]:
            arcpy.AddField_management(i, "FEC_CARGA", "TEXT", '#', '#', "30", '#', 'NULLABLE', 'NON_REQUIRED', '#')
        with arcpy.da.UpdateCursor(i, ["FEC_CARGA"]) as cursor:
            for x in cursor:
                x[0] = startTime
                cursor.updateRow(x)

        if "FLAG_NUEVO" not in [x.name for x in campos]:
            arcpy.AddField_management(i, "FLAG_NUEVO", "SHORT", '1', '#', "#", '#', 'NULLABLE', 'NON_REQUIRED', '#')
        with arcpy.da.UpdateCursor(i, ["FLAG_NUEVO"]) as cursor:
            for x in cursor:
                x[0] = 1
                cursor.updateRow(x)

    TabSCR = arcpy.Copy_management(os.path.join(str(gdb), list[0]), "TabSCR_{}".format(nomubigeo))
    arcpy.DeleteRows_management(TabSCR)
    arcpy.Append_management(list, TabSCR, "NO_TEST")
    arcpy.AddField_management(TabSCR, "UBIGEO", "TEXT", '#', '#', "6", '#', 'NULLABLE', 'NON_REQUIRED', '#')
    arcpy.CalculateField_management(TabSCR, "UBIGEO","'{}'".format(nomubigeo), "PYTHON_9.3")
    return TabSCR

#Agregar tablas de rutas llenadas
def cargarTablaAsigRuta(agregarTablaAsigRutas, conexionGDB, ubigeo):
    conexion = conectionDB_pymmsql()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM CPV_SEGMENTACION_GDB.SDE.SEGM_R_ASIGN_RUTA WHERE UBIGEO = '{}' AND FLAG_NUEVO = 1".format(ubigeo))
    conexion.commit()
    cursor.close()
    arcpy.Append_management(agregarTablaAsigRutas, r'{}\CPV_SEGMENTACION_GDB.SDE.SEGM_R_ASIGN_RUTA'.format(conexionGDB), "NO_TEST")

#Agregar tablas de SCR llenadas
def cargarTablaAsigSCR(agregarTablaAsigSCR, conexionGDB, ubigeo):
    conexion = conectionDB_pymmsql()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM CPV_SEGMENTACION_GDB.SDE.SEGM_R_ASIGN_SCR WHERE UBIGEO = '{}' AND FLAG_NUEVO = 1".format(ubigeo))
    conexion.commit()
    cursor.close()
    arcpy.Append_management(agregarTablaAsigSCR, r'{}\CPV_SEGMENTACION_GDB.SDE.SEGM_R_ASIGN_SCR'.format(conexionGDB), "NO_TEST")

def asignarEstado(ubigeo):
    conexion = conectionDB_pymmsql()
    cursor = conexion.cursor()
    cursor.execute("UPDATE TB_MODULO_ASIGN_R SET ESTADO = 3 WHERE UBIGEO = '{}'".format(ubigeo))
    conexion.commit()
    cursor.close()

def cargarTablas(TablaAsigRutas,TablaAsigSCR):
    ubigeo = nomubigeo
    arcpy.AddMessage(ubigeo)
    conexionGDB = conectionGDB_arcpy()
    cargarTablaAsigRuta(TablaAsigRutas, conexionGDB, ubigeo)
    cargarTablaAsigSCR(TablaAsigSCR, conexionGDB, ubigeo)
    # asignarEstado(ubigeo)
    arcpy.AddMessage("La carga se realizo con exito. \nPor favor espera la validacion del Jefe de equipo")


TablaAsigRutas = compilarTablaRutas(agregarGDB)
TablaAsigSCR = compilarTablaSCR(agregarGDB)
cargarTablas(TablaAsigRutas,TablaAsigSCR)


