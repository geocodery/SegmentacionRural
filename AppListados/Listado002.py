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


conexion = settings.conectionDB_arcpy()
conn = settings.conectionDB_pymmsql()
arcpy.env.overwriteOutput = True


#   DECLARANDO FUNCIONES

def registros(rows, inicio = 27, rangoo = 25):
    ini = inicio # 18
    rango = rangoo # 25
    dato = inicio
    while dato < rows:
        dato = dato + rango
    lista_ini = list(range(ini, dato - (rango - 1), rango))
    lista_fin = list(range(ini + rango, dato + 1, rango))
    lista_fin[-1] = rows
    final = zip(lista_ini, lista_fin)
    return final

def ccppFuera(ubigeo, conn=conn):
    cursor = conn.cursor()
    cursor.execute("SELECT IDRUTA, NOMCCPP, IDAER FROM CPV_SEGMENTACION_GDB.SDE.TB_CCPP WHERE UBIGEO = '{}' AND AREA = '2' AND ESTADO IN ('-1', '0', '10', '12')".format(ubigeo))
    informacion = [[x[0], x[1], x[2]] for x in cursor]
    cursor.close()
    return informacion

def ccppFueraVal(idruta, idaer, conn=conn):
    cursor = conn.cursor()
    cursor.execute("SELECT NOMCCPP FROM CPV_SEGMENTACION_GDB.SDE.TB_CCPP WHERE IDRUTA = '{}' AND AREA = '2' AND ESTADO IN ('-1', '0', '10', '12') AND IDAER = '{}'".format(idruta, idaer))
    informacion = [x[0] for x in cursor]
    cursor.close()
    return informacion

def Listado002ccppAer(ubigeos, WorkSpace, VW_DISTRITO, SEGM_R_RUTAS, SEGM_R_CCPPRUTAS, SEGM_R_AER, EscudoNacional, LogoInei, tipo, SEGM_R_EMP):
    #   EJECUCION DE LISTADOS

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
        EmpPos = 0 # FLUJO NORMAL
        # EmpPos = sum([x[0] for x in arcpy.da.SearchCursor(SEGM_R_RUTAS, ["N_EMP_RUTA"], "UBIGEO = '{}' AND FLAG_NUEVO = 0".format(ubigeo[0]))])     # CON CCPP NUEVOS

        orderby = (None, 'ORDER BY {} ASC'.format('RUTA'))
        # for ruta in [x for x in arcpy.da.SearchCursor(SEGM_R_RUTAS, ["IDRUTA", "RUTA", "SCR", "N_EMP_RUTA"], "UBIGEO = '{}'".format(ubigeo[0]), None, False, orderby)]: # FLUJO NORMAL
        for ruta in [x for x in arcpy.da.SearchCursor(SEGM_R_RUTAS, ["IDRUTA", "RUTA", "SCR", "N_EMP_RUTA"], "UBIGEO = '{}' AND FLAG_NUEVO = 1".format(ubigeo[0]), None, False, orderby)]:  # CASOS DE CCPP NUEVOS
            scr = ruta[2] if tipo == 1 else u""

            for n in range(ruta[3]):
                empadronador = str(EmpPos + 1).zfill(3)
                EmpPos = EmpPos + 1

                aersruta = list(set([x[0] for x in arcpy.da.SearchCursor(SEGM_R_CCPPRUTAS, ["IDAER"], "IDRUTA = '{}'".format(ruta[0]))]))

                for aer in aersruta:
                    aerini = aer[6:9]
                    aerfin = aer[9:12]
                    vivtrab = sum([x[0] for x in arcpy.da.SearchCursor(SEGM_R_CCPPRUTAS, ["VIV_CCPP"], "IDRUTA = '{}' AND IDAER = '{}'".format(ruta[0], aer))])
                    vivaer = ([x[0] for x in arcpy.da.SearchCursor(SEGM_R_AER, ["VIV_AER"], "IDAER = '{}'".format(aer))])[0]

                #   LISTA QUE CONTIENE LOS ELEMENTOS A GRAFICAR EN EL PDF

                    Elementos = []


                    #   AGREGANDO IMAGENES, TITULOS Y SUBTITULOS

                    if tipo == 1:
                        Titulo = Paragraph(u'CENSOS NACIONALES 2017: XII DE POBLACIÓN, VII DE VIVIENDA Y III DE COMUNIDADES INDÍGENAS',h_sub_tile)
                        Titulo2 = Paragraph(u'III Censo de Comunidades Nativas y I Censo de Comunidades Campesinas',h_sub_tile)
                        SubTitulo = Paragraph(u'<strong>LISTADO DE CENTROS POBLADOS DEL ÁREA DE EMPADRONAMIENTO RURAL</strong>', h_sub_tile_2)
                    else:
                        Titulo = Paragraph(u'CENSO DE LAS ÁREAS AFECTADAS POR ELFENÓMENO DE', h_sub_tile)
                        Titulo2 = Paragraph(u'EL NIÑO COSTERO', h_sub_tile)
                        SubTitulo = Paragraph(u'<strong>LISTADO DE CENTROS POBLADOS DEL ÁREA DE EMPADRONAMIENTO RURAL</strong>', h_sub_tile_2)


                    CabeceraPrincipal = [[Titulo, '', ''],
                                         [Image(EscudoNacional, width=50, height=50), Titulo2, Image(LogoInei, width=50, height=50)],
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
                            ['', '', '', '', '', '',Paragraph(u'<b>Doc.CPV.03.25A</b>', h5), '', ''],
                            [Paragraph(u'<b>A. UBICACIÓN GEOGRÁFICA</b>', h1), '', '', '',Paragraph(u'<b>B. UBICACIÓN CENSAL</b>', h1), '', '', '', ''],
                            [Paragraph(u'<b>DEPARTAMENTO</b>', h1), u'{}'.format(coddep), '{}'.format(departamento), '',Paragraph(u'<b>SECCIÓN Nº</b>', h1), '', '','{}'.format(scr), ''],
                            [Paragraph(u'<b>PROVINCIA</b>', h1), u'{}'.format(codprov), u'{}'.format(provincia), '', Paragraph(u'<b>A.E.R. Nº</b>', h1), '', '', 'DEL {} AL {}'.format(aerini, aerfin), ''],
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

                    Filas2 = [
                        [Paragraph(e, h3) for e in [u"<strong>D. INFORMACIÓN DE CENTROS POBLADOS Y VIVIENDAS</strong>", "", "", "", ""]],
                        [Paragraph(e, h3) for e in [u"<strong>N°</strong>", u"<strong>CENTRO POBLADO</strong>", "", "", u"<strong>N° DE VIVIENDAS</strong>"]],
                        [Paragraph(e, h3) for e in ["", u"<strong>CÓDIGO</strong>", u"<strong>NOMBRE</strong>", u"<strong>CATEGORÍA</strong>", ""]],
                        ]

                    Tabla2 = Table(Filas2,
                              colWidths = [1 * cm, 1.7 * cm, 11.6 * cm, 3.5 * cm, 2 * cm], repeatRows=1)

                    Tabla2.setStyle(TableStyle(
                        [
                            ('GRID', (1, 1), (-2, -2), 1, colors.black),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('FONTSIZE', (0, 0), (-1, -1), 7),
                            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                            ('BACKGROUND', (0, 0), (-1, -1), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                            ('SPAN', (0, 0), (4, 0)),
                            ('SPAN', (0, 1), (0, 2)),
                            ('SPAN', (1, 1), (3, 1)),
                            ('SPAN', (4, 1), (4, 2)),
                            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
                            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                        ]
                    ))

                    Elementos.append(Tabla2)

                    #   CUERPO QUE CONTIENE LOS LA INFORMACION A MOSTRAR

                    ListField = ["OR_CCPP", "CODCCPP", "NOMCCPP", "CAT_CCPP", "VIV_CCPP"]
                    orderby = (None, 'ORDER BY {} ASC'.format('OR_CCPP'))
                    cursor = [x for x in arcpy.da.SearchCursor(SEGM_R_CCPPRUTAS, ListField, "IDAER = '{}' AND IDRUTA = '{}'".format(aer, ruta[0]), None, False, orderby)]
                    # for x in cursor:
                    #     print str(x[0]) + ": " + str(x[1])
                    nrows = len(cursor)

                    contador = 0

                    if nrows > 27:
                        SeccionesRegistros = registros(nrows)

                        SeccionesRegistros.append((0, 27))
                        SeccionesRegistros.sort(key = lambda n:n[0])


                        for rangos in SeccionesRegistros:
                            print rangos
                            for ccpp in cursor[rangos[0]:rangos[1]]:
                                print ccpp
                                contador = contador + 1
                                codccpp = ccpp[1]
                                nomccpp = ccpp[2]
                                categoriaccpp = ccpp[3]
                                numviv = ccpp[4]

                                Filas3 = [[u'{}'.format(contador), u'{}'.format(codccpp), Paragraph(u'{}'.format(nomccpp), h4), Paragraph(u'{}'.format(categoriaccpp), h4), u'{}'.format(numviv)]]

                                RegistrosIngresados = Table(Filas3,
                                          colWidths = [1 * cm, 1.7 * cm, 11.6 * cm, 3.5 * cm, 2 * cm],
                                          rowHeights=[0.7 * cm])

                                RegistrosIngresados.setStyle(TableStyle(
                                    [
                                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                        ('FONTSIZE', (0, 0), (-1, -1), 7),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                                        ('ALIGN', (4, 0), (4, 0), 'CENTER'),
                                    ]
                                ))
                                Elementos.append(RegistrosIngresados)
                            Elementos.append(PageBreak())
                            Elementos.append(Tabla2)
                        del Elementos[-1]
                        del Elementos[-1]
                    else:
                        for ccpp in cursor:
                            contador = contador + 1
                            codccpp = ccpp[1]
                            nomccpp = ccpp[2]
                            categoriaccpp = ccpp[3]
                            numviv = ccpp[4]

                            Filas3= [[u'{}'.format(contador), u'{}'.format(codccpp), Paragraph(u'{}'.format(nomccpp), h4), Paragraph(u'{}'.format(categoriaccpp), h4), u'{}'.format(numviv)]]

                            RegistrosIngresados = Table(Filas3,
                                      colWidths = [1 * cm, 1.7 * cm, 11.6 * cm, 3.5 * cm, 2 * cm],
                                      rowHeights=[0.7 * cm])

                            RegistrosIngresados.setStyle(TableStyle([
                                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                    ('FONTSIZE', (0, 0), (-1, -1), 7),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                                    ('ALIGN', (4, 0), (4, 0), 'CENTER'),]))

                            Elementos.append(RegistrosIngresados)



                    # COMPROBAR SI TIENE CCP CON ESTADO -1

                    ccppFuera1 = ccppFuera(ubigeos)
                    rutas = [x[0] for x in ccppFuera1]
                    # aers = [x[0] for x in ccppFuera1]
                    if ruta[0] in rutas:
                        infoccppFuera = ccppFueraVal(ruta[0], aer)

                    #   CUERPO QUE CONTIENE OBSERVACION REFERENTE A LOS CCPP CON ESTADO -1
                    #
                        if len(infoccppFuera) == 1:
                            Filas4 = [[Paragraph(u"<strong>E. OBSERVACIONES:</strong>", h3)]]

                            ObservacionesCabecera = Table(Filas4, colWidths=[19.8 * cm],
                                                          style=[('GRID', (0, 0), (-1, -1), 1, colors.black),
                                                                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                                                 ('BACKGROUND', (0, 0), (-1, -1),
                                                                  colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                                                                 ])

                            Elementos.append(Spacer(0, 20))
                            Elementos.append(ObservacionesCabecera)
                            # Filas5 = [[Paragraph(u"El centro poblado {} de nombre {} tiene  {} vivienda no tienen track de rutas".format(infoccppFuera[0][0], infoccppFuera[0][1], infoccppFuera[0][2]), h4)]]
                            nota = u"EL CENTRO POBLADO {} NO FIGURA EN EL DOC.CPV.03.25 LISTADO DE CENTROS POBLADOS Y VIVIENDAS DEL ÁREA DE EMPADRONAMIENTO RURAL.".format(infoccppFuera[0]) + "<br/>" + u"EMPADRONE A LAS VIVIENDAS Y PERSONAS DEL CENTRO POBLADO DE ACUERDO A LA PROGRAMACIÓN DE RUTAS ESTABLECIDA."  # ACEPTA 302 CARACTERES
                            Filas5 = [[Paragraph(u"<strong>{}</strong>".format(nota), h4)]]
                            NotaEmpadronador = Table(Filas5, colWidths=[19.8 * cm], rowHeights=[1.5 * cm],
                                                     style=[('GRID', (0, 0), (-1, -1), 1, colors.black),
                                                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')])
                            Elementos.append(NotaEmpadronador)
                        elif len(infoccppFuera) >= 1:
                            Filas4 = [[Paragraph(u"<strong>E. OBSERVACIONES:</strong>", h3)]]

                            ObservacionesCabecera = Table(Filas4, colWidths=[19.8 * cm],
                                                          style=[('GRID', (0, 0), (-1, -1), 1, colors.black),
                                                                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                                                 ('BACKGROUND', (0, 0), (-1, -1),
                                                                  colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                                                                 ])

                            Elementos.append(Spacer(0, 20))
                            Elementos.append(ObservacionesCabecera)
                            # Filas5 = [[Paragraph(u"El centro poblado {} de nombre {} tiene  {} vivienda no tienen track de rutas".format(infoccppFuera[0][0], infoccppFuera[0][1], infoccppFuera[0][2]), h4)]]
                            nota = u"LOS CENTROS POBLADOS {} NO FIGURAN EN EL DOC.CPV.03.25 LISTADO DE CENTROS POBLADOS Y VIVIENDAS DEL ÁREA DE EMPADRONAMIENTO RURAL.".format(', '.join(infoccppFuera)) +  "<br/>" + u"EMPADRONE A LAS VIVIENDAS Y PERSONAS DE LOS CENTROS POBLADOS DE ACUERDO A LA PROGRAMACIÓN DE RUTAS ESTABLECIDA."  # ACEPTA 302 CARACTERES
                            Filas5 = [[Paragraph(u"<strong>{}</strong>".format(nota), h4)]]
                            NotaEmpadronador = Table(Filas5, colWidths=[19.8 * cm], rowHeights=[1.5 * cm],
                                                     style=[('GRID', (0, 0), (-1, -1), 1, colors.black),
                                                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')])
                            Elementos.append(NotaEmpadronador)



                    num = ([x[0] for x in arcpy.da.SearchCursor(SEGM_R_AER, ["AER_POS"], "IDAER = '{}'".format(aer))])[0]

                    #   SE DETERMINAN LAS CARACTERISTICAS DEL PDF (RUTA DE ALMACENAJE, TAMAÑO DE LA HOJA, ETC)

                    nombrePDF = '{}{}{}'.format(ruta[0], empadronador, num)

                    if tipo == 1:
                        PathPDF = r"{}\Rural\{}\{}-CP.pdf".format(WorkSpace, ubigeo[0], nombrePDF)
                    else:
                        PathPDF = r"{}\Rural_FEN\{}\{}-CP.pdf".format(WorkSpace, ubigeo[0], nombrePDF)

                    print PathPDF

                    pdf = SimpleDocTemplate(PathPDF, pagesize = A4, rightMargin=65,
                                        leftMargin=65,
                                        topMargin=0.5 *cm,
                                        bottomMargin=0.5 *cm,)


                    #   GENERACION DEL PDF FISICO

                    pdf.build(Elementos)


    final = "Finalizado"
    return final

