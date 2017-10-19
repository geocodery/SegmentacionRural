# -*- coding: utf-8 -*-

#    IMPORTANDO LIBRERIAS NECESARIAS


from reportlab.platypus import Image
from reportlab.platypus import Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, TableStyle, PageBreak
from reportlab.lib.styles import ParagraphStyle as PS
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import arcpy
from Generales import settings

def listado005ComunidadesIndigenas(ubigeos, WorkSpace, VW_DISTRITO, SEGM_R_CCPPRUTA, SEGM_R_EMP, SEGM_R_AER, EscudoNacional, LogoInei):
    settings.conectionDB_arcpy()

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


    for ubigeo in [x for x in arcpy.da.SearchCursor(VW_DISTRITO, ["UBIGEO", "DEPARTAMENTO", "PROVINCIA", "DISTRITO"], "UBIGEO = '{}'".format(ubigeos))]:

        conexion = settings.conectionDB_pymmsql()
        cursor1 = conexion.cursor()
        cursor1.execute("EXEC ACTUALIZAR_CCPP_INDIGENAS '{}'".format(ubigeo[0]))
        conexion.commit()

        cursor = conexion.cursor()
        cursor.execute("EXEC USP_ACTUALIZA_COMIND '{}'".format(ubigeo[0]))
        conexion.commit()

        coddep = ubigeo[0][0:2]
        departamento = ubigeo[1]
        codprov = ubigeo[0][2:4]
        provincia = ubigeo[2]
        coddist = ubigeo[0][4:6]
        distrito = ubigeo[3]

        contadorci = 0
        orderbyci = (None, 'ORDER BY OR_CCPP ASC')
        for ci in [x for x in arcpy.da.SearchCursor(SEGM_R_CCPPRUTA, ["IDCCPP"], "UBIGEO = {} AND (COD_CC IS NOT NULL OR COD_CN IS NOT NULL OR NOM_CC IS NOT NULL OR NOM_CN IS NOT NULL)".format(ubigeo[0]), None, False, orderbyci)]:
            contadorci = contadorci + 1
            orci = str(contadorci).zfill(3)
            idci = "{}{}".format(ci[0], orci)
            cursor.execute("UPDATE SEGM_R_CCPPRUTA SET OR_CI = '{}', IDCI = '{}' WHERE IDCCPP = '{}'".format(orci, idci, ci[0]))
            conexion.commit()


        orderby = (None, 'ORDER BY EMP ASC')
        for emp in [x for x in arcpy.da.SearchCursor(SEGM_R_EMP, ["IDSCR", "EMP", "IDRUTA"], "UBIGEO = '{}' AND FLAG_COMIND = 1".format(ubigeo[0]), None, False, orderby)]:

            scr = emp[0][11:14]
            empadronador = emp[1]
            aersruta = list(set([x[0] for x in arcpy.da.SearchCursor(SEGM_R_CCPPRUTA, ["IDAER"], "IDRUTA = '{}' AND (NOM_CC IS NOT NULL OR NOM_CN IS NOT NULL) ".format(emp[2]))]))


            for aer in aersruta:

                viviendas = sum([x[0] for x in arcpy.da.SearchCursor(SEGM_R_CCPPRUTA, ["VIV_CCPP"], "IDRUTA = '{}' AND (NOM_CC IS NOT NULL OR NOM_CN IS NOT NULL) AND IDAER = '{}'".format(emp[2], aer))])
                aerini = aer[6:9]
                aerfin = aer[9:12]

                #   LISTA QUE CONTIENE LOS ELEMENTOS A GRAFICAR EN EL PDF

                Elementos = []

                #   AGREGANDO IMAGENES, TITULOS Y SUBTITULOS

                Titulo = Paragraph(u'CENSOS NACIONALES 2017: XII DE POBLACIÓN, VII DE VIVIENDA Y III DE COMUNIDADES INDÍGENAS', h_sub_tile)
                Titulo2 = Paragraph(u'III Censo de Comunidades Nativas y I Censo de Comunidades Campesinas', h_sub_tile)
                SubTitulo = Paragraph(u'<strong>LISTADO DE CENTROS POBLADOS DONDE SE REALIZA EL EMPADRONAMIENTO DEL CENSO A COMUNIDADES NATIVAS Y CAMPESINAS DEL ÁREA DE EMPADRONAMIENTO RURAL</strong>', h_sub_tile_2)

                CabeceraPrincipal = [[Titulo, '', ''],
                                     [Image(EscudoNacional, width=50, height=50), Titulo2,
                                      Image(LogoInei, width=50, height=50)],
                                     ['', SubTitulo, '']]

                Tabla0 = Table(CabeceraPrincipal, colWidths=[2 * cm, 14 * cm, 2 * cm])

                Tabla0.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 1, colors.white),
                    ('SPAN', (0, 1), (0, 2)),
                    ('SPAN', (2, 1), (2, 2)),
                    ('SPAN', (0, 0), (2, 0)),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
                ]))

                Elementos.append(Tabla0)
                Elementos.append(Spacer(0, 10))

                #   CREACION DE LAS TABLAS PARA LA ORGANIZACION DEL TEXTO
                #   Se debe cargar la informacion en aquellos espacios donde se encuentra el texto 'R'



                Filas = [
                    ['', '', '', '', '', Paragraph(u'<b>Doc.CPV.03.25B</b>', h5)],
                    [Paragraph(u'<b>A. UBICACIÓN GEOGRÁFICA</b>', h1), '', '', '', Paragraph(u'<b>B. UBICACIÓN CENSAL</b>', h1), ''],
                    [Paragraph(u'<b>DEPARTAMENTO</b>', h1), u'{}'.format(coddep), u'{}'.format(departamento), '', Paragraph(u'<b>SECCIÓN Nº</b>', h1), u'{}'.format(scr)],
                    [Paragraph(u'<b>PROVINCIA</b>', h1), u'{}'.format(codprov), u'{}'.format(provincia), '', Paragraph(u'<b>A.E.R. Nº</b>', h1), u'DEL {} AL {}'.format(aerini, aerfin)],
                    [Paragraph(u'<b>DISTRITO</b>', h1), u'{}'.format(coddist), u'{}'.format(distrito), '', Paragraph(u'<b>EMPADRONADOR N°</b>', h1), u'{}'.format(empadronador)],
                    ['', '', '', '', Paragraph(u'<b>C. TOTAL DE VIVIENDAS</b>', h1), u'{}'.format(viviendas)]
                ]

                #   Permite el ajuste del ancho de la tabla

                Tabla1 = Table(Filas,
                               colWidths=[3.7 * cm, 1 * cm, 7.1 * cm, 0.3 * cm, 5 * cm, 2.7 * cm])

                #   Se cargan los estilos, como bordes, alineaciones, fondos, etc

                Tabla1.setStyle(TableStyle([
                    ('TEXTCOLOR', (0, 0), (5, 0), colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (1, 2), (1, 4), 'CENTER'),
                    ('ALIGN', (5, 2), (5, 5), 'CENTER'),
                    ('ALIGN', (0, 1), (2, 1), 'CENTER'),
                    ('ALIGN', (4, 1), (5, 1), 'CENTER'),
                    ('FONTSIZE', (0, 0), (-1, -1), 7),
                    ('GRID', (0, 1), (2, 4), 1, colors.black),
                    ('GRID', (4, 1), (5, 5), 1, colors.black),
                    ('SPAN', (0, 1), (2, 1)),
                    ('SPAN', (4, 1), (5, 1)),
                    ('BACKGROUND', (0, 1), (2, 1), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                    ('BACKGROUND', (0, 2), (0, 4), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                    ('BACKGROUND', (4, 1), (5, 1), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                    ('BACKGROUND', (4, 2), (4, 5), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255))
                ]))

                #   AGREGANDO LAS TABLAS A LA LISTA DE ELEMENTOS DEL PDF

                Elementos.append(Tabla1)
                Elementos.append(Spacer(0, 10))



                Filas2 = [
                    [Paragraph(e, h3) for e in [u"<strong>D. INFORMACIÓN DE LA COMUNIDAD NATIVA Y/O CAMPESINA</strong>", "", "", "", "", "", ""]],
                    [Paragraph(e, h3) for e in [u"<strong>Nº</strong>", u"<strong>Centro Poblado</strong>", "", "", u"<strong>Nombre de la Comunidad</strong>", u"<strong>TIPO DE<br/>COMUNIDAD</strong>", u"<strong>N° de<br/>viviendas</strong>"]],
                    [Paragraph(e, h3) for e in["", u"<strong>Código</strong>", u"<strong>Nombre</strong>", u"<strong>Categoría</strong>", "", "", ""]],
                    ]

                Tabla2 = Table(Filas2,
                               colWidths=[0.8 * cm, 1.5 * cm, 5.7 * cm, 2 * cm, 5.7 * cm, 2.5 * cm, 1.6 * cm])

                Tabla2.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('BACKGROUND', (0, 0), (-1, -1), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                    ('SPAN', (0, 0), (6, 0)),
                    ('SPAN', (0, 1), (0, 2)),
                    ('SPAN', (1, 1), (3, 1)),
                    ('SPAN', (4, 1), (4, 2)),
                    ('SPAN', (5, 1), (5, 2)),
                    ('SPAN', (6, 1), (6, 2)),
                ]))

                Elementos.append(Tabla2)

                contador = 0

                for ci in [x for x in arcpy.da.SearchCursor(SEGM_R_CCPPRUTA, ["CODCCPP", "NOMCCPP", "CAT_CCPP", "NOM_CC", "NOM_CN", "VIV_CCPP"], "IDAER = '{}' AND IDRUTA = '{}' AND (NOM_CC IS NOT NULL OR NOM_CN IS NOT NULL)".format(aer, emp[2]))]:
                    contador = contador + 1
                    codccpp = ci[0]
                    nomccpp = ci[1]
                    catccpp = ci[2]
                    nomci = ci[4] if ci[3] is None else ci[3]
                    # tipoci = 'NATIVA' if ci[3] is None else 'CAMPESINA'
                    if (ci[3] is not None) and (ci[4] is not None):
                        tipoci = 'NATIVA / CAMPESINA'
                    elif (ci[3] is not None) and (ci[4] is None):
                        tipoci = 'CAMPESINA'
                    elif (ci[4] is not None) and (ci[3] is None):
                        tipoci = 'NATIVA'


                    vivccpp = ci[5]

                    Filas3 = [[u'{}'.format(contador), u'{}'.format(codccpp), Paragraph(u'{}'.format(nomccpp), h4), Paragraph(u'{}'.format(catccpp), h4), Paragraph(u'{}'.format(nomci), h4), Paragraph(u'{}'.format(tipoci), h4), u'{}'.format(vivccpp)]]

                    RegistrosIngresados = Table(Filas3, colWidths=[0.8 * cm, 1.5 * cm, 5.7 * cm, 2 * cm, 5.7 * cm, 2.5 * cm, 1.6 * cm], rowHeights=[1 * cm])

                    RegistrosIngresados.setStyle(TableStyle([
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('FONTSIZE', (0, 0), (-1, -1), 6.5),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                        ('ALIGN', (6, 0), (6, 0), 'CENTER'),
                    ]))

                    Elementos.append(RegistrosIngresados)

                Elementos.append(Spacer(0, 10))

                Filas4 = [[Paragraph(u"<strong>E. OBSERVACIONES:</strong>", h3)]]
                Observaciones = Table(Filas4, colWidths=[19.8 * cm], style=[('GRID', (0, 0), (-1, -1), 1, colors.black),
                                                                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                                                            ('BACKGROUND', (0, 0), (-1, -1), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                                                                            ])
                Elementos.append(Observaciones)

                nota = u"<strong>{}</strong>".format('.'*909)     # ACEPTA 302 CARACTERES
                Filas5 = [[Paragraph(u"<strong>{}</strong>".format(nota), h4)]]
                NotaEmpadronador = Table(Filas5, colWidths=[19.8 * cm], rowHeights=[1.5 * cm], style=[('GRID', (0, 0), (-1, -1), 1, colors.black), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')])
                Elementos.append(NotaEmpadronador)

                num = ([x[0] for x in arcpy.da.SearchCursor(SEGM_R_AER, ["AER_POS"], "IDAER = '{}'".format(aer))])[0]


                PathPDF = r"{}\Rural\{}\{}{}{}-CI.pdf".format(WorkSpace, ubigeo[0], emp[2], empadronador, num)
                print PathPDF

                pdf = SimpleDocTemplate(PathPDF, pagesize=A4, rightMargin=65, leftMargin=65, topMargin=0.5 * cm, bottomMargin=0.5 * cm, )

                #   GENERACION DEL PDF FISICO

                pdf.build(Elementos)