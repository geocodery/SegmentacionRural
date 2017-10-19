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

arcpy.env.overwriteOutput = True


conn = settings.conectionDB_pymmsql()


def registros(rows):
    ini = 26
    rango = 35
    dato = 26
    while dato < rows:
        dato = dato + rango
    lista_ini = list(range(ini, dato - (rango - 1), rango))
    lista_fin = list(range(ini + rango, dato + 1, rango))
    lista_fin[-1] = rows
    final = zip(lista_ini, lista_fin)
    return final


def empadronadorEtiqueta(idruta, conn = conn):
    cursor = conn.cursor()
    cursor.execute("SELECT EMP FROM SEGM_R_EMP WHERE IDRUTA = '{}'".format(idruta))
    informacion = [u"{}".format(x[0]) for x in cursor]
    cursor.close()
    etiqueta = "-".join(informacion)
    return etiqueta



def Listado006ProgRuta(ubigeos, WorkSpace, VW_DISTRITO, SEGM_R_RUTAS, SEGM_R_CCPPRUTAS, SEGM_R_AER, EscudoNacional, LogoInei, tipo):

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
        if tipo == 1:
            scr_tmp = [x[0] for x in arcpy.da.SearchCursor(SEGM_R_RUTAS, ["SCR"], "UBIGEO = '{}'".format(ubigeo[0]))]
            scr = u'{} - {}'.format(min(scr_tmp), max(scr_tmp))
        else:
            scr = u''


        aerini = min([x[0] for x in arcpy.da.SearchCursor(SEGM_R_AER, ["AER_INI"], "UBIGEO = '{}'".format(ubigeo[0]))])
        aerfin = max([x[0] for x in arcpy.da.SearchCursor(SEGM_R_AER, ["AER_FIN"], "UBIGEO = '{}'".format(ubigeo[0]))])
        viviendas = sum([x[0] for x in arcpy.da.SearchCursor(SEGM_R_RUTAS, ["N_VIV_RUTA"], "UBIGEO = '{}'".format(ubigeo[0]))])


        #   LISTA QUE CONTIENE LOS ELEMENTOS A GRAFICAR EN EL PDF
        
        Elementos = []


        #   AGREGANDO IMAGENES, TITULOS Y SUBTITULOS

        if tipo == 1:
            Titulo = Paragraph(u'CENSOS NACIONALES 2017: XII DE POBLACIÓN, VII DE VIVIENDA Y III DE COMUNIDADES INDÍGENAS', h_sub_tile)
            Titulo2 = Paragraph(u'III Censo de Comunidades Nativas y I Censo de Comunidades Campesinas', h_sub_tile)
            SubTitulo = Paragraph(u'<strong>MARCO DE SECCIONES CENSALES, ÁREAS DE EMPADRONAMIENTO RURAL Y CENTROS POBLADOS DEL DISTRITO</strong>', h_sub_tile_2)
        else:
            Titulo = Paragraph(u'CENSO DE LAS ÁREAS AFECTADAS POR ELFENÓMENO DE', h_sub_tile)
            Titulo2 = Paragraph(u'EL NIÑO COSTERO', h_sub_tile)
            SubTitulo = Paragraph(u'<strong>MARCO DE ÁREAS DE EMPADRONAMIENTO RURAL Y CENTROS POBLADOS DEL DISTRITO</strong>', h_sub_tile_2)


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
                ['', '', '', '', Paragraph(u'<b>Doc.CPV.03.159A</b>', h5),''],
                [Paragraph('<b>A. UBICACIÓN GEOGRÁFICA</b>', h1), '', '', '',Paragraph('<b>B. UBICACIÓN CENSAL</b>', h1), ''],
                [Paragraph('<b>DEPARTAMENTO</b>', h1), u'{}'.format(coddep), u'{}'.format(departamento), '',Paragraph(u'<b>SECCIÓN Nº</b>', h1), scr],
                [Paragraph('<b>PROVINCIA</b>', h1), u'{}'.format(codprov), u'{}'.format(provincia), '', Paragraph(u'<b>AER Nº</b>', h1), 'DEL {} AL {}'.format(aerini, aerfin)],
                [Paragraph('<b>DISTRITO</b>', h1), u'{}'.format(coddist), u'{}'.format(distrito), '', '',''],
                ['', '','', '',Paragraph('<b>C. TOTAL DE VIVIENDAS DEL DISTRITO.</b>', h1), '{}'.format(viviendas)]
                ]
    

        #   Permite el ajuste del ancho de la tabla

        Tabla = Table(Filas, colWidths=[3.7 * cm, 1 * cm, 7.1 * cm, 0.3 * cm, 4.5 * cm, 2.2 * cm])


        #   Se cargan los estilos, como bordes, alineaciones, fondos, etc

        Tabla.setStyle(TableStyle([
                    ('FONTSIZE', (0, 0), (-1, -1), 7),
                    ('TEXTCOLOR', (0, 0), (5, 0), colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (5, 2), (5, 5), 'CENTER'),
                    ('ALIGN', (1, 2), (1, 4), 'CENTER'),
                    ('GRID', (0, 1), (2, 4), 1, colors.black),
                    ('GRID', (4, 5), (5, 5), 1, colors.black),
                    ('GRID', (4, 1), (5, 3), 1, colors.black),
                    ('GRID', (4, 3), (5, 3), 1, colors.black),
                    ('SPAN', (0, 1), (2, 1)),
                    ('SPAN', (4, 1), (5, 1)),
                    ('SPAN', (4, 0), (5, 0)),
                    ('BACKGROUND', (0, 1), (2, 1), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                    ('BACKGROUND', (0, 2), (0, 4), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                    ('BACKGROUND', (4, 1), (4, 3), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                    ('BACKGROUND', (4, 5), (4, 5), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255)),
                    ('BACKGROUND', (4, 1), (5, 1), colors.Color(220.0 / 255, 220.0 / 255, 220.0 / 255))
                    ]))


        #   AGREGANDO LAS TABLAS A LA LISTA DE ELEMENTOS DEL PDF

        Elementos.append(Tabla)
        Elementos.append(Spacer(0,10))


        #   AGREGANDO CABECERA N° 2

        Filas2 = [
            [Paragraph(e, h3) for e in [u"<strong>D. INFORMACIÓN DE LAS SECCIONES CENSALES Y ÁREAS DE EMPADRONAMIENTO DEL DISTRITO</strong>", "", "", "","", "", "", "", ""]],
            [Paragraph(e, h3) for e in [u"<strong>SECCIÓN Nº</strong>", u"<strong>AER N°</strong>", "", u"<strong>RUTA</strong>", u"<strong>EMP</strong>", u"<strong>CENTRO POBLADO</strong>", "", "",u"<strong>N° ESTIMADO DE VIVIENDAS</strong>"]],
            [Paragraph(e, h3) for e in ["", u"<strong>INICIAL</strong>", u"<strong>FINAL</strong>", "", "", u"<strong>CÓDIGO</strong>", u"<strong>NOMBRE</strong>", u"<strong>CATEGORÍA</strong>", ""]]
            ]
        
        Tabla2 = Table(Filas2,
                  colWidths = [1.5 * cm, 1.5 * cm, 1.5 * cm, 1.5 * cm, 1.5 * cm, 1.5 * cm, 5.5 * cm, 2 * cm, 2.3 * cm])

        Tabla2.setStyle(TableStyle(
            [
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('BACKGROUND', (0, 0), (-1, -1), colors.Color(220.0/255, 220.0/255, 220.0/255)),
                ('SPAN', (0, 1), (0, 2)),
                ('SPAN', (0, 0), (8, 0)),
                ('SPAN', (1, 1), (2, 1)),
                ('SPAN', (3, 1), (3, 2)),
                ('SPAN', (4, 1), (4, 2)),
                ('SPAN', (5, 1), (7, 1)),
                ('SPAN', (8, 1), (8, 2)),
            ]
        ))

        Elementos.append(Tabla2)


        #CUERPO QUE CONTIENE LOS LA INFORMACION A MOSTRAR

        nrows = len([x[0] for x in arcpy.da.SearchCursor(SEGM_R_CCPPRUTAS, ["CODCCPP"], "UBIGEO = '{}'".format(ubigeo[0]))])
        cursor = [x for x in arcpy.da.SearchCursor(SEGM_R_CCPPRUTAS, ["SCR", "AER_INI", "AER_FIN", "RUTA", "CODCCPP", "NOMCCPP", "CAT_CCPP", "VIV_CCPP", "OR_CCPP", "IDRUTA"] , "UBIGEO = '{}'".format(ubigeo[0]))]
        cursor.sort(key = lambda n:(n[0], n[3], n[-1]))
        
        if nrows > 26:

            SeccionesRegistros = registros(nrows)
            
            SeccionesRegistros.append((0, 26))

            SeccionesRegistros.sort(key = lambda n:n[0])

            for rangos in SeccionesRegistros:
                
                for ccpp in cursor[rangos[0]:rangos[1]]:
                    scr = ccpp[0] if tipo == 1 else u''
                    aeriniccpp = ccpp[1]
                    aerfinccpp = ccpp[2]
                    rutaccpp = ccpp[3]
                    emp = empadronadorEtiqueta(ccpp[9])
                    codccpp = ccpp[4]
                    nomccpp = ccpp[5]
                    categoriaccpp = ccpp[6]
                    numviv = ccpp[7]
                    
                    registrosdist = [[scr, u'{}'.format(aeriniccpp), u'{}'.format(aerfinccpp), u'{}'.format(rutaccpp), u'{}'.format(emp), u'{}'.format(codccpp), Paragraph(u'{}'.format(nomccpp), h4), Paragraph(u'{}'.format(categoriaccpp), h4), u'{}'.format(numviv)]]

                    RegistrosIngresados = Table(registrosdist,
                              colWidths = [1.5 * cm, 1.5 * cm, 1.5 * cm, 1.5 * cm, 1.5 * cm, 1.5 * cm, 5.5 * cm, 2 * cm, 2.3 * cm],
                              rowHeights=[0.7 * cm])
                    
                    RegistrosIngresados.setStyle(TableStyle(
                        [
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                            ('FONTSIZE', (0, 0), (-1, -1), 7),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('ALIGN', (0, 0), (5, 0), 'CENTER'),
                        ]
                    ))
                    Elementos.append(RegistrosIngresados)
                Elementos.append(PageBreak())
                Elementos.append(Tabla2)
            del Elementos[-1]
            del Elementos[-1] 
        else:
            for ccpp in cursor:
                scr = ccpp[0] if tipo == 1 else u''
                aeriniccpp = ccpp[1]
                aerfinccpp = ccpp[2]
                rutaccpp = ccpp[3]
                emp = empadronadorEtiqueta(ccpp[9])
                codccpp = ccpp[4]
                nomccpp = ccpp[5]
                categoriaccpp = ccpp[6]
                numviv = ccpp[7]

                registrosdist = [[scr, u'{}'.format(aeriniccpp), u'{}'.format(aerfinccpp), u'{}'.format(rutaccpp), u'{}'.format(emp), u'{}'.format(codccpp), Paragraph(u'{}'.format(nomccpp), h4), Paragraph(u'{}'.format(categoriaccpp), h4), u'{}'.format(numviv)]]

                RegistrosIngresados = Table(registrosdist,
                          colWidths = [1.5 * cm, 1.5 * cm, 1.5 * cm, 1.5 * cm, 1.5 * cm, 1.5 * cm, 5.5 * cm, 2 * cm, 2.3 * cm],
                          rowHeights=[0.7 * cm])
                
                RegistrosIngresados.setStyle(TableStyle(
                    [
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('FONTSIZE', (0, 0), (-1, -1), 7),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('ALIGN', (0, 0), (5, 0), 'CENTER'),
                    ]
                ))
                Elementos.append(RegistrosIngresados)

        #   SE DETERMINAN LAS CARACTERISTICAS DEL PDF (RUTA DE ALMACENAJE, TAMAÑO DE LA HOJA, ETC)
        

        if tipo == 1:
            PathPDF = r"{}\Rural\{}\{}.pdf".format(WorkSpace, ubigeo[0], ubigeo[0])
        else:
            PathPDF = r"{}\Rural_FEN\{}\{}.pdf".format(WorkSpace, ubigeo[0], ubigeo[0])

        print PathPDF

        pdfsec = SimpleDocTemplate(PathPDF, pagesize=A4, rightMargin=65, leftMargin=65, topMargin=0.5*cm, bottomMargin=0.5*cm,)

        #   GENERACION DEL PDF FISICO

        pdfsec.build(Elementos)


    #   IMPRESION DE FINALIZADO
    finalizado = "Finalizado"
    return finalizado


conexion = settings.conectionDB_arcpy()