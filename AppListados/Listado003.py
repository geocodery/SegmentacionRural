# -*- coding: utf-8 -*-

#    IMPORTANDO LIBRERIAS NECESARIAS

from reportlab.platypus import Image
from reportlab.platypus import Spacer
from reportlab.lib.pagesizes import A4                          #   ->  Importa el tamaño de hoja a utilizar
from reportlab.lib import colors                                #   ->  Importa colores
from reportlab.platypus import Table                            #   -> Importa las funcionalidades para crear tablas
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, TableStyle, PageBreak
from  reportlab.lib.styles import ParagraphStyle as PS
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import arcpy
from Generales import settings


arcpy.env.overwriteOutput = True
conn = settings.conectionDB_pymmsql()
conexion = settings.conectionDB_arcpy()


def ccppFuera(ubigeo, conn=conn):
    cursor = conn.cursor()
    cursor.execute("SELECT IDSCR, NOMCCPP FROM CPV_SEGMENTACION_GDB.SDE.TB_CCPP WHERE UBIGEO = '{}' AND AREA = '2' AND ESTADO IN ('-1', '0', '10', '12')".format(ubigeo))
    informacion = [[x[0], x[1]] for x in cursor]
    cursor.close()
    return informacion

def ccppFueraVal(idruta, conn=conn):
    cursor = conn.cursor()
    cursor.execute("SELECT NOMCCPP FROM CPV_SEGMENTACION_GDB.SDE.TB_CCPP WHERE IDSCR = '{}' AND AREA = '2' AND ESTADO IN ('-1', '0', '10', '12')".format(idruta))
    informacion = [x[0] for x in cursor]
    cursor.close()
    return informacion


def registros(rows):
    ini = 27
    rango = 35
    dato = 27
    while dato < rows:
        dato = dato + rango
    lista_ini = list(range(ini, dato - (rango - 1), rango))
    lista_fin = list(range(ini + rango, dato + 1, rango))
    lista_fin[-1] = rows
    final = zip(lista_ini, lista_fin)
    return final

def Listado003ccppSeccion(ubigeos, WorkSpace, VW_DISTRITO, SEGM_R_RUTAS, SEGM_R_CCPPRUTAS, EscudoNacional, LogoInei):

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
        departamento = ubigeo[1]
        coddep = ubigeo[0][0:2]
        provincia = ubigeo[2]
        codprov = ubigeo[0][2:4]
        distrito = ubigeo[3]
        coddist = ubigeo[0][4:6]

        conn = settings.conectionDB_pymmsql()
        cursorsql = conn.cursor()
        cursorsql.execute("DELETE FROM SEGM_R_SCR WHERE UBIGEO = '{}'".format(ubigeo[0])) # FLUJO NORMAL
        # cursorsql.execute("DELETE FROM SEGM_R_SCR WHERE UBIGEO = '{}' AND FLAG_NUEVO = 1".format(ubigeo[0])) # CON CCPP NUEVOS
        conn.commit()


        for seccion in list(set([x[0]for x in arcpy.da.SearchCursor(SEGM_R_RUTAS, ["IDSCR"], "UBIGEO = '{}' AND FLAG_NUEVO = 1".format(ubigeo[0]))])):
            scr = seccion[11:14]

            infoscr = [x[0] for x in arcpy.da.SearchCursor(SEGM_R_CCPPRUTAS, ["VIV_CCPP"], "IDSCR = '{}'".format(seccion))]
            ccppscr = len(infoscr)
            vivscr = sum(infoscr)

            # cursorsql.execute("INSERT INTO SEGM_R_SCR (UBIGEO, IDSCR, SCR, EST_IMP, FLAG_LEGAJO, VIV_SCR, CCPP_SCR) VALUES ('{}', '{}', '{}', '0', '0', {}, {})".format(ubigeo[0], seccion, scr, vivscr, ccppscr)) # FLUJO NORMAL
            cursorsql.execute("INSERT INTO SEGM_R_SCR (UBIGEO, IDSCR, SCR, EST_IMP, FLAG_LEGAJO, VIV_SCR, CCPP_SCR, FLAG_NUEVO) VALUES ('{}', '{}', '{}', '0', '0', {}, {}, '1')".format(ubigeo[0], seccion, scr, vivscr, ccppscr)) # CON CCPP NUEVOS
            conn.commit()
            #   LISTA QUE CONTIENE LOS ELEMENTOS A GRAFICAR EN EL PDF

            Elementos = []

            #   AGREGANDO IMAGENES, TITULOS Y SUBTITULOS

            Titulo = Paragraph(u'CENSOS NACIONALES 2017: XII DE POBLACIÓN, VII DE VIVIENDA Y III DE COMUNIDADES INDÍGENAS', h_sub_tile)
            Titulo2 = Paragraph(u'III Censo de Comunidades Nativas y I Censo de Comunidades Campesinas', h_sub_tile)
            SubTitulo = Paragraph(u'<strong>LISTADO DE CENTROS POBLADOS DE LA SECCIÓN CENSAL RURAL</strong>', h_sub_tile_2)

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
            Elementos.append(Spacer(0,10))


            #   CREACION DE LAS TABLAS PARA LA ORGANIZACION DEL TEXTO
            #   Se debe cargar la informacion en aquellos espacios donde se encuentra el texto 'R'

            Filas = [
                        ['', '', '', '', Paragraph('<b>Doc.CPV.03.78</b>', h5), '', ''],
                        [Paragraph('<b>A. UBICACIÓN GEOGRÁFICA</b>', h1), '', '', '', Paragraph('<b>B. UBICACIÓN CENSAL</b>', h1), '', ''],
                        [Paragraph('<b>DEPARTAMENTO</b>', h1), u'{}'.format(coddep), u'{}'.format(departamento), '', Paragraph(u'<b>SECCIÓN Nº</b>', h1), '{}'.format(scr), ''],
                        [Paragraph('<b>PROVINCIA</b>', h1), u'{}'.format(codprov),u'{}'.format(provincia), '', '','', ''],
                        [Paragraph('<b>DISTRITO</b>', h1), u'{}'.format(coddist), u'{}'.format(distrito),'', Paragraph('<b>C. TOTAL DE VIVIENDAS DE LA SECCIÓN.</b>', h1), '', '{}'.format(vivscr)],
                        ['', '', '','', '','']
                    ]

            #   Permite el ajuste del ancho de la tabla

            Tabla1 = Table(Filas, colWidths=[3.7 * cm, 1 * cm, 7.1 * cm, 0.3 * cm, 3.7 * cm, 1.5 * cm, 1.5 * cm])


            #   Se cargan los estilos, como bordes, alineaciones, fondos, etc

            Tabla1.setStyle(TableStyle([
                        ('FONTSIZE', (0, 0), (-1, -1), 7),
                        ('TEXTCOLOR', (0, 0), (6, 0), colors.white),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('ALIGN', (5, 2), (6, 2), 'CENTER'),
                        ('ALIGN', (6, 4), (6, 5), 'CENTER'),
                        ('ALIGN', (1, 2), (1, 4), 'CENTER'),
                        ('GRID', (0, 1), (2, 4), 1, colors.black),
                        ('GRID', (4, 4), (5, 5), 1, colors.black),
                        ('GRID', (4, 1), (6, 2), 1, colors.black),
                        ('GRID', (4, 4), (6, 5), 1, colors.black),
                        ('SPAN', (0, 1), (2, 1)),
                        ('SPAN', (4, 4), (5, 5)),
                        ('SPAN', (6, 4), (6, 5)),
                        ('SPAN', (4, 1), (6, 1)),
                        ('SPAN', (5, 2), (6, 2)),
                        ('SPAN', (4, 0), (6, 0)),
                        ('BACKGROUND', (0, 1), (2, 1), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                        ('BACKGROUND', (4, 1), (6, 1), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                        ('BACKGROUND', (0, 2), (0, 4), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                        ('BACKGROUND', (4, 2), (4, 2), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                        ('BACKGROUND', (4, 4), (5, 5), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255))
                    ]))


            #   AGREGANDO LAS TABLAS A LA LISTA DE ELEMENTOS DEL PDF

            Elementos.append(Tabla1)
            Elementos.append(Spacer(0,10))


            #   AGREGANDO CABECERA N° 2

            Filas2 = [
                [Paragraph(e, h3) for e in [u"<strong>D. INFORMACIÓN DE CENTROS POBLADOS Y VIVIENDAS</strong>", "", "", "", "", ""]],
                [Paragraph(e, h3) for e in [u"<strong>AER Nº</strong>", "", u"<strong>CENTRO POBLADO</strong>", "", "", u"<strong>N° DE VIVIENDAS</strong>"]],
                [Paragraph(e, h3) for e in [u"<strong>INICIAL</strong>", u"<strong>FINAL</strong>", u"<strong>CÓDIGO</strong>", u"<strong>NOMBRE</strong>", u"<strong>CATEGORÍA</strong>", ""]],
                ]

            Tabla2 = Table(Filas2,
                      colWidths = [1.3 * cm, 1.3 * cm, 1.7 * cm, 9 * cm, 3.5 * cm, 2 * cm], repeatRows=1)

            Tabla2.setStyle(TableStyle(
                [
                    ('GRID', (1, 1), (-2, -2), 1, colors.black),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTSIZE', (0, 0), (-1, -1), 7),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.Color(220.0/255, 220.0/255, 220.0/255)),
                    ('BACKGROUND', (0, 0), (-1, -1), colors.Color(220.0/255, 220.0/255, 220.0/255)),
                    ('SPAN', (0, 0), (5, 0)),
                    ('SPAN', (0, 1), (1, 1)),
                    ('SPAN', (2, 1), (4, 1)),
                    ('SPAN', (5, 1), (5, 2)),
                    ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.Color(220.0/255, 220.0/255, 220.0/255)),
                ]
            ))

            Elementos.append(Tabla2)



            #CUERPO QUE CONTIENE LOS LA INFORMACION A MOSTRAR

            nrows = len([x[0] for x in arcpy.da.SearchCursor(SEGM_R_CCPPRUTAS, ["CODCCPP"], "IDSCR = '{}'".format(seccion))])
            cursor = [x for x in arcpy.da.SearchCursor(SEGM_R_CCPPRUTAS, ["AER_INI", "AER_FIN", "CODCCPP", "NOMCCPP", "CAT_CCPP", "VIV_CCPP"] , "IDSCR = '{}'".format(seccion))]
            cursor.sort(key = lambda n:(n[0], n[2]))

            if nrows > 27:

                SeccionesRegistros = registros(nrows)

                SeccionesRegistros.append((0, 27))

                SeccionesRegistros.sort(key = lambda n:n[0])

                for rangos in SeccionesRegistros:

                    for ccpp in cursor[rangos[0]:rangos[1]]:
                        aeriniccpp = ccpp[0]
                        aerfinccpp = ccpp[1]
                        codccpp = ccpp[2]
                        nomccpp = ccpp[3]
                        categoriaccpp = ccpp[4]
                        numviv = ccpp[5]

                        Filas3 = [[u'{}'.format(aeriniccpp), u'{}'.format(aerfinccpp), u'{}'.format(codccpp), Paragraph(u'{}'.format(nomccpp), h4), Paragraph(u'{}'.format(categoriaccpp), h4), u'{}'.format(numviv)]]
                        # Filas3 = [[u'{}'.format(contador), u'{}'.format(codccpp), Paragraph(u'{}'.format(nomccpp), h4), Paragraph(u'{}'.format(catccpp), h4), Paragraph(u'{}'.format(nomci), h4), Paragraph(u'{}'.format(tipoci), h4), u'{}'.format(vivccpp)]]

                        RegistrosIngresados = Table(Filas3,
                                  colWidths = [1.3 * cm, 1.3 * cm, 1.7 * cm, 9 * cm, 3.5 * cm, 2 * cm],
                                  rowHeights=[0.7 * cm])

                        RegistrosIngresados.setStyle(TableStyle(
                            [
                                ('GRID', (1, 1), (-2, -2), 1, colors.black),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('FONTSIZE', (0, 0), (5, 0), 7),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ('ALIGN', (5, 0), (5, 0), 'CENTER'),
                                ('ALIGN', (0, 0), (2, 0), 'CENTER'),
                            ]
                        ))
                        Elementos.append(RegistrosIngresados)
                    Elementos.append(PageBreak())
                    Elementos.append(Tabla2)
                del Elementos[-1]
                del Elementos[-1]
            else:
                for ccpp in cursor:
                    aeriniccpp = ccpp[0]
                    aerfinccpp = ccpp[1]
                    codccpp = ccpp[2]
                    nomccpp = ccpp[3]
                    categoriaccpp = ccpp[4]
                    numviv = ccpp[5]

                    Filas3= [[u'{}'.format(aeriniccpp), u'{}'.format(aerfinccpp), u'{}'.format(codccpp), Paragraph(u'{}'.format(nomccpp), h4), Paragraph(u'{}'.format(categoriaccpp), h4), u'{}'.format(numviv)]]

                    RegistrosIngresados = Table(Filas3,
                              colWidths = [1.3 * cm, 1.3 * cm, 1.7 * cm, 9 * cm, 3.5 * cm, 2 * cm],
                              rowHeights=[0.7 * cm])

                    RegistrosIngresados.setStyle(TableStyle([
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                            ('FONTSIZE', (0, 0), (5, 0), 7),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('ALIGN', (5, 0), (5, 0), 'CENTER'),
                            ('ALIGN', (0, 0), (2, 0), 'CENTER'),]))

                    Elementos.append(RegistrosIngresados)

            # COMPROBAR SI TIENE CCP CON ESTADO -1

            ccppFuera1 = ccppFuera(ubigeos)
            scr = [x[0] for x in ccppFuera1]
            if seccion in scr:
                infoccppFuera = ccppFueraVal(seccion)

                #   AGREGANDO CABECERA N° 3
                Filas4 = [[Paragraph(u"<strong>E. OBSERVACIONES:</strong>", h3)]]

                ObservacionesCabecera = Table(Filas4, colWidths=[19.8 * cm],
                                              style=[('GRID', (0, 0), (-1, -1), 1, colors.black),
                                                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                                     ('BACKGROUND', (0, 0), (-1, -1),
                                                      colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                                                     ])

                Elementos.append(Spacer(0, 20))
                Elementos.append(ObservacionesCabecera)

                #   CUERPO QUE CONTIENE OBSERVACION REFERENTE A LOS CCPP CON ESTADO -1

                if len(infoccppFuera) == 1:
                    nota = u"EL CENTRO POBLADO {} NO FIGURA EN EL DOC.CPV.03.25 LISTADO DE CENTROS POBLADOS Y VIVIENDAS DEL ÁREA DE EMPADRONAMIENTO RURAL. ".format(infoccppFuera[0]) + "<br/>" + u"CONTROLE EL EMPADRONAMIENTO DE LAS VIVIENDAS Y PERSONAS DEL CENTRO POBLADO DE ACUERDO A LA PROGRAMACIÓN DE RUTAS ESTABLECIDA."  # ACEPTA 302 CARACTERES
                    Filas5 = [[Paragraph(u"<strong>{}</strong>".format(nota), h4)]]
                    NotaEmpadronador = Table(Filas5, colWidths=[19.8 * cm], rowHeights=[1.5 * cm],
                                             style=[('GRID', (0, 0), (-1, -1), 1, colors.black),
                                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')])
                    Elementos.append(NotaEmpadronador)
                elif len(infoccppFuera) >= 1:
                    nota = u"LOS CENTROS POBLADOS {} NO FIGURAN EN EL DOC.CPV.03.25 LISTADO DE CENTROS POBLADOS Y VIVIENDAS DEL ÁREA DE EMPADRONAMIENTO RURAL.".format(', '.join(infoccppFuera)) + "<br/>" + u"CONTROLE EL EMPADONAMIENTO DE LAS VIVIENDAS Y PERSONAS DE LOS CENTROS POBLADOS DE ACUERDO A LA PROGRAMACIÓN DE RUTAS ESTABLECIDA." # ACEPTA 302 CARACTERES
                    Filas5 = [[Paragraph(u"<strong>{}</strong>".format(nota), h4)]]
                    NotaEmpadronador = Table(Filas5, colWidths=[19.8 * cm], rowHeights=[1.5 * cm],
                                             style=[('GRID', (0, 0), (-1, -1), 1, colors.black),
                                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')])
                    Elementos.append(NotaEmpadronador)

            #   SE DETERMINAN LAS CARACTERISTICAS DEL PDF (RUTA DE ALMACENAJE, TAMAÑO DE LA HOJA, ETC)


            PathPDFsec = r"{}\Rural\{}\{}.pdf".format(WorkSpace, ubigeo[0], seccion)
            print PathPDFsec

            pdfsec = SimpleDocTemplate(PathPDFsec, pagesize = A4, rightMargin=65,
                                leftMargin=65,
                                topMargin=0.5 *cm,
                                bottomMargin=0.5 *cm,)


            #   GENERACION DEL PDF FISICO

            pdfsec.build(Elementos)

        #   IMPRESION DE FINALIZADO

        cursorsql.close()
        conn.close()
    finalizado = "Finalizado"
    return finalizado


