# -*- #################

import arcpy, time, getpass, pymssql

ubigeo = arcpy.GetParameterAsText(0)
usuario = arcpy.GetParameterAsText(1)
carpeta = arcpy.GetParameterAsText(2)

lyrAer = r'\\192.168.201.115\cpv2017\SegmentacionRural_Procesamiento\Insumos\AER.lyr'
lyrCcpp = r'\\192.168.201.115\cpv2017\SegmentacionRural_Procesamiento\Insumos\CCPP.lyr'
lyrDist = r'\\192.168.201.115\cpv2017\SegmentacionRural_Procesamiento\Insumos\DIST.lyr'
lyrTrack = r'\\192.168.201.115\cpv2017\SegmentacionRural_Procesamiento\Insumos\TRACK.lyr'
lyrCN = r'\\192.168.201.115\cpv2017\SegmentacionRural_Procesamiento\Insumos\CN.lyr'
lyrHidro = r'\\192.168.201.115\cpv2017\SegmentacionRural_Procesamiento\Insumos\HIDRO.lyr'

arcpy.env.overwriteOutput = True

ip = "172.18.1.93"
nombre = 'CPV_SEGMENTACION'

def conectionDB_arcpy(ip, nombre):
    if arcpy.Exists("{}.sde".format(nombre)) == False:
        arcpy.CreateDatabaseConnection_management("Database Connections",
                                                  "{}.sde".format(nombre),
                                                  "SQL_SERVER",
                                                  ip,
                                                  "DATABASE_AUTH",
                                                  "us_arcgis_seg_2",
                                                  "MBs0p0rt301",
                                                  "#",
                                                  nombre,
                                                  "#",
                                                  "#",
                                                  "#",
                                                  "#")

    conexionDB = r'Database Connections\{}.sde'.format(nombre)
    return conexionDB


def conectionDB_pymmsql(ip, nombre):
    user_sde = "us_arcgis_seg_2"
    password_sde = "MBs0p0rt301"
    conexion = pymssql.connect(ip, user_sde, password_sde, nombre)
    return conexion


def cursorDB():
    conn = conectionDB_pymmsql(ip, nombre)
    cursor = conn.cursor()
    return cursor


def crearFileGDB(ubigeo, carpeta):

    user = getpass.getuser()
    fecha = time.strftime('%d%b%y')
    hora = time.strftime('%H%M%S')
    nameFile = "SR_{}-{}-{}-{}".format(ubigeo, user, fecha, hora)
    folder = arcpy.CreateFolder_management(carpeta, nameFile)
    nameGDB = "BD_SEGM_R_{}".format(ubigeo)
    fileGDB = arcpy.CreateFileGDB_management(folder, nameGDB, "10.0")

    fdGenerales = arcpy.CreateFeatureDataset_management(fileGDB, "Generales", arcpy.SpatialReference(4326))
    arcpy.CreateFeatureDataset_management(fileGDB, "Procesamiento", arcpy.SpatialReference(4326))
    arcpy.CreateFeatureDataset_management(fileGDB, "Resultados", arcpy.SpatialReference(4326))

    # featureClass = [["DIST_{}".format(ubigeo), "POLYGON"], ["AER_{}".format(ubigeo), "POLYGON"], ["CCPP_{}".format(ubigeo), "POINT"], ["TRACK_{}".format(ubigeo), "POLYLINE"]]
    featureClass = [["DIST_{}".format(ubigeo), "POLYGON"], ["AER_{}".format(ubigeo), "POLYGON"], ["CCPP_{}".format(ubigeo), "POINT"], ["TRACK_{}".format(ubigeo), "POLYLINE"], ["CN_{}".format(ubigeo), "POLYLINE"], ["HIDRO_{}".format(ubigeo), "POLYLINE"],
                    ["CCPP_N_{}".format(ubigeo), "POINT"], ["RUTA_OLD_{}".format(ubigeo), "POLYGON"]]

    Campos_AER = [("UBIGEO", "TEXT", "6"), ("IDAER", "TEXT", "12"), ("AER_INI", "TEXT", "3"), ("AER_FIN", "TEXT", "3"), ("CCPP_AER", "SHORT", "3"), ("VIV_AER", "SHORT", "5")]
    Campos_TRACK = [("UBIGEO", "TEXT", "6"), ("SUP_VIA", "TEXT", "50")]

    # ******************************************************************************************************************************************************************

    Campos_CCPP = [("UBIGEO", "TEXT", "6"), ("LLAVE_CCPP", "TEXT", "10"), ("IDAER", "TEXT", "12"), ("AREA", "SHORT", "1"), ("CODCCPP", "TEXT", "4"), ("NOMCCPP", "TEXT", "100"), ("VIV_CCPP", "SHORT", "6")]

    Campos_CCPP_N = [("UBIGEO", "TEXT", "6"), ("LLAVE_CCPP", "TEXT", "10"), ("IDAER", "TEXT", "12"), ("AREA", "SHORT", "1"), ("CODCCPP", "TEXT", "4"), ("NOMCCPP", "TEXT", "100"), ("VIV_CCPP", "SHORT", "6"),
                     ("IDSCR", "TEXT", "14"), ("IDRUTA", "TEXT", "17")]

    Campos_RUTA = [("UBIGEO", "TEXT", "6"), ("IDRUTA", "TEXT", "17"), ("RUTA", "SHORT", "1")]

    # ******************************************************************************************************************************************************************
    Campos_DIST = [("UBIGEO", "TEXT", "6"), ("DEPARTAMENTO", "TEXT", "50"), ("PROVINCIA", "TEXT", "50"), ("DISTRITO", "TEXT", "50"), ("REGION", "SHORT", "1")]
    Campos_CN = [("UBIGEO", "TEXT", "6"), ("ALTITUD", "SHORT", "5")]
    Campos_HIDRO = [("UBIGEO", "TEXT", "6"), ("NOMBRE", "TEXT", "60"), ("CLASIFICAC", "SHORT", "2")]

    for i in featureClass:
        fc_tmp = arcpy.CreateFeatureclass_management("in_memory", i[0], i[1], "#", "#", "#", arcpy.SpatialReference(4326))
        if i[0] == "DIST_{}".format(ubigeo):
            for n in Campos_DIST:
                if n[1] == "TEXT":
                    arcpy.AddField_management(fc_tmp, n[0], n[1], '#', '#', n[2], '#', 'NULLABLE', 'NON_REQUIRED', '#')
                else:
                    arcpy.AddField_management(fc_tmp, n[0], n[1], n[2], '#', '#', '#', 'NULLABLE', 'NON_REQUIRED', '#')
        elif i[0] == "AER_{}".format(ubigeo):
            for n in Campos_AER:
                if n[1] == "TEXT":
                    arcpy.AddField_management(fc_tmp, n[0], n[1], '#', '#', n[2], '#', 'NULLABLE', 'NON_REQUIRED', '#')
                else:
                    arcpy.AddField_management(fc_tmp, n[0], n[1], n[2], '#', '#', '#', 'NULLABLE', 'NON_REQUIRED', '#')
        elif i[0] == "CCPP_{}".format(ubigeo):
            for n in Campos_CCPP:
                if n[1] == "TEXT":
                    arcpy.AddField_management(fc_tmp, n[0], n[1], '#', '#', n[2], '#', 'NULLABLE', 'NON_REQUIRED', '#')
                else:
                    arcpy.AddField_management(fc_tmp, n[0], n[1], n[2], '#', '#', '#', 'NULLABLE', 'NON_REQUIRED', '#')
        # ****************************************************
        elif i[0] == "CCPP_N_{}".format(ubigeo):
            for n in Campos_CCPP_N:
                if n[1] == "TEXT":
                    arcpy.AddField_management(fc_tmp, n[0], n[1], '#', '#', n[2], '#', 'NULLABLE', 'NON_REQUIRED', '#')
                else:
                    arcpy.AddField_management(fc_tmp, n[0], n[1], n[2], '#', '#', '#', 'NULLABLE', 'NON_REQUIRED', '#')
        elif i[0] == "RUTA_OLD_{}".format(ubigeo):
            for n in Campos_RUTA:
                if n[1] == "TEXT":
                    arcpy.AddField_management(fc_tmp, n[0], n[1], '#', '#', n[2], '#', 'NULLABLE', 'NON_REQUIRED', '#')
                else:
                    arcpy.AddField_management(fc_tmp, n[0], n[1], n[2], '#', '#', '#', 'NULLABLE', 'NON_REQUIRED', '#')
        # ****************************************************
        elif i[0] == "CN_{}".format(ubigeo):
            for n in Campos_CN:
                if n[1] == "TEXT":
                    arcpy.AddField_management(fc_tmp, n[0], n[1], '#', '#', n[2], '#', 'NULLABLE', 'NON_REQUIRED', '#')
                else:
                    arcpy.AddField_management(fc_tmp, n[0], n[1], n[2], '#', '#', '#', 'NULLABLE', 'NON_REQUIRED', '#')
        elif i[0] == "HIDRO_{}".format(ubigeo):
            for n in Campos_HIDRO:
                if n[1] == "TEXT":
                    arcpy.AddField_management(fc_tmp, n[0], n[1], '#', '#', n[2], '#', 'NULLABLE', 'NON_REQUIRED', '#')
                else:
                    arcpy.AddField_management(fc_tmp, n[0], n[1], n[2], '#', '#', '#', 'NULLABLE', 'NON_REQUIRED', '#')
        ##############
        else:
            for n in Campos_TRACK:
                if n[1] == "TEXT":
                    arcpy.AddField_management(fc_tmp, n[0], n[1], '#', '#', n[2], '#', 'NULLABLE', 'NON_REQUIRED', '#')
                else:
                    arcpy.AddField_management(fc_tmp, n[0], n[1], n[2], '#', '#', '#', 'NULLABLE', 'NON_REQUIRED', '#')

        fc = arcpy.CreateFeatureclass_management(fdGenerales, i[0], i[1], fc_tmp, "#", "#", arcpy.SpatialReference(4326))


    rutaFD = '{}\{}\{}.gdb\Generales'.format(carpeta, nameFile, nameGDB)

    return rutaFD


def importarFeatureClass(ubigeo, rutaFD):
    conexionDB = conectionDB_arcpy(ip, nombre)
    ccpp = arcpy.MakeQueryLayer_management(conexionDB, "CCPP_{}".format(ubigeo), "SELECT * FROM CPV_SEGMENTACION_GDB.sde.TB_CCPP where UBIGEO = '{}' ".format(ubigeo), 'LLAVE_CCPP', 'POINT', '4326', arcpy.SpatialReference(4326))
    aer = arcpy.MakeQueryLayer_management(conexionDB, "AER_{}".format(ubigeo), "SELECT * FROM CPV_SEGMENTACION_GDB.sde.TB_AER where UBIGEO = '{}'".format(ubigeo), 'UBIGEO;AER_INI;AER_FIN', 'POLYGON', '4326', arcpy.SpatialReference(4326))
    distrito = arcpy.MakeQueryLayer_management(conexionDB, "DIST_{}".format(ubigeo), "SELECT*FROM CPV_SEGMENTACION_GDB.sde.TB_LIMITE_DIS WHERE UBIGEO = '{}'".format(ubigeo), "UBIGEO", "POLYGON", '4326', arcpy.SpatialReference(4326))
    track = arcpy.MakeQueryLayer_management(conexionDB, "TRACK_{}".format(ubigeo), "SELECT * FROM CPV_SEGMENTACION_GDB.sde.TB_TRACK where UBIGEO = '{}'".format(ubigeo), 'ID', 'POLYLINE', '4326', arcpy.SpatialReference(4326))

    curvasnivel = arcpy.MakeQueryLayer_management(conexionDB, "CN_{}".format(ubigeo), "SELECT*FROM CPV_SEGMENTACION_GDB.sde.TB_CN WHERE UBIGEO = '{}'".format(ubigeo), "UBIGEO", "POLYLINE", '4326', arcpy.SpatialReference(4326))
    hidrografia = arcpy.MakeQueryLayer_management(conexionDB, "HIDRO_{}".format(ubigeo), "SELECT * FROM CPV_SEGMENTACION_GDB.sde.TB_HIDRO where UBIGEO = '{}'".format(ubigeo), 'UBIGEO', 'POLYLINE', '4326', arcpy.SpatialReference(4326))

    ccpp_n = arcpy.MakeQueryLayer_management(conexionDB, "CCPP_N_{}".format(ubigeo), "SELECT * FROM CPV_SEGMENTACION_GDB.sde.TB_CCPP where UBIGEO = '{}' AND ESTADO = '3'".format(ubigeo), 'LLAVE_CCPP', 'POINT', '4326', arcpy.SpatialReference(4326))
    ruta = arcpy.MakeQueryLayer_management(conexionDB, "RUTA_OLD_{}".format(ubigeo), "SELECT * FROM CPV_SEGMENTACION_GDB.sde.SEGM_R_RUTA where UBIGEO = '{}'".format(ubigeo), 'IDRUTA', 'POLYGON', '4326', arcpy.SpatialReference(4326))

    arcpy.Append_management(ccpp, r'{}\CCPP_{}'.format(rutaFD, ubigeo), "NO_TEST")
    arcpy.Append_management(aer, r'{}\AER_{}'.format(rutaFD, ubigeo), "NO_TEST")
    arcpy.Append_management(distrito, r'{}\DIST_{}'.format(rutaFD, ubigeo), "NO_TEST")
    arcpy.Append_management(track, r'{}\TRACK_{}'.format(rutaFD, ubigeo), "NO_TEST")
    # ****************************************************
    arcpy.Append_management(ccpp_n, r'{}\CCPP_N_{}'.format(rutaFD, ubigeo), "NO_TEST")
    arcpy.Append_management(ruta, r'{}\RUTA_OLD_{}'.format(rutaFD, ubigeo), "NO_TEST")
    # ****************************************************
    arcpy.Append_management(curvasnivel, r'{}\CN_{}'.format(rutaFD, ubigeo), "NO_TEST")
    arcpy.Append_management(hidrografia, r'{}\HIDRO_{}'.format(rutaFD, ubigeo), "NO_TEST")

def validarUsuario(ubigeo, usuario, carpeta):
    cursor = cursorDB()
    cursor.execute("SELECT SEGMENTISTA FROM TB_MODULO_ASIGN_R WHERE UBIGEO = '{}' AND SEGMENTISTA = '{}'".format(ubigeo, usuario))

    validacion = len([x[0] for x in cursor])

    if validacion == 1:
        rutaFD = crearFileGDB(ubigeo, carpeta)
        importarFeatureClass(ubigeo, rutaFD)
        arcpy.env.scratchWorkspace = rutaFD

        arcpy.AlterField_management(r'{}\CCPP_{}'.format(rutaFD, ubigeo), "LLAVE_CCPP", "IDCCPP")
        arcpy.AlterField_management(r'{}\CCPP_N_{}'.format(rutaFD, ubigeo), "LLAVE_CCPP", "IDCCPP")

        arcpy.SetParameterAsText(3, r'{}\CCPP_{}'.format(rutaFD, ubigeo))
        arcpy.SetParameterAsText(4, r'{}\TRACK_{}'.format(rutaFD, ubigeo))
        arcpy.SetParameterAsText(5, r'{}\AER_{}'.format(rutaFD, ubigeo))
        arcpy.SetParameterAsText(6, r'{}\DIST_{}'.format(rutaFD, ubigeo))
        arcpy.SetParameterAsText(7, r'{}\CN_{}'.format(rutaFD, ubigeo))
        arcpy.SetParameterAsText(8, r'{}\HIDRO_{}'.format(rutaFD, ubigeo))
        # ****************************************************
        arcpy.SetParameterAsText(9,  r'{}\CCPP_N_{}'.format(rutaFD, ubigeo))
        arcpy.SetParameterAsText(10, r'{}\RUTA_OLD_{}'.format(rutaFD, ubigeo))

        params = arcpy.GetParameterInfo()

        for param in params:
            if '{}'.format(param.name) == 'centrosPoblados':
                param.symbology = lyrCcpp
            elif '{}'.format(param.name) == 'track':
                param.symbology = lyrTrack
            elif '{}'.format(param.name) == 'aer':
                param.symbology = lyrAer
            elif '{}'.format(param.name)== 'distrito':
                param.symbology = lyrDist
            ##--------------------------------------------------
            elif '{}'.format(param.name) == 'curvasnivel':
                param.symbology = lyrCN
            elif '{}'.format(param.name) == 'hidrografia':
                param.symbology = lyrHidro


    else:
        arcpy.AddError("\n"*2 + "-"*80 + "\n")
        arcpy.AddError("OBSERVACION:")
        arcpy.AddWarning("EL usuario ingresado no esta relacionado a este ubigeo.")
        arcpy.AddError("\n" + "-"*80 + "\n"*2)
        raise arcpy.ExecuteError

    cursor.close()



validarUsuario(ubigeo, usuario, carpeta)