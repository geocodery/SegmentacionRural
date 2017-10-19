# -*- coding: utf-8 -*-

import arcpy

arcpy.env.overwriteOutput = True

gdb = arcpy.GetParameter(0)

lyrRuta = r'\\192.168.201.115\cpv2017\SegmentacionRural_Procesamiento\Insumos\RUTA_FINAL.lyr'

def crearFeature(ubigeo, dataset):

    nombreFc = 'RUTAS_{}'.format(ubigeo)
    Campos_RUTAS = [("UBIGEO", "TEXT", "6"), ("N_EMP_RUTA", "SHORT", "5")]
    fc_tmp = arcpy.CreateFeatureclass_management("in_memory", '{}_TMP'.format(nombreFc), "POLYGON", "#", "#", "#", arcpy.SpatialReference(4326))

    for n in Campos_RUTAS:
        if n[1] == "TEXT":
            arcpy.AddField_management(fc_tmp, n[0], n[1], '#', '#', n[2], '#', 'NULLABLE', 'NON_REQUIRED', '#')
        else:
            arcpy.AddField_management(fc_tmp, n[0], n[1], n[2], '#', '#', '#', 'NULLABLE', 'NON_REQUIRED', '#')

    rutas = arcpy.CreateFeatureclass_management(dataset, nombreFc, "POLYGON", fc_tmp, "#", "#", arcpy.SpatialReference(4326))

    arcpy.AssignDefaultToField_management(rutas, 'UBIGEO', ubigeo)

    return rutas


def validarGDB(gdb):
    desc = arcpy.Describe(gdb)
    validacion = desc.basename
    if validacion[0:10] == 'BD_SEGM_R_':
        if arcpy.Exists(r'{}\Procesamiento'.format(gdb)):
            ubigeo = validacion[10:16]
            dataset = r'{}\Procesamiento'.format(gdb)

            output = crearFeature(ubigeo, dataset)
            arcpy.SetParameterAsText(1, output)
            params = arcpy.GetParameterInfo()

            for param in params:
                if '{}'.format(param.name) == 'rutas':
                    param.symbology = lyrRuta
        else:
            arcpy.AddError("OBSERVACION:")
            arcpy.AddError("No se encuentra el dataset 'Procesamiento' dentro de la GDB ingresada")
    else:
        arcpy.AddError("OBSERVACION:")
        arcpy.AddError("Ingrese la GDB correcta")


validarGDB(gdb)








