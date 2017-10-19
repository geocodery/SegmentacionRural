# -*- #################

import arcpy
arcpy.env.overwriteOutput = True

gdb = arcpy.GetParameter(0)

nomubigeo = str(gdb)[-10:-4]

def crearTablaSCR(SCR):
    nombreTb = 'SCR_{}'.format(SCR)
    Campos_SCR = [("DIA_SCR", "SHORT", "2"), ("CODCCPP_SCR", "TEXT", "4"), ("TIPO_SCR", "TEXT", "2"), ("COSTO_SCR", "SHORT", "3")]
    tb_temp = arcpy.CreateTable_management('{}\\'.format(gdb), nombreTb)

    for n in Campos_SCR:
        if n[1] == "TEXT":
            arcpy.AddField_management(tb_temp, n[0], n[1], '#', '#', n[2], '#', 'NULLABLE', 'NON_REQUIRED', '#')
        else:
            arcpy.AddField_management(tb_temp, n[0], n[1], n[2], '#', '#', '#', 'NULLABLE', 'NON_REQUIRED', '#')

# Extraer nombres de tablas
lista_SCR_temp = []

with arcpy.da.SearchCursor("SEGM_R_CCPPRUTA_{}".format(nomubigeo),["IDSCR"]) as cursor:
    for x in cursor:
        lista_SCR_temp.append(x[0])
    lista_SCR = dict.fromkeys(lista_SCR_temp).keys()
    lista_SCR.sort()

for i in lista_SCR:
    crearTablaSCR(i)



