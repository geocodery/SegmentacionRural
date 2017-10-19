# DECLARANDO FUNCIONES GENERALES

# IMPORTS

import arcpy
import time
import shutil
import os

# GENERA UNA EXPRESION SQL MUY EXTENSA

def Expresion(where_list, orden, campo):
    m=0
    where_expression=""
    if orden=="#":
        for x in where_list:
            if (m+1)==len(where_list):
                where_expression = where_expression +"{}='{}'".format(campo,x)
            else:
                where_expression = where_expression +"{}='{}' OR ".format(campo,x)
            m=m+1
        return  where_expression
    else:
        for x in where_list:
            if (m+1)==len(where_list):
                where_expression = where_expression +"{}='{}'".format(campo,x[orden])
            else:
                where_expression = where_expression +"{}='{}' OR ".format(campo,x[orden])
            m=m+1
        return  where_expression


def Plantillas_TMP(carpeta):
    list_fc = []
    fecha = time.strftime('%d%b%y')
    hora = time.strftime('%H%M%S')
    nameFile = "Proceso-{}-{}".format(fecha, hora)
    FILE = arcpy.CreateFolder_management(carpeta, nameFile)
    GDB = arcpy.CreatePersonalGDB_management(FILE, "Segmentacion Rural", "10.0")

    FcOriginales = arcpy.CreateFeatureDataset_management(GDB, "Insumos Originales", arcpy.SpatialReference(4326))

    FC = [["DIST", "POLYGON"], ["AER", "POLYGON"], ["CCPP", "POINT"], ["VIV", "POINT"]]

    Campos_AER = [("UBIGEO", "TEXT", "6"), ("IDAER", "TEXT", "12"),("AER_INI", "TEXT", "3"), ("AER_FIN", "TEXT", "3"),
                  ("CCPP_AER", "SHORT", "3"), ("VIV_AER", "SHORT", "5"), ("AER_POS", "TEXT", "2")]
    Campos_VIV = [("UBIGEO", "TEXT", "6"), ("CODCCPP", "TEXT", "4"), ("AREA", "SHORT", "1"),
                  ("ID_REG_OR", "SHORT", "4"), ("P29", "SHORT", "1"), ("P29M", "SHORT", "1"),
                  ("OR_VIV_RUTA", "SHORT", "5"), ("OR_CCPP_DIST", "SHORT", "5"), ("IDVIV", "TEXT", "14"), ("IDCCPP", "TEXT", "10"),
                  ("IDRUTA", "TEXT", "17"), ("IDSCR", "TEXT", "14"), ("IDAER", "TEXT", "12")]
    Campos_CCPP = [("UBIGEO", "TEXT", "6"), ("CODCCPP", "TEXT", "4"), ("AREA", "SHORT", "1"), ("VIV_CCPP", "SHORT", "6"),
                   ("IDCCPP", "TEXT", "10"), ("IDRUTA", "TEXT", "17"), ("IDSCR", "TEXT", "14"), ("IDAER", "TEXT", "12")]
    Campos_DIST = [("UBIGEO", "TEXT", "6"), ("REGION", "SHORT", "1"), ("REGION_NAT", "TEXT", "10")]

    for i in FC:
        fc_tmp = arcpy.CreateFeatureclass_management("in_memory", i[0], i[1], "#", "#", "#",
                                                     arcpy.SpatialReference(4326))
        if i[0] == "DIST":
            for n in Campos_DIST:
                if n[1] == "TEXT":
                    arcpy.AddField_management(fc_tmp, n[0], n[1], '#', '#', n[2], '#', 'NULLABLE', 'NON_REQUIRED', '#')
                else:
                    arcpy.AddField_management(fc_tmp, n[0], n[1], n[2], '#', '#', '#', 'NULLABLE', 'NON_REQUIRED', '#')
        elif i[0] == "AER":
            for n in Campos_AER:
                if n[1] == "TEXT":
                    arcpy.AddField_management(fc_tmp, n[0], n[1], '#', '#', n[2], '#', 'NULLABLE', 'NON_REQUIRED', '#')
                else:
                    arcpy.AddField_management(fc_tmp, n[0], n[1], n[2], '#', '#', '#', 'NULLABLE', 'NON_REQUIRED', '#')
        elif i[0] == "CCPP":
            for n in Campos_CCPP:
                if n[1] == "TEXT":
                    arcpy.AddField_management(fc_tmp, n[0], n[1], '#', '#', n[2], '#', 'NULLABLE', 'NON_REQUIRED', '#')
                else:
                    arcpy.AddField_management(fc_tmp, n[0], n[1], n[2], '#', '#', '#', 'NULLABLE', 'NON_REQUIRED', '#')
        else:
            for n in Campos_VIV:
                if n[1] == "TEXT":
                    arcpy.AddField_management(fc_tmp, n[0], n[1], '#', '#', n[2], '#', 'NULLABLE', 'NON_REQUIRED', '#')
                else:
                    arcpy.AddField_management(fc_tmp, n[0], n[1], n[2], '#', '#', '#', 'NULLABLE', 'NON_REQUIRED', '#')

        dato = arcpy.CreateFeatureclass_management(FcOriginales, i[0], i[1], fc_tmp, "#", "#",
                                                   arcpy.SpatialReference(4326))
        list_fc.append(dato)
    return list_fc


def Expresion_DB(where_list,orden,campo):
    m=0
    where_expression=""
    if orden=="#":
        for x in where_list:
            if (m+1)==len(where_list):
                where_expression = where_expression +"{}='{}'".format(campo,x)
            else:
                where_expression = where_expression +"{}='{}' OR ".format(campo,x)
            m=m+1
        return  where_expression
    else:
        for x in where_list:
            if (m+1)==len(where_list):
                where_expression = where_expression +"{}='{}'".format(campo,x[orden])
            else:
                where_expression = where_expression +"{}='{}' OR ".format(campo,x[orden])
            m=m+1
        return  where_expression


def Crear_Carpetas_Croquis_AER(PathFileServer, ubigeos, tipo):
    if tipo == 1:
        if os.path.exists(PathFileServer + '\{}'.format("Rural")) == False:
            for ubigeo in ubigeos:
                os.mkdir(PathFileServer + '\Rural\{}'.format(ubigeo))
        else:
            folder_list = os.listdir(PathFileServer + '\{}'.format("Rural"))
            for ubigeo in ubigeos:
                if ubigeo in folder_list:
                    shutil.rmtree(PathFileServer + '\{}'.format("Rural") + '\{}'.format(ubigeo))
                    os.mkdir(PathFileServer + '\Rural\{}'.format(ubigeo))
                else:
                    os.mkdir(PathFileServer + '\Rural\{}'.format(ubigeo))
    else:
        if os.path.exists(PathFileServer + '\{}'.format("Rural_FEN")) == False:
            for ubigeo in ubigeos:
                os.mkdir(PathFileServer + '\Rural_FEN\{}'.format(ubigeo))
        else:
            folder_list = os.listdir(PathFileServer + '\{}'.format("Rural_FEN"))
            for ubigeo in ubigeos:
                if ubigeo in folder_list:
                    shutil.rmtree(PathFileServer + '\{}'.format("Rural_FEN") + '\{}'.format(ubigeo))
                    os.mkdir(PathFileServer + '\Rural_FEN\{}'.format(ubigeo))
                else:
                    os.mkdir(PathFileServer + '\Rural_FEN\{}'.format(ubigeo))


def Crear_Carpetas_FileServer(PathFileServer, ubigeos, fase, tipo):
    if tipo == 1:
        if os.path.exists(PathFileServer + '\{}'.format("Rural")) == False:
            for ubigeo in ubigeos:
                os.mkdir(PathFileServer + '\Rural\{}\{}'.format(fase, ubigeo))
        else:
            folder_list = os.listdir(PathFileServer + '\{}'.format("Rural") + '\{}'.format(fase))
            for ubigeo in ubigeos:
                if ubigeo in folder_list:
                    shutil.rmtree(PathFileServer + '\{}'.format("Rural") + '\{}'.format(fase) + '\{}'.format(ubigeo))
                    os.mkdir(PathFileServer + '\Rural\{}\{}'.format(fase, ubigeo))
                else:
                    os.mkdir(PathFileServer + '\Rural\{}\{}'.format(fase, ubigeo))
    else:
        pass
