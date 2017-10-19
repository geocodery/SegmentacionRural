#!/usr/bin/python
# -*- coding: utf-8 -*-

#    IMPORTANDO LIBRERIAS NECESARIAS
from reportlab.platypus import Image, Spacer, Table
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, TableStyle, PageBreak
from reportlab.lib.styles import ParagraphStyle as PS
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import arcpy
from Generales import settings



# VARIABLES

conexion = settings.conectionDB_arcpy()
conn = settings.conectionDB_pymmsql()
arcpy.env.overwriteOutput = True


#   DECLARANDO FUNCIONES

def vivCCPPfuera(ruta, aer, conn=conn):
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(VIV_CCPP) FROM CPV_SEGMENTACION_GDB.SDE.TB_CCPP WHERE IDRUTA = '{}' AND IDAER = '{}' AND ESTADO IN ('-1', '0', '10', '12')".format(ruta, aer))
    informacion = [x[0] for x in cursor]
    cursor.close()
    return informacion

def registros(rows):
    ini = 17
    rango = 25
    dato = ini
    while dato < rows:
        dato = dato + rango
    lista_ini = list(range(ini, dato - (rango - 1), rango))
    lista_fin = list(range(ini + rango, dato + 1, rango))
    if lista_fin[-1] < rows:
        lista_ini.append(lista_fin[-1])
        lista_fin.append(rows)
        final = zip(lista_ini, lista_fin)
    else:
        lista_fin[-1] = rows
        final = zip(lista_ini, lista_fin)
    return final


def Listado001ViviendasAer(ubigeos, WorkSpace, VW_DISTRITOS, SEGM_R_RUTA, SEGM_R_CCPPRUTA, SEGM_R_AER, VW_SEGM_R_AER_VIV, EscudoNacional, LogoInei, tipo):
    #   CREADO ESTILOS DE TEXTO

    h1 = PS(
        name='Heading1',
        fontSize=7,
        leading=8
    )

    h3 = PS(
        name='Normal',
        fontSize=6.5,
        leading=10,
        alignment=TA_CENTER
    )

    h4 = PS(
        name='Normal',
        fontSize=6.5,
        leading=10,
        alignment=TA_LEFT
    )

    h5 = PS(
        name='Heading1',
        fontSize=7,
        leading=8,
        alignment=TA_RIGHT
    )

    h_sub_tile = PS(
        name='Heading1',
        fontSize=10,
        leading=14,
        alignment=TA_CENTER
    )
    h_sub_tile_2 = PS(
        name='Heading1',
        fontSize=11,
        leading=14,
        alignment=TA_CENTER
    )

    #   EJECUCION DE LISTADOS 

    for ubigeo in [x for x in arcpy.da.SearchCursor(VW_DISTRITOS, ["UBIGEO", "DEPARTAMENTO", "PROVINCIA", "DISTRITO"], "UBIGEO = '{}'".format(ubigeos))]:
        departamento = ubigeo[1]
        coddep = ubigeo[0][0:2]
        provincia = ubigeo[2]
        codprov = ubigeo[0][2:4]
        distrito = ubigeo[3]
        coddist = ubigeo[0][4:6]

        EmpPos = 0 # FLUJO NORMAL
        # EmpPos = sum([x[0] for x in arcpy.da.SearchCursor(SEGM_R_RUTA, ["N_EMP_RUTA"],"UBIGEO = '{}' AND FLAG_NUEVO = 0".format(ubigeo[0]))])  # CON CCPP NUEVOS

        # conn = settings.conectionDB_pymmsql()
        # cursorsql = conn.cursor()
        # cursorsql.execute("DELETE FROM SEGM_R_EMP WHERE UBIGEO = '{}' AND FLAG_NUEVO = 1".format(ubigeo[0]) )
        # conn.commit()
        #
        # cursorsql2 = conn.cursor()
        # cursorsql2.execute("EXEC ACTUALIZAR_RUTAS '{}'".format(ubigeo[0]))
        # conn.commit()

        orderby = (None, 'ORDER BY {} ASC'.format('RUTA'))
        for ruta in [x for x in arcpy.da.SearchCursor(SEGM_R_RUTA, ["IDRUTA", "RUTA", "SCR", "N_EMP_RUTA", "IDSCR"], "UBIGEO = '{}'".format(ubigeo[0]), None, False, orderby)]: # FLUJO NORMAL
        # for ruta in [x for x in arcpy.da.SearchCursor(SEGM_R_RUTA, ["IDRUTA", "RUTA", "SCR", "N_EMP_RUTA", "IDSCR"], "UBIGEO = '{}' AND FLAG_NUEVO = 1".format(ubigeo[0]), None, False, orderby)]: #CASOS DE CCPP NUEVOS

            scr = ruta[2] if tipo == 1 else u""

            for n in range(ruta[3]):
                empadronador = str(EmpPos + 1).zfill(3)
                EmpPos = EmpPos + 1
                # cursorsql.execute("INSERT INTO SEGM_R_EMP (IDRUTA, EMP, EST_IMP, UBIGEO, IDSCR, FLAG_LEGAJO, SCR, FASE) VALUES ('{}', '{}', '0', '{}', '{}', '0', '{}', 'CPV2017')".format(ruta[0], empadronador, ubigeo[0], ruta[4], scr)) # FLUJO NORMAL
                # cursorsql.execute("INSERT INTO SEGM_R_EMP (IDRUTA, EMP, EST_IMP, UBIGEO, IDSCR, FLAG_LEGAJO, SCR, FASE, FLAG_NUEVO) VALUES ('{}', '{}', '0', '{}', '{}', '0', '{}', 'CPV2017', 1)".format(ruta[0], empadronador, ubigeo[0], ruta[4], scr)) # CON CCPP NUEVOS
                # conn.commit()
                aersruta = list(set([x[0] for x in arcpy.da.SearchCursor(SEGM_R_CCPPRUTA, ["IDAER"], "IDRUTA = '{}'".format(ruta[0]))]))

                for aer in aersruta:
                    aerini = aer[6:9]
                    aerfin = aer[9:12]
                    vivtrab = sum([x[0] for x in arcpy.da.SearchCursor(SEGM_R_CCPPRUTA, ["VIV_CCPP"], "IDRUTA = '{}' AND IDAER = '{}'".format(ruta[0], aer))])
                    vivfuera = vivCCPPfuera(ruta[0], aer)
                    if vivfuera[0] != None :
                        vivtrab = vivtrab - vivfuera[0]

                    vivaer = ([x[0] for x in arcpy.da.SearchCursor(SEGM_R_AER, ["VIV_AER"], "IDAER = '{}'".format(aer))])[0]

                    #   LISTA QUE CONTIENE LOS ELEMENTOS A GRAFICAR EN EL PDF

                    Elementos = []

                    #   AGREGANDO IMAGENES, TITULOS Y SUBTITULOS

                    if tipo == 1:
                        Titulo = Paragraph(u'CENSOS NACIONALES 2017: XII DE POBLACIÓN, VII DE VIVIENDA Y III DE COMUNIDADES INDÍGENAS', h_sub_tile)
                        Titulo2 = Paragraph(u'III Censo de Comunidades Nativas y I Censo de Comunidades Campesinas', h_sub_tile)
                        SubTitulo = Paragraph(u'<strong>LISTADO DE CENTROS POBLADOS Y VIVIENDAS DEL ÁREA DE EMPADRONAMIENTO RURAL</strong>', h_sub_tile_2)
                    else:
                        Titulo = Paragraph(u'CENSO DE LAS ÁREAS AFECTADAS POR ELFENÓMENO DE', h_sub_tile)
                        Titulo2 = Paragraph(u'EL NIÑO COSTERO', h_sub_tile)
                        SubTitulo = Paragraph(u'<strong>LISTADO DE CENTROS POBLADOS Y VIVIENDAS DEL ÁREA DE EMPADRONAMIENTO RURAL</strong>', h_sub_tile_2)


                    CabeceraPrincipal = [[Titulo, '', ''],
                                         [Image(EscudoNacional, width=50, height=50), Titulo2, Image(LogoInei, width=50, height=50)],
                                         ['', SubTitulo, '']]

                    Tabla0 = Table(CabeceraPrincipal, colWidths=[2 * cm, 14 * cm, 2 * cm])

                    Tabla0.setStyle( TableStyle([
                        ('GRID', (0, 0), (-1, -1), 1, colors.white),
                        ('SPAN', (0, 1), (0, 2)),
                        ('SPAN', (2, 1), (2, 2)),
                        ('SPAN', (0, 0), (2, 0)),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
                        ]))

                    Elementos.append(Tabla0)
                    Elementos.append(Spacer(0,10))

                    #   CREACION DE LAS TABLAS PARA LA ORGANIZACION DEL TEXTO
                    #   Se debe cargar la informacion en aquellos espacios donde se encuentra el texto 'R'



                    Filas = [
                            ['', '', '', '', '', '',Paragraph(u'<b>Doc.CPV.03.25</b>', h5), '', ''],
                            [Paragraph(u'<b>A. UBICACIÓN GEOGRÁFICA</b>', h1), '', '', '',Paragraph(u'<b>B. UBICACIÓN CENSAL</b>', h1), '', '', '', ''],
                            [Paragraph(u'<b>DEPARTAMENTO</b>', h1), u'{}'.format(coddep), u'{}'.format(departamento), '',Paragraph(u'<b>SECCIÓN Nº</b>', h1), '', '',u'{}'.format(scr), ''],
                            [Paragraph(u'<b>PROVINCIA</b>', h1), u'{}'.format(codprov), u'{}'.format(provincia), '', Paragraph(u'<b>A.E.R. Nº</b>', h1), '', '', u'DEL {} AL {}'.format(aerini, aerfin), ''],
                            [Paragraph(u'<b>DISTRITO</b>', h1), u'{}'.format(coddist), u'{}'.format(distrito),'', Paragraph(u'<b>C. TOTAL DE VIVIENDAS DEL AER</b>', h1),'', '', '', u'{}'.format(vivaer)],
                            ['', '','', '',Paragraph(u'<b>EMP. N°</b>', h1), u'{}'.format(empadronador), Paragraph(u'<b>VIVIENDAS POR TRABAJAR</b>', h1), '', u'{}'.format(vivtrab)]
                            ]


                    #   Permite el ajuste del ancho de la tabla

                    Tabla1 = Table(Filas, colWidths=[3.7 * cm, 1 * cm, 7.1 * cm, 0.3 * cm, 2 * cm, 1 * cm, 2 * cm, 1.7 * cm, 1 * cm])


                    #   Se cargan los estilos, como bordes, alineaciones, fondos, etc

                    Tabla1.setStyle(TableStyle([
                        ('TEXTCOLOR', (0, 0), (8, 0), colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('ALIGN', (1, 2), (1, 4), 'CENTER'),
                        ('ALIGN', (5, 5), (5, 5), 'CENTER'),
                        ('ALIGN', (8, 5), (8, 5), 'CENTER'),
                        ('ALIGN', (7, 2), (8, 2), 'CENTER'),
                        ('ALIGN', (7, 3), (8, 3), 'CENTER'),
                        ('ALIGN', (7, 4), (8, 4), 'CENTER'),
                        ('FONTSIZE', (0, 0), (-1, -1), 7),
                        ('GRID', (0, 1), (2, 4), 1, colors.black),
                        ('GRID', (4, 1), (8, 5), 1, colors.black),
                        ('SPAN', (0, 1), (2, 1)),
                        ('SPAN', (4, 1), (8, 1)),
                        ('SPAN', (4, 2), (6, 2)),
                        ('SPAN', (4, 3), (6, 3)),
                        ('SPAN', (4, 4), (7, 4)),
                        ('SPAN', (6, 5), (7, 5)),
                        ('SPAN', (6, 0), (8, 0)),
                        ('SPAN', (7, 2), (8, 2)),
                        ('SPAN', (7, 3), (8, 3)),
                        ('BACKGROUND', (0, 1), (2, 1), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                        ('BACKGROUND', (0, 2), (0, 4), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                        ('BACKGROUND', (4, 2), (6, 3), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                        ('BACKGROUND', (4, 4), (7, 4), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                        ('BACKGROUND', (6, 5), (7, 5), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                        ('BACKGROUND', (4, 5), (4, 5), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                        ('BACKGROUND', (4, 1), (8, 1), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255))
                    ]))


                    #   AGREGANDO LAS TABLAS A LA LISTA DE ELEMENTOS DEL PDF

                    Elementos.append(Tabla1)
                    Elementos.append(Spacer(0,10))

                    #   AGREGANDO CABECERA N° 2

                    Filas2  = [
                                [Paragraph(e, h3) for e in [u"<strong>D. INFORMACIÓN DE CENTROS POBLADOS Y VIVIENDAS</strong>", "", "", "", "", "", "", "", "", ""]],
                                [Paragraph(e, h3) for e in [u"<strong>Viv. Nº por CCPP</strong>", u"<strong>CENTRO POBLADO</strong>", "", "", u"<strong>DIRECCIÓN DE LA VIVIENDA</strong>", "", "", "", "", u"<strong>Nombres y Apellidos del<br/>JEFE DE HOGAR</strong>"]],
                                [Paragraph(e, h3) for e in [u"", u"<strong>Cod</strong>", u"<strong>Nombre</strong>", "", u"<strong>Tipo de Vía</strong>", u"<strong>Nombre de Vía</strong>", u"<strong>N° de Puerta</strong>", u"<strong>Piso N°</strong>", u"<strong>Km. N°</strong>", ""]],
                                [Paragraph(e, h3) for e in [u"<strong>(1)</strong>", u"<strong>(2)</strong>", u"<strong>(3)</strong>", "", u"<strong>(4)</strong>", u"<strong>(5)</strong>", u"<strong>(6)</strong>", u"<strong>(7)</strong>", u"<strong>(8)</strong>", u"<strong>(9)</strong>"]],
                               ]


                    Tabla2 = Table(Filas2, colWidths = [1.2 * cm, 1 * cm, 0.5 * cm, 4.3 * cm, 1.2 * cm, 2.6 * cm, 1.2 * cm, 1 * cm, 1 * cm, 5.8 * cm])

                    Tabla2.setStyle(TableStyle([
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('BACKGROUND', (0, 0), (-1, -1), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                        ('SPAN', (0, 0), (9, 0)),
                        ('SPAN', (1, 1), (3, 1)),
                        ('SPAN', (4, 1), (8, 1)),
                        ('SPAN', (9, 1), (9, 2)),
                        ('SPAN', (0, 1), (0, 2)),
                        ('SPAN', (2, 3), (3, 3)),
                        ('SPAN', (2, 2), (3, 2))
                        ]))

                    Elementos.append(Tabla2)

                    #   CUERPO QUE CONTIENE LOS LA INFORMACION A MOSTRAR

                    ListField = ["OR_VIV_RUTA", "CODCCPP", "NOMCCPP", "P20_NOMBRE", "P21", "P22_A", "P26", "P28", "JEFE_HOGAR"]
                    orderby = (None, 'ORDER BY {}, {} ASC'.format('OR_CCPP_DIST', 'ID_REG_OR'))
                    cursor = [x for x in arcpy.da.SearchCursor(VW_SEGM_R_AER_VIV, ListField, "IDAER = '{}' AND IDRUTA = '{}'".format(aer, ruta[0]), None, False, orderby)]

                    nrows = len(cursor)

                    if nrows > 17:

                        HojaRegistros = registros(nrows)
                        HojaRegistros.append((0, 17))
                        HojaRegistros.sort(key = lambda n:n[0])

                        for rangos in HojaRegistros:
                            for viv in cursor[rangos[0]: rangos[1]]:
                                if tipo == 1:
                                    nviv = "" if viv[0] == None else viv[0]
                                else:
                                    if viv[0] != None:
                                        nviv = ''
                                    else:
                                        if viv[0] == '99F':
                                            nviv = '99'
                                        else:
                                            nviv = viv[0]


                                    # nviv = "99" if viv[0] == '99F' elif viv[0] != None
                                codccpp = viv[1]
                                nomccpp = viv[2]
                                tipovia = viv[3]
                                nomvia = u"{}{}".format(viv[4][0:24], u"..") if len(viv[4]) > 26 else u'{}'.format(viv[4])
                                numpuerta = viv[5]
                                piso = viv[6]
                                nkm = u"" if viv[7] == None else u'{}'.format(viv[7])
                                jefehogar = u"" if viv[8] == None else u'{}'.format(viv[8])

                                Filas3 = [[u'{}'.format(nviv), u'{}'.format(codccpp), Paragraph(u'{}'.format(nomccpp), h4), u'', u'{}'.format(tipovia), Paragraph(u'{}'.format(nomvia), h4), u'{}'.format(numpuerta), u'{}'.format(piso), u'{}'.format(nkm), Paragraph(u'{}'.format(jefehogar), h4)]]

                                RegistrosIngresados = Table(Filas3,
                                          colWidths = [1.2 * cm, 1 * cm, 0.5 * cm, 4.3 * cm, 1.2 * cm, 2.6 * cm, 1.2 * cm, 1 * cm, 1 * cm, 5.8 * cm],
                                          rowHeights=[1 * cm])

                                RegistrosIngresados.setStyle(TableStyle([
                                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                        ('FONTSIZE', (0, 0), (-1, -1), 6.5),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ('ALIGN', (0, 0), (2, 0), 'CENTER'),
                                        ('ALIGN', (4, 0), (4, 0), 'CENTER'),
                                        ('ALIGN', (6, 0), (8, 0), 'CENTER'),
                                        ('SPAN', (2, 0), (3, 0))
                                        ]))

                                Elementos.append(RegistrosIngresados)
                            Elementos.append(PageBreak())
                            Elementos.append(Tabla2)
                        del Elementos[-1]
                        del Elementos[-1]

                    else:
                        for viv in cursor:
                            if tipo == 1:
                                nviv = "" if viv[0] in (None, 99) else viv[0]
                            else:
                                nviv = "" if viv[0] == None else viv[0]
                            codccpp = viv[1]
                            nomccpp = viv[2]
                            tipovia = viv[3]
                            nomvia = u"{}{}".format(viv[4][0:24], u"..") if len(viv[4]) > 26 else viv[4]
                            numpuerta = viv[5]
                            piso = viv[6]
                            nkm = u"" if viv[7] == None else viv[7]
                            jefehogar = u"" if viv[8] == None else viv[8]


                            Filas3 = [[u'{}'.format(nviv), u'{}'.format(codccpp), Paragraph(u'{}'.format(nomccpp), h4), u'', tipovia, Paragraph(u'{}'.format(nomvia), h4), u'{}'.format(numpuerta), u'{}'.format(piso), u'{}'.format(nkm), Paragraph(u'{}'.format(jefehogar), h4)]]

                            RegistrosIngresados = Table(Filas3,
                                      colWidths = [0.8 * cm, 1 * cm, 0.9 * cm, 4.3 * cm, 1.2 * cm, 2.6 * cm, 1.2 * cm, 1 * cm, 1 * cm, 5.8 * cm],
                                      rowHeights=[1 * cm])

                            RegistrosIngresados.setStyle(TableStyle([
                                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                    ('FONTSIZE', (0, 0), (-1, -1), 6.5),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ('ALIGN', (0, 0), (2, 0), 'CENTER'),
                                    ('ALIGN', (4, 0), (4, 0), 'CENTER'),
                                    ('ALIGN', (6, 0), (8, 0), 'CENTER'),
                                    ('SPAN', (2, 0), (3, 0))
                                    ]))

                            Elementos.append(RegistrosIngresados)

                        #   AGREGANDO NOTA PARA EL EMPADRONADOR

                    Elementos.append(Spacer(0, 10))
                    nota = u"<strong>Todas las viviendas que estén dentro de los límites de tu Área de Empadronamiento Rural (A.E.R.) deben ser empadronadas. Debes tener cuidado de no omitir ninguna vivienda.</strong>"
                    Filas4 = [[Paragraph(u"<strong>EMPADRONADOR:<br/>{}</strong>".format(nota), h3)]]
                    NotaEmpadronador = Table(Filas4, colWidths = [19.8 * cm], rowHeights = [1 * cm], style=[('GRID', (0, 0), (-1, -1), 1, colors.black), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')])
                    Elementos.append(NotaEmpadronador)

                    #   SE DETERMINAN LAS CARACTERISTICAS DEL PDF (RUTA DE ALMACENAJE, TAMAÑO DE LA HOJA, ETC)

                    num = ([x[0] for x in arcpy.da.SearchCursor(SEGM_R_AER, ["AER_POS"], "IDAER = '{}'".format(aer))])[0]


                    if tipo == 1:
                        PathPDF = u"{}\Rural\{}\{}{}{}.pdf".format(WorkSpace, ubigeo[0], ruta[0], empadronador, num)
                    else:
                        PathPDF = u"{}\Rural_FEN\{}\{}{}{}.pdf".format(WorkSpace, ubigeo[0], ruta[0], empadronador, num)

                    print PathPDF

                    pdf = SimpleDocTemplate(PathPDF, pagesize = A4, rightMargin=65,
                                        leftMargin=65,
                                        topMargin=0.5 *cm,
                                        bottomMargin=0.5 *cm,)

                    #   GENERACION DEL PDF FISICO

                    if nrows != 0:
                        pdf.build(Elementos)

        # cursorsql.close()
        # conn.close()
    final = "Finalizado"
    return final

