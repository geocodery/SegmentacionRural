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

# def registrosReporte003(departamento):
#     informacion = []
#     cursor = conn.cursor()
#     cursor.execute("SELECT E.NOMBPROV, E.NOMBDIST, A.UBIGEO, A.CC, B.CN, C.CCPP, D.SUMA FROM (SELECT UBIGEO,COUNT(NOM_CC) AS CC FROM CCPP_INDIGENAS GROUP BY UBIGEO) A INNER JOIN (SELECT UBIGEO,COUNT(NOM_CN)AS CN FROM CCPP_INDIGENAS GROUP BY UBIGEO) B ON A.UBIGEO = B.UBIGEO INNER JOIN (SELECT UBIGEO,COUNT(CODCCPP) AS CCPP FROM CPV_SEGMENTACION_GDB.SDE.TB_CCPP GROUP BY UBIGEO) C ON A.UBIGEO COLLATE DATABASE_DEFAULT = C.UBIGEO COLLATE DATABASE_DEFAULT  INNER JOIN (SELECT UBIGEO,SUM(VIV_CCPP) AS SUMA FROM SEGM_R_CCPPRUTA GROUP BY UBIGEO) D ON D.UBIGEO COLLATE DATABASE_DEFAULT = C.UBIGEO COLLATE DATABASE_DEFAULT INNER JOIN (SELECT UBIGEO,NOMBPROV, NOMBDIST FROM TB_LIMITE_DIS) E ON E.UBIGEO COLLATE DATABASE_DEFAULT = D.UBIGEO COLLATE DATABASE_DEFAULT  WHERE SUBSTRING(A.UBIGEO,1,2) = '01' ORDER BY A.UBIGEO ".format(departamento))
#     for row in cursor.fetchall():
#         informacion.append(row)
#     cursor.close()
#     return informacion

def registrosReporte004(departamento):
    informacion = []
    cursor = conn.cursor()
    cursor.execute("SELECT E.NOMBPROV, E.NOMBDIST, A.UBIGEO, A.CC, B.CN, (A.CC + B.CN) AS CCPP, D.VIV FROM (SELECT UBIGEO,COUNT(NOM_CC) AS CC FROM CCPP_INDIGENAS GROUP BY UBIGEO) A  INNER JOIN (SELECT UBIGEO,COUNT(NOM_CN) AS CN FROM CCPP_INDIGENAS GROUP BY UBIGEO) B ON A.UBIGEO = B.UBIGEO  INNER JOIN (SELECT UBIGEO,SUM(VIV_CCPP) AS VIV FROM SEGM_R_CCPPRUTA WHERE (COD_CC IS NOT NULL OR COD_CN IS NOT NULL) GROUP BY UBIGEO) D ON D.UBIGEO COLLATE DATABASE_DEFAULT = A.UBIGEO COLLATE DATABASE_DEFAULT INNER JOIN (SELECT UBIGEO,NOMBPROV, NOMBDIST FROM TB_LIMITE_DIS) E ON E.UBIGEO COLLATE DATABASE_DEFAULT = D.UBIGEO COLLATE DATABASE_DEFAULT WHERE SUBSTRING(A.UBIGEO,1,2) = '{}' ORDER BY A.UBIGEO".format(departamento))
    for row in cursor.fetchall():
        informacion.append(row)
    cursor.close()
    return informacion

def cantregistros(rows):
    ini = 31
    rango = 36
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


def Reporte0004Rural(departamentos, WorkSpace, LIMITE_DEP, EscudoNacional, LogoInei):
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

    for dep in departamentos:
        for depart in [x for x in arcpy.da.SearchCursor(LIMITE_DEP, ["CCDD", "NOMBDEP"], "CCDD= '{}'".format(dep))]:
            coddep = depart[0]
            departamento = depart[1]

            Elementos = []

            #   AGREGANDO IMAGENES, TITULOS Y SUBTITULOS

            Titulo = Paragraph(u'CENSOS NACIONALES 2017: XII DE POBLACIÓN, VII DE VIVIENDA Y III DE COMUNIDADES INDÍGENAS', h_sub_tile)
            Titulo2 = Paragraph(u'III Censo de Comunidades Nativas y I Censo de Comunidades Campesinas', h_sub_tile)
            SubTitulo = Paragraph(u'<strong>NÚMERO DE COMUNIDADES NATIVAS Y CAMPESINAS, CENTROS POBLADOS Y VIVIENDAS DEL DEPARTAMENTO</strong>',h_sub_tile_2)

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
            Elementos.append(Spacer(0, 20))

            #   CREACION DE LAS TABLAS PARA LA ORGANIZACION DEL TEXTO
            #   Se debe cargar la informacion en aquellos espacios donde se encuentra el texto 'R'

            Filas = [
                    [Paragraph(u'<b>A. UBICACIÓN GEOGRÁFICA</b>', h1), '', '', '', ''],
                    [Paragraph(u'<b>DEPARTAMENTO</b>', h1), Paragraph(u'{}'.format(coddep), h3), Paragraph(u'{}'.format(departamento),h3), '', ''],
                    ['', '', '', '', Paragraph(u'<b>Doc.CPV.03.161B</b>', h5)],
                    ]

            #   Permite el ajuste del ancho de la tabla
            Tabla1 = Table(Filas, colWidths=[4 * cm, 2 * cm, 6 * cm, 3.5 * cm, 3.5 * cm])

            #   Se cargan los estilos, como bordes, alineaciones, fondos, etc
            Tabla1.setStyle(TableStyle([
                ('TEXTCOLOR', (0, 0), (0, 2), colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (2, 1), 1, colors.black),
                ('SPAN', (0, 0), (2, 0)),
                ('BACKGROUND', (0, 0), (2, 0), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                ('BACKGROUND', (0, 1), (0, 1), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
            ]))
            #
            #   AGREGANDO LAS TABLAS A LA LISTA DE ELEMENTOS DEL PDF
            Elementos.append(Tabla1)
            # Elementos.append(Spacer(0, 10))
            #
            #   AGREGANDO CABECERA DE REGISTROS

            datos = registrosReporte004(coddep)

            totalubigeos = len(datos)
            totalcc = 0
            totalcn = 0
            cantccpp = 0
            cantviv = 0

            for dato in datos:
                totalcc = totalcc + dato[3]
                totalcn = totalcn + dato[4]
                cantccpp = cantccpp + dato[5]
                cantviv = cantviv + dato[6]

            Filas2 = [
                [Paragraph(u"<strong>N°</strong>", h3),
                 Paragraph(u"<strong>UBIGEO</strong>", h3),
                 Paragraph(u"<strong>Provincia</strong>", h3),
                 Paragraph(u"<strong>Distrito</strong>", h3),
                 Paragraph(u"<strong>N° de Comunidades Campesinas</strong>", h3),
                 Paragraph(u"<strong>N° de Comunidades Nativas</strong>", h3),
                 Paragraph(u"<strong>N° de Centros Poblados</strong>", h3),
                 Paragraph(u"<strong>N° de Viviendas</strong>", h3)],
                [Paragraph(u"<strong>Total Departamental</strong>", h3),
                 '',
                 '',
                 '',
                 Paragraph(u"{}".format(totalcc), h3),
                 Paragraph(u"{}".format(totalcn), h3),
                 Paragraph(u"{}".format(cantccpp), h3),
                 Paragraph(u"{}".format(cantviv), h3)]
            ]
            Tabla2 = Table(Filas2,
                           colWidths=[1 * cm, 2 * cm, 4 * cm, 4 * cm, 2 * cm, 2 * cm, 2 * cm, 2 * cm]
                           )
            Tabla2.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('SPAN', (0, 1), (3, 1)),
                ('BACKGROUND', (0, 0), (-1, 0), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                ('BACKGROUND', (0, 1), (3, 1), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
            ]))
            Elementos.append(Tabla2)

            #   CUERPO QUE CONTIENE LOS LA INFORMACION A MOSTRAR

            nrows = len(datos)
            nreg = 0

            if nrows > 31:

                HojaRegistros = cantregistros(nrows)
                HojaRegistros.append((0, 31))
                HojaRegistros.sort(key=lambda n: n[0])

                for rangos in HojaRegistros:
                    if rangos != HojaRegistros[0]:
                        Filas2 = [
                            [Paragraph(u"<strong>N°</strong>", h3),
                             Paragraph(u"<strong>UBIGEO</strong>", h3),
                             Paragraph(u"<strong>Provincia</strong>", h3),
                             Paragraph(u"<strong>Distrito</strong>", h3),
                             Paragraph(u"<strong>N° de Comunidades Campesinas</strong>", h3),
                             Paragraph(u"<strong>N° de Comunidades Nativas</strong>", h3),
                             Paragraph(u"<strong>N° de Centros Poblados</strong>", h3),
                             Paragraph(u"<strong>N° de Viviendas</strong>", h3)]
                        ]
                        Tabla2 = Table(Filas2,
                                       colWidths=[1 * cm, 2 * cm, 4 * cm, 4 * cm,  2 * cm, 2 * cm, 2 * cm, 2 * cm]
                                       )
                        Tabla2.setStyle(TableStyle([
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('SPAN', (0, 1), (1, 1)),
                            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                            ('BACKGROUND', (0, 1), (1, 1), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                        ]))

                        Elementos.append(Tabla2)

                    for row in datos[rangos[0]: rangos[1]]:
                        nreg = nreg + 1
                        nombprov = row[0]
                        nombdist = row[1]
                        codubigeo = row[2]
                        cc = row[3]
                        cn = row[4]
                        ccpp = row[5]
                        vivccpp = row[6]

                        Filas3 = [[u'{}'.format(nreg), u'{}'.format(codubigeo), Paragraph(u'{}'.format(nombprov), h3), Paragraph(u'{}'.format(nombdist), h3), u'{}'.format(cc), u'{}'.format(cn), u'{}'.format(ccpp), u'{}'.format(vivccpp)]]

                        RegistrosIngresados = Table(Filas3,
                                                    colWidths = [1 * cm, 2 * cm, 4 * cm, 4 * cm, 2 * cm, 2 * cm, 2 * cm, 2 * cm]

                        )

                        RegistrosIngresados.setStyle(TableStyle([
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('FONTSIZE', (0, 0), (-1, -1), 6.5),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ]))

                        Elementos.append(RegistrosIngresados)
                    Elementos.append(PageBreak())
            else:
                for row in datos:
                    nreg = nreg + 1
                    nombprov = row[0]
                    nombdist = row[1]
                    codubigeo = row[2]
                    cc = row[3]
                    cn = row[4]
                    ccpp = row[5]
                    vivccpp = row[6]

                    Filas3 = [[u'{}'.format(nreg), u'{}'.format(codubigeo), Paragraph(u'{}'.format(nombprov), h3), Paragraph(u'{}'.format(nombdist), h3), u'{}'.format(cc), u'{}'.format(cn), u'{}'.format(ccpp), u'{}'.format(vivccpp)]]

                    RegistrosIngresados = Table(Filas3,
                                                colWidths=[1 * cm, 2 * cm, 4 * cm, 4 * cm, 2 * cm, 2 * cm, 2 * cm, 2 * cm]
                                                )

                    RegistrosIngresados.setStyle(TableStyle([
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('FONTSIZE', (0, 0), (-1, -1), 6.5),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ]))

                    Elementos.append(RegistrosIngresados)

            PathPDF = u"{}\Rural\Departamental\Comunidades_Indigenas\{}-R004.pdf".format(WorkSpace, coddep)

            print PathPDF

            pdf = SimpleDocTemplate(PathPDF, pagesize = A4, rightMargin=65,
                                leftMargin = 65,
                                topMargin = 0.5 * cm,
                                bottomMargin = 0.5 *cm,)

            pdf.build(Elementos)

    final = "Finalizado"
    return final