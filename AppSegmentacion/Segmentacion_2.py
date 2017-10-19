
#::::::::::::::::::: ETAPA NUMERO UNO DE LA SEGMENTACION AUTOMATIZADA ---> AGRUPACION DE AERS ::::::::::::::::

'''
Censo Nacional de Poblacion y Vivienda
Segementacion Rural Atutomatizada
Daniel Aguado HuacCharaqui
Oficina Tecnica de Informatica
'''

from Generales import settings
from Generales.funcionesGenerales import*
from settings import conectionGDB_Monitoreo, conectionGDB_Monitoreo_pymmsql


arcpy.env.overwriteOutput = True

#    ACTUALIZACION DE CAMPOS NECESARIOS ANTES DE REALIZAR LA SEGMENTACION

def ActualizarJefeHogar(ubigeos_originales, conexion):
    for ubigeo in ubigeos_originales:
        cursor2 = conexion.cursor()
        cursor2.execute("EXEC ACTUALIZAR_JEFE_HOGAR '{}', '99999', '2'".format(ubigeo))
        conexion.commit()
        cursor2.close()

def ActualizarFlagSegmRural(ubigeo, conexion):
    cursor = conexion.cursor()
    cursor.execute("UPDATE MARCO_DISTRITO SET FLAG_SEGM_R = '1' WHERE UBIGEO = '{}'".format(ubigeo))
    conexion.commit()
    cursor.close()

def actualizarAsignacion(ubigeo,conexion):
    cursor = conexion.cursor()
    sql = "EXEC USP_ACTUALIZA_ASIGN_RURAL '{}'".format(ubigeo)
    cursor.execute(sql)
    conexion.commit()
    cursor.close()

def actualizarRegistrosRuralMonitoreo(conexion):
    cursor = conexion.cursor()
    sql = "EXEC USP_ACTUALIZAR_REGISTROS_RURAL_CPV_SEGMENTACION"
    cursor.execute(sql)
    conexion.commit()
    cursor.close()

def SegmentacionRural(carpeta, DIST_FC_ORIG, Coneccion_SDE, ConexionGDB, SEGM_R_AER, SEGM_R_CCPP, SEGM_R_VIV, SEGM_R_AER_POST):

    conexion = settings.conectionDB_pymmsql()
    cursor = conexion.cursor()

    cursor.execute("update  CPV_SEGMENTACION_GDB.sde.TB_VIVIENDA_R set IDVIV = ubigeo + codccpp + right('000' + CAST(isnull (id_reg_or, 0) as varchar(4)), 4)")
    conexion.commit()
    cursor.execute("update CPV_SEGMENTACION_GDB.sde.TB_CPV0301_VIVIENDA_R set IDVIV = ubigeo + codccpp + right('000' + CAST(isnull (id_reg_or, 0) as varchar(4)), 4)")
    conexion.commit()

    #    SELECCION DE UBIGEOS A PROCESAR

    ubigeos_originales = [x[0] for x in arcpy.da.SearchCursor(DIST_FC_ORIG, ["UBIGEO"])]

    ActualizarJefeHogar(ubigeos_originales, conexion)

    sql = Expresion(ubigeos_originales, "#", "UBIGEO")

    AER_FC_ORIG_mfl_0 = arcpy.MakeQueryLayer_management(Coneccion_SDE, 'AER_mfl', "SELECT * FROM  CPV_SEGMENTACION_GDB.sde.TB_AER where {}".format(sql), 'UBIGEO;AER_INI;AER_FIN', 'POLYGON', '4326', arcpy.SpatialReference(4326))

    CCPP_FC_ORIG_mfl_0 = arcpy.MakeQueryLayer_management(Coneccion_SDE, "CCPP_mfl", "SELECT * FROM CPV_SEGMENTACION_GDB.sde.TB_CCPP where {}".format(sql), 'LLAVE_CCPP', 'POINT', '4326', arcpy.SpatialReference(4326))

    VIV_FC_ORIG_mfl_0 = arcpy.MakeQueryLayer_management(Coneccion_SDE, 'VIV_mfl', "SELECT * FROM VW_R_VIV where {}".format(sql), 'IDVIV', 'POINT', '4326', arcpy.SpatialReference(4326))


    ubigeo_aer = list(set([x[0] for x in arcpy.da.SearchCursor(AER_FC_ORIG_mfl_0, ["UBIGEO"])]))
    ubigeo_ccpp = list(set([x[0] for x in arcpy.da.SearchCursor(CCPP_FC_ORIG_mfl_0, ["UBIGEO"])]))
    ubigeo_viv = list(set([x[0] for x in arcpy.da.SearchCursor(VIV_FC_ORIG_mfl_0, ["UBIGEO"])]))


    longitudes = [[ubigeo_aer, len(ubigeo_aer)], [ubigeo_ccpp, len(ubigeo_ccpp)], [ubigeo_viv, len(ubigeo_viv)]]

    if 0 not in [x[1] for x in longitudes]:

        longitudes.sort(key = lambda minimo:minimo[1], reverse = False)

        for ubigeo in longitudes[0][0]:
            if ubigeo in longitudes[1][0] and ubigeo in longitudes[2][0]:
                continue
            else:
                (longitudes[0][0]).remove(ubigeo)

        UbigeosParaProcesar = longitudes[0][0]

        sql2 = Expresion(UbigeosParaProcesar, "#", "UBIGEO")
        print sql2

        DIST_FC_ORIG_mfl = arcpy.MakeFeatureLayer_management(DIST_FC_ORIG, "distrito", sql2)
        AER_FC_ORIG_mfl = arcpy.MakeFeatureLayer_management(AER_FC_ORIG_mfl_0, "aer", sql2)
        CCPP_FC_ORIG_mfl = arcpy.MakeFeatureLayer_management(CCPP_FC_ORIG_mfl_0, "ccpp", sql2)
        VIV_FC_ORIG_mfl = arcpy.MakeFeatureLayer_management(VIV_FC_ORIG_mfl_0, "vivienda", sql2)

# ------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------

        DIST_FC_ORIG_copy = arcpy.CopyFeatures_management(DIST_FC_ORIG_mfl, carpeta + '\DistBD.shp')
        CCPP_FC_ORIG_copy = arcpy.CopyFeatures_management(CCPP_FC_ORIG_mfl, carpeta + '\CcppBD.shp')
        AER_FC_ORIG_copy = arcpy.CopyFeatures_management(AER_FC_ORIG_mfl, carpeta + '\\' + 'AersBD.shp')
        VIV_FC_ORIG_copy = arcpy.CopyFeatures_management(VIV_FC_ORIG_mfl, carpeta + '\\' + 'VivsBD.shp')
        # areaSecciones_copy = arcpy.CopyFeatures_management(areaSecciones, carpeta + '\\' + 'SeccBD.shp')


        #Asociando informacion a la GDB generada

        lista = Plantillas_TMP(carpeta)

        distritos = arcpy.Describe(lista[0])
        areasempadronamiento = arcpy.Describe(lista[1])
        centrospoblados = arcpy.Describe(lista[2])
        viviendas = arcpy.Describe(lista[3])


        #Declarando el espacio de trabajo

        arcpy.env.workspace = distritos.path
        arcpy.env.overwriteOutput = True

        arcpy.Append_management(DIST_FC_ORIG_copy, distritos.path + "\\" + distritos.name, "NO_TEST")
        arcpy.Append_management(AER_FC_ORIG_copy, areasempadronamiento.path + "\\" + areasempadronamiento.name, "NO_TEST")
        arcpy.Append_management(CCPP_FC_ORIG_copy, centrospoblados.path + "\\" + centrospoblados.name, "NO_TEST")
        arcpy.Append_management(VIV_FC_ORIG_copy, viviendas.path + "\\" + viviendas.name, "NO_TEST")


        # Rutas de feature class extraidas

        DIST_FC = distritos.path + "\\" + distritos.name
        AER_FC = areasempadronamiento.path + "\\" + areasempadronamiento.name
        CCPP_FC = centrospoblados.path + "\\" + centrospoblados.name
        VIV_FC = viviendas.path + "\\" + viviendas.name

        for ubigeo in UbigeosParaProcesar:
            print ubigeo
            # CCPPRutas = arcpy.MakeQueryLayer_management(Coneccion_SDE, 'CCPPRutas2', "SELECT * FROM SEGM_R_CCPPRUTA WHERE UBIGEO = '{}' AND FLAG_NUEVO = 1".format(ubigeo))    # FLUJO CON CCPP NUEVOS
            CCPPRutas = arcpy.MakeQueryLayer_management(Coneccion_SDE, 'CCPPRutas2', "SELECT * FROM SEGM_R_CCPPRUTA WHERE UBIGEO = '{}'".format(ubigeo))                     # FLUJO NORMAL
            # Rutas = arcpy.MakeQueryLayer_management(Coneccion_SDE, 'Rutas', "SELECT * FROM SEGM_R_RUTA WHERE UBIGEO = '{}' AND FLAG_NUEVO = 1".format(ubigeo))                 # FLUJO CON CCPP NUEVOS
            Rutas = arcpy.MakeQueryLayer_management(Coneccion_SDE, 'Rutas', "SELECT * FROM SEGM_R_RUTA WHERE UBIGEO = '{}'".format(ubigeo))                                    # FLUJO NORMAL

            correlativo = 0
            with arcpy.da.UpdateCursor(AER_FC, ["IDAER", "CCPP_AER", "VIV_AER", "AER_POS", "AER_INI", "AER_FIN"], "UBIGEO = '{}'".format(ubigeo)) as cursorUC:
                for aer in cursorUC:
                    infoRuta = [ccpp[0] for ccpp in arcpy.da.SearchCursor(CCPPRutas, ["VIV_CCPP"], "IDAER = '{}'".format(aer[0]))]
                    aer[0] = ubigeo + aer[4] + aer[5]
                    aer[1] = len(infoRuta)
                    aer[2] = sum(infoRuta)
                    aer[3] = (str(correlativo + 1)).zfill(2)
                    correlativo = correlativo + 1
                    cursorUC.updateRow(aer)
            del cursorUC

            with arcpy.da.UpdateCursor(CCPP_FC, ["IDCCPP", "CODCCPP", "IDSCR", "IDRUTA"], "UBIGEO = '{}'".format(ubigeo)) as cursorUC:
                for ccpp in cursorUC:
                    if ccpp[1] in [codccpp[0] for codccpp in arcpy.da.SearchCursor(CCPPRutas, ["CODCCPP"], "UBIGEO = '{}'".format(ubigeo))]:
                        idccpp = "{}{}".format(ubigeo, ccpp[1])
                        ccpp[0] = "{}".format(idccpp)
                        ccpp[2] = ([idscr[0] for idscr in arcpy.da.SearchCursor(CCPPRutas, ["IDSCR"], "IDCCPP = '{}'".format(idccpp))])[0]
                        ccpp[3] = ([idruta[0] for idruta in arcpy.da.SearchCursor(CCPPRutas, ["IDRUTA"], "IDCCPP = '{}'".format(idccpp))])[0]
                        cursorUC.updateRow(ccpp)
            del cursorUC

            for ccpp in arcpy.da.SearchCursor(CCPPRutas, ["IDCCPP", "CODCCPP", "IDSCR", "IDAER", "IDRUTA", "OR_CCPP"]):
                with arcpy.da.UpdateCursor(VIV_FC, ["IDCCPP", "IDSCR", "IDAER", "IDRUTA", "OR_CCPP_DIST"], "UBIGEO = '{}' AND CODCCPP = '{}'".format(ubigeo, ccpp[1])) as cursorUC:
                    for viv in cursorUC:
                        viv[0] = ccpp[0]
                        viv[1] = ccpp[2]
                        viv[2] = ccpp[3]
                        viv[3] = ccpp[4]
                        viv[4] = ccpp[5]
                        cursorUC.updateRow(viv)
                del cursorUC
            # print len(CCPPRutas)

            orderby = (None, 'ORDER BY {}, {} ASC'.format('OR_CCPP_DIST', 'ID_REG_OR'))
            for ccpp in arcpy.da.SearchCursor(CCPPRutas, ["IDCCPP"]):
                contador = 0
                with arcpy.da.UpdateCursor(VIV_FC, ["OR_VIV_RUTA"], "IDCCPP = '{}' AND ([P29] = 1 OR [P29] = 3 OR ( [P29] = 6 AND ( [P29M] =1 OR [P29M] =3 )))".format(ccpp[0]), None, False, orderby) as cursorUC:
                    for row in cursorUC:
                        row[0] = contador + 1
                        contador = contador + 1
                        cursorUC.updateRow(row)
                del cursorUC

        AER_tmp = arcpy.MakeFeatureLayer_management(SEGM_R_AER, "AER_tmp_1", sql2)
        CCPP_tmp = arcpy.MakeFeatureLayer_management(SEGM_R_CCPP, "CCPP_tmp_1", sql2)
        VIV_tmp = arcpy.MakeFeatureLayer_management(SEGM_R_VIV, "VIV_tmp_1", sql2)
        for eliminar in [AER_tmp, CCPP_tmp, VIV_tmp]:
            arcpy.DeleteRows_management(eliminar)


        arcpy.Append_management(AER_FC, SEGM_R_AER, "NO_TEST")
        arcpy.Append_management(CCPP_FC, SEGM_R_CCPP, "NO_TEST")
        arcpy.Append_management(VIV_FC, SEGM_R_VIV, "NO_TEST")


        with arcpy.da.UpdateCursor(SEGM_R_AER, ['EST_SEG', 'EST_CROQUIS', 'EST_CONT', 'CONT_RUR_ERROR_01', 'CONT_RUR_ERROR_02', 'CONT_RUR_ERROR_03', 'CONT_RUR_ERROR_04'], sql2) as cursorUC:
            for x in cursorUC:
                x[0], x[1], x[2], x[3], x[4], x[5], x[6] = 4, 0, 0, 0, 0, 0, 0
                cursorUC.updateRow(x)
        del cursorUC

        conexion = settings.conectionDB_pymmsql()
        cursor = conexion.cursor()

        for eliminar in UbigeosParaProcesar:
            cursor.execute("DELETE FROM SEGM_R_AER_POST WHERE UBIGEO = '{}'".format(eliminar))
        conexion.commit()

        TableAER = arcpy.TableToTable_conversion(SEGM_R_AER, 'in_memory', 'TableAER')

        sql3 = Expresion_DB(UbigeosParaProcesar , "#", "A.UBIGEO")

        arcpy.Append_management(TableAER, SEGM_R_AER_POST, "NO_TEST")

        SQL_ProcAlm_CCPP = """UPDATE A SET A.VIV_CCPP = B.VIV_CCPP, A.IDSCR = B.IDSCR, A.IDAER = B.IDAER, A.IDRUTA = B.IDRUTA FROM CPV_SEGMENTACION_GDB.sde.TB_CCPP A INNER JOIN CPV_SEGMENTACION_GDB.sde.SEGM_R_CCPP_TMP B ON A.LLAVE_CCPP COLLATE DATABASE_DEFAULT = B.IDCCPP COLLATE DATABASE_DEFAULT WHERE {}""".format(sql3)

        SQL_ProcAlm_VIV = """UPDATE A SET A.OR_CCPP_DIST = B.OR_CCPP_DIST, A.IDSCR = B.IDSCR, A.IDAER = B.IDAER, A.IDRUTA = B.IDRUTA, A.OR_VIV_RUTA = B.OR_VIV_RUTA from CPV_SEGMENTACION_GDB.sde.TB_VIVIENDA_R A INNER JOIN CPV_SEGMENTACION_GDB.sde.SEGM_R_VIV_TMP B ON A.IDVIV COLLATE DATABASE_DEFAULT = B.IDVIV COLLATE DATABASE_DEFAULT WHERE {}""".format(sql3)

        cursor.execute(SQL_ProcAlm_CCPP)
        conexion.commit()

        cursor.execute(SQL_ProcAlm_VIV)
        conexion.commit()

    cursor.close()
    conexion.close()

    return sql2