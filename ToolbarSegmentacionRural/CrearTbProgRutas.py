# -*- #################

import arcpy
arcpy.env.overwriteOutput = True

gdb = arcpy.GetParameter(0)

nomubigeo = str(gdb)[-10:-4]

def crearTablaRuta(Ruta):
    nombreTb = 'RUTA_{}'.format(Ruta)
    Campos_RUTAS = [("DIA_RUTA", "SHORT", "2"), ("CODCCPP_RUTA", "TEXT", "4"), ("TIPO_RUTA", "TEXT", "2"), ("COSTO_RUTA", "SHORT", "3")]
    tb_temp = arcpy.CreateTable_management('{}\\'.format(gdb), nombreTb)

    for n in Campos_RUTAS:
        if n[1] == "TEXT":
            arcpy.AddField_management(tb_temp, n[0], n[1], '#', '#', n[2], '#', 'NULLABLE', 'NON_REQUIRED', '#')
        else:
            arcpy.AddField_management(tb_temp, n[0], n[1], n[2], '#', '#', '#', 'NULLABLE', 'NON_REQUIRED', '#')

# Extraer nombres de tablas
lista_RUTA_temp = []

with arcpy.da.SearchCursor("SEGM_R_CCPPRUTA_{}".format(nomubigeo),["IDRUTA"]) as cursor:
    for x in cursor:
        lista_RUTA_temp.append(x[0])
    lista_RUTA = dict.fromkeys(lista_RUTA_temp).keys()
    lista_RUTA.sort()

for i in lista_RUTA:
    crearTablaRuta(i)





















