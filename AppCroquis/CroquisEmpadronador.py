#-*- coding: utf-8 -*-

import arcpy
from Generales import settings
import os
import sys

arcpy.env.overwriteOutput = True

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


def datosRutas(ubigeo, conn=conn):
    cursor = conn.cursor()
    # cursor.execute("SELECT IDRUTA, SCR, N_EMP_RUTA FROM CPV_SEGMENTACION_GDB.SDE.SEGM_R_RUTA WHERE UBIGEO = '{}' ORDER BY IDRUTA".format(ubigeo)) # FLUJO NORMAL
    cursor.execute("SELECT IDRUTA, SCR, N_EMP_RUTA FROM CPV_SEGMENTACION_GDB.SDE.SEGM_R_RUTA WHERE UBIGEO = '{}' AND FLAG_NUEVO = 1 ORDER BY IDRUTA".format(ubigeo))  # CON CCPP NUEVOS
    informacion = [[x[0], x[1], x[2]] for x in cursor]
    cursor.close()
    del cursor
    return informacion


def dataEmp(idruta, conn=conn):
    cursor = conn.cursor()
    cursor.execute("SELECT EMP FROM SEGM_R_EMP WHERE IDRUTA = '{}' AND FASE  = 'CPV2017'".format(idruta))
    informacion = [x[0] for x in cursor]
    cursor.close()
    del cursor
    return informacion


def dataAER(idruta, conn=conn):
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT IDAER FROM SEGM_R_CCPPRUTA WHERE IDRUTA = '{}'".format(idruta))
    informacion = [x[0] for x in cursor]
    cursor.close()
    del cursor
    return informacion


def sufijoNombrePDF(aer, conn=conn):
    cursor = conn.cursor()
    cursor.execute("SELECT AER_POS FROM SEGM_R_AER_POST WHERE IDAER = '{}'".format(aer))
    informacion = [x for x in cursor][0]
    cursor.close()
    del cursor
    return informacion


def informacioCabeceraRutasSCR(mxd, SCR, tipo):
    ElementoTexto7 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "SCR")[0]
    ElementoTexto7.text = SCR if tipo == 1 else u'{}'.format(' ')


def informacionCabeceraRutasEMP(mxd, EMP, IDRUTA):
    ElementoTexto12 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "NEMP")[0]
    ElementoTexto13 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "COD_BARRA")[0]
    ElementoTexto14 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "NUMCODE")[0]
    ElementoTexto15 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "NEMP_OBS")[0]

    ElementoTexto12.text = EMP
    ElementoTexto13.text = "*{}{}*".format(IDRUTA, EMP)
    ElementoTexto14.text = "{}{}".format(IDRUTA, EMP)
    ElementoTexto15.text = EMP


def informacionCabeceraAER(mxd, aer):
    ElementoTexto8 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "AER_INI")[0]
    ElementoTexto9 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "AER_FIN")[0]

    ElementoTexto8.text = aer[6:9]
    ElementoTexto9.text = aer[9:12]


def informacionCabeceraRutasViv(mxd, aer, idruta, conn=conn):
    cursor = conn.cursor()
    cursor.execute("SELECT VIV_AER FROM SEGM_R_AER_POST WHERE IDAER = '{}'".format(aer))
    informacionVivAer = [x[0] for x in cursor]
    cursor.close()
    del cursor
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(VIV_CCPP) FROM SEGM_R_CCPPRUTA WHERE IDAER = '{}' AND IDRUTA = '{}'".format(aer, idruta))
    informacionVivTrab = [x[0] for x in cursor]
    cursor.close()
    del cursor

    ElementoTexto10 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "AER_VIV")[0]
    ElementoTexto11 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "VIV_TRAB")[0]

    ElementoTexto10.text = informacionVivAer[0]
    ElementoTexto11.text = informacionVivTrab[0]


def agregarLyrUbigeo(mxd, id, nombrecampo):
    for i in arcpy.mapping.ListLayers(mxd):
        if i.name == 'Tracks':
            i.definitionQuery = "{} = '{}'".format(nombrecampo, id)
        elif i.name == 'CCPP_URB':
            i.definitionQuery = "{} = '{}' AND (AREA = 1)".format(nombrecampo, id)
    arcpy.RefreshActiveView()


def querysLayersAER(mxd, id, nombrecampo):
    for i in arcpy.mapping.ListLayers(mxd):
        if i.name == 'AER':
            i.definitionQuery = "{} = '{}'".format(nombrecampo, id)


def queryCapasAuxiliares(ubigeo, mxd):
    for i in arcpy.mapping.ListLayers(mxd):
        if i.name == 'RED HIDROGRAFICA':
            i.definitionQuery = "UBIGEO = '{}'".format(ubigeo)
            i.visible = True
            arcpy.RefreshTOC()
            arcpy.RefreshActiveView()
        elif i.name == 'CURVAS NIVEL':
            i.definitionQuery = "UBIGEO = '{}'".format(ubigeo)
            i.visible = True
            arcpy.RefreshTOC()
            arcpy.RefreshActiveView()


def querysLayers(mxd, id, nombrecampo, idaer):
    for i in arcpy.mapping.ListLayers(mxd):
        if i.name == 'CCPP_EM':
            i.definitionQuery = "{} = '{}' AND IDAER = '{}'".format(nombrecampo, id, idaer)
        elif i.name == 'CCPP_CN':
            i.definitionQuery = "{} = '{}' AND (NOM_CN <> '') AND IDAER = '{}'".format(nombrecampo, id, idaer)
        elif i.name == 'CCPP_FE':
            i.definitionQuery = "{} <> '{}'".format(nombrecampo, id)
        elif i.name == 'CCPP_CC':
            i.definitionQuery = "{} = '{}' AND (NOM_CC <> '') AND IDAER = '{}'".format(nombrecampo, id, idaer)
    arcpy.RefreshActiveView()

#
def zoomAER(mxd, df):
    lista_revisar_zoom = []
    for i in arcpy.mapping.ListLayers(mxd):
        if i.name == 'AER':
        # if i.name == 'CCPP_EM':
            df.extent = i.getSelectedExtent()  # ZOOM EXTEND A LA CAPA DE AERS
            df.scale = df.scale * 1.25
            # df.scale = df.scale * 12
    arcpy.RefreshActiveView()
    return lista_revisar_zoom


def zoomAER3(mxd, df, emp):
    lista = []
    lista2 = []
    lista_revisar_zoom = []
    for i in arcpy.mapping.ListLayers(mxd):
        if i.name == 'AER':
            aer = i
        if i.name == 'CCPP_EM':
            centropoblado = i
            lista.append(i)
        if i.name == 'CCPP_CC':
            pass
            # lista.append(i)
        if i.name == 'CCPP_CN':
            pass
            # lista.append(i)

    area = [x[0] for x in arcpy.da.SearchCursor(aer, ["SHAPE@AREA"])][0]
    # area = [x[0] for x in arcpy.da.SearchCursor(aer, ["SHAPE@AREA"])]

    for i in lista:
        a = arcpy.GetCount_management(i)[0]
        lista2.append(int(a))
        cantCCPP = sum(filter(None, lista2))

    if area < 0.022:
        # print "Menor al área"
        df.extent = aer.getSelectedExtent()  # ZOOM EXTEND A LA CAPA DE AERS
        df.scale = df.scale * 1.15
        arcpy.RefreshActiveView()
            # df.scale = df.scale * 12
    elif area >= 0.022:
        print "Mayor al área"
        # ccpp = arcpy.Merge_management(lista, 'in_memory\ccpp1')
        ccpp = centropoblado
        if cantCCPP < 3:
            print "Menor a 3"
            mfl = arcpy.MakeFeatureLayer_management(ccpp , 'CentroPoblados')
            layerFileArea = arcpy.mapping.Layer('CentroPoblados')
            arcpy.RefreshActiveView()
            df.extent = layerFileArea.getSelectedExtent()  # ZOOM EXTEND A LA CAPA DE AERS
            df.scale = 90000
            # df.scale = 150000
            arcpy.RefreshActiveView()
            lista_revisar_zoom.append(emp)
        else:
            print "Mayor a 3"
            nameArea = 'areaMfl'
            mfl = arcpy.MakeFeatureLayer_management(ccpp, 'area1')
            areaBound =  arcpy.MinimumBoundingGeometry_management(mfl, r'D:\SegmentacionRuralV2\Procesamiento\Croquis\Croq_proceso\area.shp', "RECTANGLE_BY_AREA", "ALL")
            mfl = arcpy.MakeFeatureLayer_management(areaBound, nameArea)
            layerFileArea = arcpy.mapping.Layer(nameArea)
            arcpy.RefreshActiveView()
            df.extent = layerFileArea.getSelectedExtent()  # ZOOM EXTEND A LA CAPA DE AERS
            df.scale = df.scale * 1.8
            arcpy.RefreshActiveView()
    # if len(lista_revisar_zoom) != 0:
    return lista_revisar_zoom





def observacionesCroquis(mxd, empruta, idruta, idaer, conn=conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(IDCCPP) AS CANT_CCPP, SUM(VIV_CCPP) AS VIV_EMP FROM SEGM_R_CCPPRUTA WHERE IDRUTA = '{}' AND IDAER = '{}'".format(idruta, idaer))
    informacion = [[x[0], x[1]] for x in cursor]
    cursor.close()
    del cursor

    ConteoCCPP = informacion[0][0]
    viviendasccppruta = informacion[0][1]

    ElementoTexto16 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "CCPP_OBS")[0]
    ElementoTexto17 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "VIV_OBS")[0]

    ElementoTexto16.text = "01    CENTRO POBLADO." if ConteoCCPP == 1 else "{}    CENTROS POBLADOS.".format(
        str(ConteoCCPP).zfill(3))

    if empruta > 1:
        ElementoTexto17.text = 'LAS VIVIENDAS A TRABAJAR SERÁN ASIGNADAS EN CAMPO POR EL JEFE DE SECCIÓN.'
    elif empruta == 1 and ConteoCCPP == '1':
        ElementoTexto17.text = 'EL CUAL CONTIENE {} VIVIENDAS.'.format(viviendasccppruta)
    elif empruta == 1 and ConteoCCPP != '1':
        ElementoTexto17.text = 'QUE SUMAN {} VIVIENDAS.'.format(viviendasccppruta)
    arcpy.RefreshActiveView()


def CroquisEmpadronador(ubigeos, WorkSpaceCroquis, mxd_croquis_emp, tipo):
    listaProblemas = []
    settings.conectionGDB_arcpy()
    settings.conectionDB_arcpy()

    for ubigeo in datosDistrito(ubigeos):

        mxd = arcpy.mapping.MapDocument(mxd_croquis_emp)
        df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]

        print ubigeo
        queryCapasAuxiliares(ubigeo[0], mxd)
        informacionCabecera(ubigeo, mxd)
        agregarLyrUbigeo(mxd, ubigeo[0], "UBIGEO")

        for ruta in datosRutas(ubigeo[0]):
            informacioCabeceraRutasSCR(mxd, ruta[1], tipo)

            for emp in dataEmp(ruta[0]):
                informacionCabeceraRutasEMP(mxd, emp, ruta[0])
                for aer in dataAER(ruta[0]):
                    observacionesCroquis(mxd, ruta[2], ruta[0], aer)
                    informacionCabeceraAER(mxd, aer)
                    informacionCabeceraRutasViv(mxd, aer, ruta[0])
                    querysLayers(mxd, ruta[0], "IDRUTA", aer)
                    querysLayersAER(mxd, aer, "IDAER")
                    # listarevisar = zoomAER3(mxd, df, emp)
                    listarevisar = zoomAER(mxd, df)

                    sufijo = sufijoNombrePDF(aer)

                    if tipo == 1:
                        CroquisPathPdf = os.path.join(WorkSpaceCroquis, "Rural", ubigeo[0], ruta[0] + emp + sufijo[0] + ".pdf")
                        if len(listarevisar) > 0:
                            listaRevisar(ubigeo[0], os.path.join(ruta[0] + emp))
                    else:
                        CroquisPathPdf = os.path.join(WorkSpaceCroquis, "Rural_FEN", ubigeo[0], ruta[0] + emp + sufijo[0] + ".pdf")

                    print CroquisPathPdf
                    arcpy.RefreshActiveView()
                    arcpy.mapping.ExportToPDF(mxd, CroquisPathPdf, "PAGE_LAYOUT")
                    # --------------------------------------------------------------------------------------------------
                    # GUARDAR MXD
                    # mxd.saveACopy(r'D:\SegmentacionRuralV2\Procesamiento\Croquis\Rural_mxd\{}.mxd'.format(ruta[0] + emp + sufijo[0]))

                    # --------------------------------------------------------------------------------------------------

                    try:
                        # print CroquisPathPdf
                        arcpy.RefreshActiveView()
                        # arcpy.mapping.ExportToPDF(mxd, CroquisPathPdf, "PAGE_LAYOUT")
                    except KeyboardInterrupt:
                        print "Error en pdf"
                        sys.exit(0)
                    # except Exception as ex:
                    #     print ex
        del mxd
