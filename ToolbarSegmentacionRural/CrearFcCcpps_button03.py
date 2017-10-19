# -*- coding: utf-8 -*-

import arcpy, pymssql

arcpy.env.overwriteOutput = True

gdb = arcpy.GetParameter(0)

lyrCcpp = r'\\192.168.201.115\cpv2017\SegmentacionRural_Procesamiento\Insumos\CCPPRUTAS_FINAL.lyr'


# def conectionDB_pymmsql(user_sde="us_arcgis_app_desa", password_sde="m4Thu6uNEQaj", ip="172.18.1.41", nombre='CPV_SEGMENTACION'):
#     conexion = pymssql.connect(ip, user_sde, password_sde, nombre)
#     return conexion

#
# def cursorBD():
#     conn = conectionDB_pymmsql()
#     cursor = conn.cursor()
#     return cursor


def crearFeature(ccpps, dataset, ubigeo):

    nombreFc = 'CCPPRUTAS_{}'.format(ubigeo)
    ccpps_mfl = arcpy.MakeFeatureLayer_management(ccpps, 'ccpps', 'AREA <> 1')
    fc = arcpy.CopyFeatures_management(ccpps_mfl, "{}\{}".format(dataset, nombreFc))
    Campos_CCPPRUTAS = [("RUTA_TMP", "SHORT",  "2"), ("OR_CCPP", "SHORT", "5")]

    for n in Campos_CCPPRUTAS:
        if n[1] == "TEXT":
            arcpy.AddField_management(fc, n[0], n[1], '#', '#', n[2], '#', 'NULLABLE', 'NON_REQUIRED', '#')
        else:
            arcpy.AddField_management(fc, n[0], n[1], n[2], '#', '#', '#', 'NULLABLE', 'NON_REQUIRED', '#')

    return fc


def fcRutas(gdb, ubigeo):
    rutas = '{}\Procesamiento\RUTAS_{}'.format(gdb, ubigeo)
    return rutas


def fcCcpp(gdb, ubigeo):
    ccpps = '{}\Generales\CCPP_N_{}'.format(gdb, ubigeo)
    return ccpps


def consistencia01(rutas):
    informacion = [[1, x[0], x[1]] for x in arcpy.da.SearchCursor(rutas, ["OID@", "N_EMP_RUTA"]) if x[1] == None]
    return informacion


def consistencia02(rutas, ccpps):
    ccpps_mfl = arcpy.MakeFeatureLayer_management(ccpps, 'ccpps', 'AREA <> 1')
    seleccion = arcpy.SelectLayerByLocation_management(ccpps_mfl, "INTERSECT", rutas, "#", "NEW_SELECTION", "INVERT")
    informacion = [[2, x[0], x[1], x[2]] for x in arcpy.da.SearchCursor(seleccion , ["IDCCPP", "CODCCPP", "VIV_CCPP"])]
    return informacion


def consistencia03(rutas, ccpps):
    rutas_mfl = arcpy.MakeFeatureLayer_management(rutas, 'rutas')
    informacion = []
    for x in arcpy.da.SearchCursor(ccpps, ["SHAPE@", "IDCCPP", "CODCCPP", "VIV_CCPP"], "AREA <> 1"):
        seleccion = arcpy.SelectLayerByLocation_management(rutas_mfl, "INTERSECT", x[0], "#", "NEW_SELECTION", "NOT_INVERT")
        longitud = (arcpy.GetCount_management(seleccion))[0]
        if int(longitud) in (0, 1):
            pass
        else:
            informacion.append([3, x[1], x[2], x[2]])
    return informacion

#
# def consistencia04(ubigeo, ccpps):
#     informacion = []
#     cursor = cursorBD()
#     cursor.execute("SELECT CODCCPP FROM TB_CCPP WHERE UBIGEO = '{}'".format(ubigeo))
#     ccppBD = [x[0] for x in cursor]
#     ccppFC = [x[0] for x in arcpy.da.SearchCursor(ccpps, ["CODCCPP"])]
#     informacion_tmp1 = [[4, x] for x in ccppFC if x not in ccppBD]
#     informacion_tmp2 = [[5, x] for x in ccppBD if x not in ccppFC]
#     informacion.extend(informacion_tmp1)
#     informacion.extend(informacion_tmp2)
#     return informacion


def actualizarRegistros(rutas, output):
    ccpps_mfl = arcpy.MakeFeatureLayer_management(output, 'ccpps_out')
    for x in arcpy.da.SearchCursor(rutas, ["SHAPE@", "OID@"]):
        seleccion = arcpy.SelectLayerByLocation_management(ccpps_mfl, "INTERSECT", x[0], "#", "NEW_SELECTION", "NOT_INVERT")
        arcpy.CalculateField_management(seleccion, "RUTA_TMP", x[1])


def validarGDB(gdb):
    informacion = []
    desc = arcpy.Describe(gdb)
    validacion = desc.basename

    if validacion[0:10] == 'BD_SEGM_R_':
        if arcpy.Exists(r'{}\Procesamiento'.format(gdb)):
            ubigeo = validacion[10:16]
            dataset = r'{}\Procesamiento'.format(gdb)

            if arcpy.Exists(r'{}\Procesamiento\RUTAS_{}'.format(gdb, ubigeo)):
                rutas = fcRutas(gdb, ubigeo)
                ccpps = fcCcpp(gdb, ubigeo)
                con01 = consistencia01(rutas)
                con02 = consistencia02(rutas, ccpps)
                con03 = consistencia03(rutas, ccpps)
                # con04 = consistencia04(ubigeo, ccpps)

                if len(con01) > 0 or len(con02) > 0 or len(con03) > 0:
                    informacion.extend(con01)
                    informacion.extend(con02)
                    informacion.extend(con03)
                    # informacion.extend(con04)
                    for x in informacion:
                        if x[0] == 1:
                            arcpy.AddWarning("La ruta FID:{}; no presenta cantidad de empadronadores".format(x[1]))
                        elif x[0] == 2:
                            arcpy.AddWarning(
                                "El centro poblado {} | {} | {} no tiene una ruta asociada".format(x[1], x[2], x[3]))
                        elif x[0] == 3:
                            arcpy.AddWarning(
                                "El centro poblado {} | {} | {} esta asociado a mas de una ruta".format(x[1], x[2],x[3]))
                        elif x[0] == 4:
                            arcpy.AddWarning("El centro poblado {} no existe en la base de datos (posiblemente agrego un centro poblado nuevo)".format(x[1]))
                        elif x[0] == 5:
                            arcpy.AddWarning("El centro poblado {} no se encuentra o fue eliminado, asegurese de que todos los centros poblados RURALES del distrito se encuentren presentes en la Segmentacion".format(x[1]))

                else:
                    output = crearFeature(ccpps, dataset, ubigeo)
                    actualizarRegistros(rutas, output)
                    arcpy.SetParameterAsText(1, output)

                    params = arcpy.GetParameterInfo()

                    for param in params:
                        if '{}'.format(param.name) == 'ccpp':
                            param.symbology = lyrCcpp

            else:
                arcpy.AddError("OBSERVACION:")
                arcpy.AddError("Debes realizar la asignacion de rutas")
        else:
            arcpy.AddError("OBSERVACION:")
            arcpy.AddError("No se encuentra el dataset 'Procesamiento' dentro de la GDB ingresada")
    else:
        arcpy.AddError("OBSERVACION:")
        arcpy.AddError("Ingrese la GDB correcta")


validarGDB(gdb)


