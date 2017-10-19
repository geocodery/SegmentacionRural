#   CONEXIONNES A LA BD MSSQL

import arcpy
import pymssql

arcpy.env.overwriteOutput = True

ip = "172.18.1.93"
nombrebd = "CPV_SEGMENTACION"

def conectionDB_arcpy():
    if arcpy.Exists("TMP_CPV_SEGMENTACION.sde") == False:
        arcpy.CreateDatabaseConnection_management("Database Connections",
                                                  "{}.sde".format(nombrebd),
                                                  "SQL_SERVER",
                                                  ip,
                                                  "DATABASE_AUTH",
                                                  "us_arcgis_seg_2",
                                                  "MBs0p0rt301",
                                                  "#",
                                                  nombrebd,
                                                  "#",
                                                  "#",
                                                  "#",
                                                  "#")
    conexionDB = r'Database Connections\{}.sde'.format(nombrebd)
    return conexionDB

def conectionDB_pymmsql():
    ip = "172.18.1.93"
    user_sde = "us_arcgis_seg_2"
    password_sde = "MBs0p0rt301"
    nombrebd = "CPV_SEGMENTACION"
    conexion = pymssql.connect(ip, user_sde, password_sde, nombrebd)
    return conexion

def conectionGDB_arcpy():
    ip = "172.18.1.93"
    if arcpy.Exists("CPV_SEGMENTACION_GDB.sde") == False:
        arcpy.CreateDatabaseConnection_management("Database Connections",
                                                  'CPV_SEGMENTACION_GDB.sde',
                                                  'SQL_SERVER',
                                                  ip,
                                                  'DATABASE_AUTH',
                                                  'sde',
                                                  "$deDEs4Rr0lLo",
                                                  "#",
                                                  'CPV_SEGMENTACION_GDB',
                                                  "#",
                                                  '#',
                                                  '#',
                                                  "#")
    conexionGDB = r'Database Connections\CPV_SEGMENTACION_GDB.sde\CPV_SEGMENTACION_GDB.SDE.RURAL'
    return conexionGDB

def conectionGDB_pymmsql():
    user_sde = "sde"
    password_sde = "$deDEs4Rr0lLo"
    nombrebd = 'CPV_SEGMENTACION_GDB'
    conexion = pymssql.connect(ip, user_sde, password_sde, nombrebd)
    return conexion

def conectionGDB_Monitoreo_pymmsql():
    ip = '192.168.202.84'
    user_sde = "sde"
    password_sde = "wruvA7a*tat*"
    nombrebd = 'CPV_MONITOREO_GIS'
    conexion = pymssql.connect(ip, user_sde, password_sde, nombrebd)
    return conexion


def conectionGDB_Monitoreo():
    ip = '192.168.202.84'
    if arcpy.Exists("CPV_MONITOREO_GIS.sde") == False:
        arcpy.CreateDatabaseConnection_management("Database Connections",
                                                  "CPV_MONITOREO_GIS.sde",
                                                  "SQL_SERVER",
                                                  ip,
                                                  "DATABASE_AUTH",
                                                  "sde",
                                                  "wruvA7a*tat*",
                                                  "#",
                                                  "CPV_MONITOREO_GIS",
                                                  "#",
                                                  "#",
                                                  "#",
                                                  "#")

    conexionDB = r'Database Connections\{}.sde'.format("CPV_MONITOREO_GIS")
    return conexionDB
