import arcpy
from Generales import settings, funcionesGenerales
import os

conn = settings.conectionDB_pymmsql()


def listaRevisar(ubigeo, pathCroquis, conn=conn):
    cursor = conn.cursor()
    cursor.execute("SELECT NOMBRE FROM CPV_SEGMENTACION_GDB.SDE.R_REVISAR_CROQUIS")
    Paths = [x[0] for x in cursor]
    cursor.close()
    if pathCroquis in Paths:
        pass
    else:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO CPV_SEGMENTACION_GDB.SDE.R_REVISAR_CROQUIS VALUES ({}, {})".format(ubigeo, pathCroquis))
        conn.commit()
        cursor.close()

def datosDistrito(ubigeos, conn=conn):
    informacion = []
    for ubigeo in ubigeos:
        cursor = conn.cursor()
        cursor.execute("SELECT DEPARTAMENTO, PROVINCIA, DISTRITO FROM VW_DISTRITO WHERE UBIGEO = '{}'".format(ubigeo))
        infoTMP = [[ubigeo, row[0], row[1], row[2]] for row in cursor]
        informacion.extend(infoTMP)
        cursor.close()
        del cursor
    return informacion

def zoomAer(idscr, conn=conn):
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT A.IDAER ,B.IDSCR FROM SEGM_R_CCPPRUTA A INNER JOIN SEGM_R_RUTA  B ON A.IDRUTA = B.IDRUTA WHERE A.IDSCR = '{}'".format(idscr))
    informacion = [x[0] for x in cursor]
    cursor.close()
    del cursor
    return informacion

def zoomCCPP(mxd, df, seccion):
    lista = []
    lista2 = []
    lista_revisar_zoom = []
    for i in arcpy.mapping.ListLayers(mxd):
        if i.name == 'AER':
            scr = i
        if i.name == 'CCPP_EM':
            lista.append(i)
        if i.name == 'CCPP_CC':
            # lista.append(i)
            pass
        if i.name == 'CCPP_CN':
            # lista.append(i)
            pass

    # area = [x[0] for x in arcpy.da.SearchCursor(scr, ["SHAPE@AREA"])][0]
    for i in lista:
        a = arcpy.GetCount_management(i)[0]
        lista2.append(int(a))
        cantCCPP = sum(filter(None, lista2))

    ccpp = arcpy.Merge_management(lista, 'in_memory\ccpp1')
    mfl = arcpy.MakeFeatureLayer_management(ccpp, 'CentroPoblados')
    layerFileArea = arcpy.mapping.Layer('CentroPoblados')

    if cantCCPP > 3:
        df.extent = layerFileArea .getSelectedExtent()  # ZOOM EXTEND A LA CAPA DE AERS
        df.scale = df.scale * 1.5
        arcpy.RefreshActiveView()
            # df.scale = df.scale * 12
    elif cantCCPP < 4:
        print "menor a 4"
        df.extent = scr.getSelectedExtent()  # ZOOM EXTEND A LA CAPA DE AERS
        df.scale = df.scale * 1.2
        arcpy.RefreshActiveView()
        lista_revisar_zoom.append(seccion)

    return lista_revisar_zoom

## ---------------------------------------------------------------------

def datosSeccion(ubigeo, conn=conn):
    cursor = conn.cursor()
    # cursor.execute("SELECT IDSCR, SCR, VIV_SCR, CCPP_SCR FROM SEGM_R_SCR WHERE UBIGEO = '{}' ORDER BY SCR".format(ubigeo)) # FLUJO NORMAL
    cursor.execute("SELECT IDSCR, SCR, VIV_SCR, CCPP_SCR FROM SEGM_R_SCR WHERE UBIGEO = '{}' AND FLAG_NUEVO = 1 ORDER BY SCR".format(ubigeo))  # CON CCPP NUEVOS
    informacion = ([[x[0], x[1], x[2], x[3]] for x in cursor])
    cursor.close()
    del cursor
    return informacion

def informacionCabecera(lista, mxd):

    ElementoTexto1 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "CCDD")[0]
    ElementoTexto2 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "DEPARTAMENTO")[0]
    ElementoTexto3 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "CCPP")[0]
    ElementoTexto4 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "PROVINCIA")[0]
    ElementoTexto5 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "CCDI")[0]
    ElementoTexto6 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "DISTRITO")[0]

    ElementoTexto1.text = lista[0][0:2]
    ElementoTexto2.text = lista[1]
    ElementoTexto3.text = lista[0][2:4]
    ElementoTexto4.text = lista[2]
    ElementoTexto5.text = lista[0][4:6]
    ElementoTexto6.text = lista[3]

    arcpy.RefreshActiveView()


def informacionCabeceraSCR(mxd, IDSCR, SCR, VIV_SCR, CCPP_SCR):

    ElementoTexto7 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "SCR_INFO")[0]
    ElementoTexto8 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "VIV_SCR")[0]
    ElementoTexto9 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "COD_BARRA")[0]
    ElementoTexto10 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "NUMCODE")[0]

    ElementoTexto11 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "SCR_OBS")[0]
    ElementoTexto12 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "CCPP_OBS")[0]
    ElementoTexto13 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "VIV_OBS")[0]

    ElementoTexto7.text = SCR
    ElementoTexto8.text = VIV_SCR
    ElementoTexto9.text = "*{}*".format(IDSCR)
    ElementoTexto10.text = IDSCR
    ElementoTexto11.text = SCR
    ElementoTexto12.text = CCPP_SCR
    ElementoTexto13.text = VIV_SCR

    arcpy.RefreshActiveView()


def agregarLyrUbigeo(mxd, id, nombrecampo, idscr):
    for i in arcpy.mapping.ListLayers(mxd):
        if i.name == 'Tracks':
            i.definitionQuery = "{} = '{}'".format(nombrecampo, id)
        elif i.name == 'AER':
            zoom_aer = zoomAer(idscr)
            # zoom_aer = zoomAer2(mxd,df)
            lista_aer = "','".join(zoom_aer)
            i.definitionQuery = "IDAER IN ('{}')".format(lista_aer)
        elif i.name == 'CCPP_URB':
            i.definitionQuery = "{} = '{}' AND (AREA = 1)".format(nombrecampo, id)
    arcpy.RefreshActiveView()


def queryCapasAuxiliares(ubigeo, mxd):
    for i in arcpy.mapping.ListLayers(mxd):
        if i.name == 'RED HIDROGRAFICA':
            i.definitionQuery = "UBIGEO = '{}'".format(ubigeo)
            i.visible = True
        elif i.name == 'CURVAS NIVEL':
            i.definitionQuery = "UBIGEO = '{}'".format(ubigeo)
            i.visible = True
        arcpy.RefreshTOC()
        arcpy.RefreshActiveView()


def querysLayers(mxd, id, nombrecampo, ubigeo):
    for i in arcpy.mapping.ListLayers(mxd):
        if i.name == 'CCPP_EM':
            i.definitionQuery = "{} = '{}' AND (UBIGEO = '{}')".format(nombrecampo, id, ubigeo)
        elif i.name == 'CCPP_CN':
            i.definitionQuery = "{} = '{}' AND (NOM_CN <> '') AND (UBIGEO = '{}')".format(nombrecampo, id, ubigeo)
        elif i.name == 'CCPP_FE':
            i.definitionQuery = "{} <> '{}' AND (UBIGEO = '{}')".format(nombrecampo, id, ubigeo)
        elif i.name == 'CCPP_CC':
            i.definitionQuery = "{} = '{}' AND (NOM_CC <> '') AND (UBIGEO = '{}')".format(nombrecampo, id, ubigeo)
    arcpy.RefreshActiveView()


# def zoomCCPP(mxd, df):
#     lista_revisar_zoom = []
#     for i in arcpy.mapping.ListLayers(mxd):
#         if i.name == 'CCPP_EM':
#         # if i.name == 'SCR':
#             df.extent = i.getSelectedExtent()  # ZOOM EXTEND A LA CAPA DE AERS
#             # df.scale = df.scale * 9.5
#             df.scale = df.scale * 1.8
#     return lista_revisar_zoom


def aersenscr(idscr, conn=conn):
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT IDAER FROM SEGM_R_CCPPRUTA WHERE IDSCR = '{}' ".format(idscr))
    aers = [x[0] for x in cursor]
    sql = funcionesGenerales.Expresion(aers, "#", "IDAER")
    cursor.close()
    del cursor
    return sql


def geometriaScr(scr, sql, SEGM_R_AER, df, SCR_LYR, mxd):

    nameSCR = 'SCRmfl'

    SCRmfl_TMP = arcpy.MakeFeatureLayer_management(SEGM_R_AER, "SCRmfl_TMP", sql)
    SCRdisolve = arcpy.Dissolve_management(SCRmfl_TMP, 'in_memory\seccion', '#', '#', 'MULTI_PART', 'DISSOLVE_LINES')
    mfl = arcpy.MakeFeatureLayer_management(SCRdisolve, nameSCR)
    arcpy.AddField_management(mfl, "SCR", "TEXT", '#', '#', '3')
    with arcpy.da.UpdateCursor(mfl, ["SCR"]) as cursorUC:
        for row in cursorUC:
            row[0] = str(scr).zfill(3)
            cursorUC.updateRow(row)
    del cursorUC

    layerFileSCR = arcpy.mapping.Layer(nameSCR)
    arcpy.RefreshActiveView()
    arcpy.ApplySymbologyFromLayer_management(layerFileSCR, SCR_LYR)
    arcpy.RefreshActiveView()
    arcpy.mapping.AddLayer(df, layerFileSCR)
    arcpy.RefreshActiveView()

    for x in arcpy.mapping.ListLayers(mxd):
        if x.name == 'SCRmfl':
            arcpy.RefreshActiveView()
            lblclass = x.labelClasses[0]
            arcpy.RefreshActiveView()
            lblclass.expression = '''"<FNT size = '20'>" & "<CLR red='0' green='0' blue='0'>" & "<BOL>" & "SCR: " & [SCR] & "</BOL>" & "</CLR>" & "</FNT>"'''
            x.showLabels = True
            arcpy.RefreshActiveView()


def removerLayersTMP(mxd, df, nivel):
    if nivel == 1:
        for i in arcpy.mapping.ListLayers(mxd):
            if i.name in ('Tracksmfl', 'CCPP_DIST'):
                arcpy.mapping.RemoveLayer(df, i)
    else:
        for i in arcpy.mapping.ListLayers(mxd):
            if i.name == 'SCRmfl':
                arcpy.mapping.RemoveLayer(df, i)


def CroquisSeccion(ubigeos, WorkSpaceCroquis, SEGM_R_AER, SCR_LYR, mxd_croquis_scr):

    listaProblemas = []

    mxd = arcpy.mapping.MapDocument(mxd_croquis_scr)
    df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
    settings.conectionGDB_arcpy()
    settings.conectionDB_arcpy()

    for ubigeo in datosDistrito(ubigeos):
        print ubigeo

        queryCapasAuxiliares(ubigeo[0], mxd)
        informacionCabecera(ubigeo, mxd)
        # agregarLyrUbigeo(mxd, ubigeo[0], "UBIGEO")

        for seccion in datosSeccion(ubigeo[0]):

            informacionCabeceraSCR(mxd, seccion[0], seccion[1], seccion[2], seccion[3])
            # idscr = seccion[0]
            agregarLyrUbigeo(mxd, ubigeo[0], "UBIGEO", seccion[0])
            querysLayers(mxd, seccion[0], "IDSCR", ubigeo[0])

            listarevisar = zoomCCPP(mxd, df, seccion)
            sql = aersenscr(seccion[0])
            geometriaScr(seccion[1], sql, SEGM_R_AER, df, SCR_LYR, mxd)
            # zoomAER2(mxd, df)

            CroquisPathPdf = os.path.join(WorkSpaceCroquis, "Rural", ubigeo[0], seccion[0] + ".pdf")
            print CroquisPathPdf
            if len(listarevisar) > 0:
                listaRevisar(ubigeo[0], seccion[0])

            arcpy.mapping.ExportToPDF(mxd, CroquisPathPdf, "PAGE_LAYOUT")
            # mxd.saveACopy(r'D:\SegmentacionRuralV2\Procesamiento\Croquis\Rural_mxd\{}.mxd'.format(seccion[0]))

            if len(listarevisar) > 0:
                print "Revisar croquis del ubigeo: " + str(ubigeo)
                print listaProblemas