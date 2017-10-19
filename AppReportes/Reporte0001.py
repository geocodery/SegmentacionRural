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

def registrosReporte001(provincia):
    informacion = []
    cursor = conn.cursor()
    cursor.execute("SELECT A.UBIGEO, A.NOMBDIST, C.PEA_SCR, B.PEA_EMP, D.CCPP, D.VIV FROM (SELECT NOMBPROV, NOMBDIST, UBIGEO FROM MARCO_DISTRITO WHERE FASE = 'CPV2017' AND FLAG_AREA_R = 1) A INNER JOIN (SELECT DISTINCT UBIGEO, COUNT(EMP) AS EMP, SUM(CANT_PEA) AS PEA_EMP FROM SEGM_R_EMP WHERE FASE = 'CPV2017' GROUP BY UBIGEO) B 	ON B.UBIGEO COLLATE DATABASE_DEFAULT = A.UBIGEO COLLATE DATABASE_DEFAULT INNER JOIN (SELECT DISTINCT UBIGEO, COUNT(DISTINCT SCR) AS SECCIONES, SUM(CANT_PEA) AS PEA_SCR FROM SEGM_R_SCR GROUP BY UBIGEO) C 	ON C.UBIGEO COLLATE DATABASE_DEFAULT = A.UBIGEO COLLATE DATABASE_DEFAULT INNER JOIN (SELECT UBIGEO, COUNT(*) AS CCPP,SUM(VIV_CCPP) AS VIV FROM CPV_SEGMENTACION_GDB.SDE.TB_CCPP WHERE AREA = '2' GROUP BY UBIGEO) D ON D.UBIGEO COLLATE DATABASE_DEFAULT = A.UBIGEO COLLATE DATABASE_DEFAULT WHERE SUBSTRING(A.UBIGEO,1,4) = '{}' ORDER BY A.UBIGEO".format(provincia))
    for row in cursor.fetchall():
        informacion.append(row)
    cursor.close()
    return informacion

def cantregistros(rows):
    ini = 29
    rango = 39
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


def Reporte0001Rural(provincias, WorkSpace, LIMITE_PRO, EscudoNacional, LogoInei):
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

    for prov in provincias:
        for provincia in [x for x in arcpy.da.SearchCursor(LIMITE_PRO, ["CCDD", "NOMBDEP", "CCPP", "NOMBPROV", 'CODPROV'], "CODPROV = '{}'".format(prov))]:
            coddep = provincia[0]
            departamento = provincia[1]
            codprov = provincia[2]
            provi = provincia[3]

            Elementos = []

            #   AGREGANDO IMAGENES, TITULOS Y SUBTITULOS

            Titulo = Paragraph(u'CENSOS NACIONALES 2017: XII DE POBLACIÓN, VII DE VIVIENDA Y III DE COMUNIDADES INDÍGENAS', h_sub_tile)
            Titulo2 = Paragraph(u'III Censo de Comunidades Nativas y I Censo de Comunidades Campesinas', h_sub_tile)
            SubTitulo = Paragraph(u'<strong>NÚMERO DE JEFES DE SECCIÓN, EMPADRONADORES RURALES, CENTROS POBLADOS Y VIVIENDAS DE LA PROVINCIA</strong>', h_sub_tile_2)

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
                [Paragraph(u'<b>DEPARTAMENTO</b>', h1), Paragraph(u'{}'.format(coddep), h3), Paragraph(u'{}'.format(departamento), h3), '', ''],
                [Paragraph(u'<b>PROVINCIA</b>', h1), Paragraph(u'{}'.format(codprov), h3), Paragraph(u'{}'.format(provi), h3), '', ''],
                ['', '', '', '', Paragraph(u'<b>Doc.CPV.03.160A</b>', h5)],
            ]

            #   Permite el ajuste del ancho de la tabla
            Tabla1 = Table(Filas, colWidths=[4 * cm, 2 * cm, 6 * cm, 3.5 * cm, 3.5 * cm])

            #   Se cargan los estilos, como bordes, alineaciones, fondos, etc
            Tabla1.setStyle(TableStyle([
                ('TEXTCOLOR', (0, 0), (0, 3), colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (0, 1), 'CENTER'),
                ('ALIGN', (-1, -1), (-1, -1), 'CENTER'),
            #     ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('GRID', (0, 0), (2, 2), 1, colors.black),
                ('SPAN', (0, 0), (2, 0)),
                ('BACKGROUND', (0, 0), (2, 0), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                ('BACKGROUND', (0, 1), (0, 2), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
            ]))

            #   AGREGANDO LAS TABLAS A LA LISTA DE ELEMENTOS DEL PDF

            Elementos.append(Tabla1)

            #   AGREGANDO CABECERA DE REGISTROS

            datos = registrosReporte001(prov)

            totalubigeos = len(datos)
            secciones = 0
            empadronadores = 0
            cantccpp = 0
            cantviv = 0

            for dato in datos:
                secciones = secciones + dato[2]
                empadronadores = empadronadores + dato[3]
                cantccpp = cantccpp + dato[4]
                cantviv = cantviv + dato[5]

            Filas2 = [
                [Paragraph(u"<strong>N°</strong>", h3), Paragraph(u"<strong>Ubigeo</strong>", h3), Paragraph(u"<strong>Distrito</strong>", h3),Paragraph(u"<strong>N° de Jefes de Sección</strong>", h3), Paragraph(u"<strong>N° de Empadronadores</strong>", h3), Paragraph(u"<strong>N° de Centros Poblados</strong>", h3), Paragraph(u"<strong>N° de Viviendas</strong>", h3)],
                [Paragraph(u"<strong>Total Provincial</strong>", h3), '', '', Paragraph(u"{}".format(secciones), h3), Paragraph(u"{}".format(empadronadores), h3), Paragraph(u"{}".format(cantccpp), h3), Paragraph(u"{}".format(cantviv), h3)]
            ]
            Tabla2 = Table(Filas2,
                           colWidths=[0.8 * cm, 2.7 * cm, 5.1 * cm, 2.6 * cm, 2.6 * cm, 2.6 * cm, 2.6 * cm]
            )
            Tabla2.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('SPAN', (0, 1), (2, 1)),
                ('BACKGROUND', (0, 0), (-1, 0), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                ('BACKGROUND', (0, 1), (2, 1), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
            ]))
            Elementos.append(Tabla2)

            # #   CUERPO QUE CONTIENE LOS LA INFORMACION A MOSTRAR

            nrows = len(datos)
            nreg = 0

            if nrows > 29:

                HojaRegistros = cantregistros(nrows)
                HojaRegistros.append((0, 29))
                HojaRegistros.sort(key=lambda n: n[0])

                for rangos in HojaRegistros:
                    if rangos != HojaRegistros[0]:
                        Filas2 = [
                            [Paragraph(u"<strong>N°</strong>", h3), Paragraph(u"<strong>UBIGEO</strong>", h3), Paragraph(u"<strong>Distrito</strong>", h3),  Paragraph(u"<strong>N° de Jefes de Sección</strong>", h3),Paragraph(u"<strong>N° de Empadronadores</strong>", h3), Paragraph(u"<strong>N° de Centros Poblados</strong>", h3), Paragraph(u"<strong>N° de Viviendas</strong>", h3)],
                        ]
                        Tabla2 = Table(Filas2,
                                       colWidths=[0.8 * cm, 2.7 * cm, 5.1 * cm, 2.6 * cm, 2.6 * cm, 2.6 * cm, 2.6 * cm]
                                       )
                        Tabla2.setStyle(TableStyle([
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('BACKGROUND', (0, 0), (-1, -1), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                        ]))
                        Elementos.append(Tabla2)

                    for row in datos:
                        nreg = nreg + 1
                        codubigeo = row[0]
                        nombdist = row[1]
                        SCR = row[2]
                        Emp = row[3]
                        ccpp = row[4]
                        vivccpp = row[5]

                        Filas3 = [[Paragraph(u'{}'.format(nreg),h3), Paragraph(u'{}'.format(codubigeo),h3), Paragraph(u'{}'.format(nombdist), h3), Paragraph(u'{}'.format(SCR),h3), Paragraph(u'{}'.format(Emp),h3), Paragraph(u'{}'.format(ccpp),h3), Paragraph(u'{}'.format(vivccpp),h3)]]

                        RegistrosIngresados = Table(Filas3,
                                                    colWidths=[0.8 * cm, 2.7 * cm, 5.1 * cm, 2.6 * cm, 2.6 * cm, 2.6 * cm, 2.6 * cm]
                                                    )

                        RegistrosIngresados.setStyle(TableStyle([
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                # ('FONTSIZE', (0, 0), (-1, -1), 6.5),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ]))

                        Elementos.append(RegistrosIngresados)
                    Elementos.append(PageBreak())

            else:
                for row in datos:
                    nreg = nreg + 1
                    codubigeo = row[0]
                    nombdist = row[1]
                    SCR = row[2]
                    Emp = row[3]
                    ccpp = row[4]
                    vivccpp = row[5]

                    Filas3 = [[Paragraph(u'{}'.format(nreg), h3), Paragraph(u'{}'.format(codubigeo), h3), Paragraph(u'{}'.format(nombdist), h3), Paragraph(u'{}'.format(SCR), h3), Paragraph(u'{}'.format(Emp), h3), Paragraph(u'{}'.format(ccpp), h3), Paragraph(u'{}'.format(vivccpp), h3)]]

                    RegistrosIngresados = Table(Filas3,
                                                colWidths=[0.8 * cm, 2.7 * cm, 5.1 * cm, 2.6 * cm, 2.6 * cm, 2.6 * cm, 2.6 * cm]
                                                )

                    RegistrosIngresados.setStyle(TableStyle([
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        # ('FONTSIZE', (0, 0), (-1, -1), 6.5),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ]))

                    Elementos.append(RegistrosIngresados)


            PathPDF = u"{}\Rural\Provincial\Centros_Poblados\{}-R001.pdf".format(WorkSpace, provincia[4])

            print PathPDF

            pdf = SimpleDocTemplate(PathPDF, pagesize = A4, rightMargin=65,
                                leftMargin = 65,
                                topMargin = 0.5 * cm,
                                bottomMargin = 0.5 *cm,)

            pdf.build(Elementos)

    final = "Finalizado"
    return final