import arcpy
import pyPdf
import os
from Generales import settings

conn = settings.conectionDB_pymmsql()

##########################################################################################################################################################
##############################################              CALIDAD                 ######################################################################
##########################################################################################################################################################

def borrarEMPant(ubigeo, conexion=conn):
    cursor1 = conexion.cursor()
    cursor1.execute("DELETE FROM CALIDAD_R_EMP WHERE UBIGEO = '{}'".format(ubigeo))
    cursor1.close()

def extraerEmp(ubigeo, conexion=conn):
    cursor = conexion.cursor()
    cursor.execute("SELECT IDEMP, UBIGEO, EMP, SCR FROM SEGM_R_EMP WHERE UBIGEO = '{}'".format(ubigeo))
    informacion = [[x[0], x[1], x[2], x[3]] for x in cursor]
    cursor.close()
    return informacion

def subirValoresEmp(idemp, conexion=conn):
    cursor = conexion.cursor()
    for x in idemp:
        cursor.execute("INSERT INTO CALIDAD_R_EMP (ID, UBIGEO, EMP, SCR, IND1, IND2, IND3, IND4, FLAG_CALIDAD) VALUES ({}, {}, {}, {}, 0,0,0,0,0)".format(x[0], x[1], x[2], x[3]))
    cursor.close()

def actualizaIDEMP(ubigeo):
    cursor = conn.cursor()
    cursor.execute("UPDATE CPV_SEGMENTACION.dbo.SEGM_R_EMP SET IDEMP = IDRUTA + EMP WHERE UBIGEO = '{}'".format(ubigeo))
    conn.commit()
    cursor.close()

##########################################################################################################################################################

def actualizaEmpadronadores(paginas, idruta, empadronador, conn=conn):
    cursor = conn.cursor()
    cursor.execute("UPDATE SEGM_R_EMP SET CANT_PAG = {} WHERE IDRUTA = '{}' AND EMP = '{}'".format(paginas, idruta, empadronador))
    conn.commit()
    cursor.close()

def actualizaSecciones(paginas, idscr, conn=conn):
    cursor = conn.cursor()
    cursor.execute("UPDATE SEGM_R_SCR SET CANT_PAG = {} WHERE IDSCR = '{}'".format(paginas, idscr))
    conn.commit()
    cursor.close()

def actualizaDistritos(paginas, ubigeo, conn=conn):
    cursor = conn.cursor()
    cursor.execute("UPDATE SEGM_R_DIST SET CANT_PAG = {} WHERE UBIGEO = '{}'".format(paginas, ubigeo))
    conn.commit()
    cursor.close()

def actualizaCodCroquis(id, nivel, conn=conn):
    if nivel == 'Empadronador':
        cursor = conn.cursor()
        cursor.execute("UPDATE SEGM_R_EMP SET COD_CROQ = '{}' WHERE IDEMP = '{}'".format(id,id))
        conn.commit()
        cursor.close()
    elif nivel == 'Seccion':
        cursor = conn.cursor()
        cursor.execute("UPDATE SEGM_R_SCR SET COD_CROQ = '{}' WHERE IDSCR = '{}'".format(id, id))
        conn.commit()
        cursor.close()
    elif nivel == 'Distrito':
        cursor = conn.cursor()
        cursor.execute("UPDATE SEGM_R_DIST SET COD_CROQ = '{}' WHERE UBIGEO = '{}'".format(id, id))
        conn.commit()
        cursor.close()

def contarPag(ubigeo):
    cursor = conn.cursor()
    cursor.execute("SELECT RUTA_CROQ FROM SEGM_R_EMP WHERE UBIGEO = '{}'".format(ubigeo))
    lista = [x[0] for x in cursor]
    conn.commit()
    cursor.close()
    for pathEmp in lista:
        pdf = pyPdf.PdfFileReader(open(pathEmp, "rb"))
        cant_pag = pdf.getNumPages()
        cursor2 = conn.cursor()
        cursor2.execute("UPDATE SEGM_R_EMP SET CANT_PAG = {} WHERE RUTA_CROQ = '{}'".format(cant_pag, pathEmp))
        conn.commit()
        cursor2.close()
    cursor = conn.cursor()
    cursor.execute("SELECT RUTA_CROQ FROM SEGM_R_SCR WHERE UBIGEO = '{}'".format(ubigeo))
    lista2 = [x[0] for x in cursor]
    conn.commit()
    cursor.close()
    for pathScr in lista2:
        pdf = pyPdf.PdfFileReader(open(pathScr, "rb"))
        cant_pag = pdf.getNumPages()
        cursor2 = conn.cursor()
        cursor2.execute("UPDATE SEGM_R_SCR SET CANT_PAG = {} WHERE RUTA_CROQ = '{}'".format(cant_pag, pathScr))
        conn.commit()
        cursor2.close()
    cursor = conn.cursor()
    cursor.execute("SELECT RUTA_CROQ FROM SEGM_R_DIST WHERE UBIGEO = '{}'".format(ubigeo))
    lista3 = [x[0] for x in cursor]
    conn.commit()
    cursor.close()
    for pathDist in lista3:
        pdf = pyPdf.PdfFileReader(open(pathDist, "rb"))
        cant_pag = pdf.getNumPages()
        cursor2 = conn.cursor()
        cursor2.execute("UPDATE SEGM_R_DIST SET CANT_PAG = {} WHERE RUTA_CROQ = '{}'".format(cant_pag, pathDist))
        conn.commit()
        cursor2.close()

def actualizaRutaCroquis(ruta_croq, ruta_web, id, nivel, conn=conn):
    if nivel == 'Empadronador':
        cursor = conn.cursor()
        cursor.execute("UPDATE SEGM_R_EMP SET RUTA_CROQ = '{}' WHERE IDEMP = '{}'  UPDATE SEGM_R_EMP SET RUTA_WEB = '{}' WHERE IDEMP = '{}'".format(ruta_croq, id, ruta_web, id))
        conn.commit()
        cursor.close()
    elif nivel == 'Seccion':
        cursor = conn.cursor()
        cursor.execute("UPDATE SEGM_R_SCR SET RUTA_CROQ = '{}' WHERE IDSCR = '{}'  UPDATE SEGM_R_SCR SET RUTA_WEB = '{}' WHERE IDSCR = '{}'".format(ruta_croq, id, ruta_web, id))
        conn.commit()
        cursor.close()
    elif nivel == 'Distrito':
        cursor = conn.cursor()
        cursor.execute("UPDATE SEGM_R_DIST SET RUTA_CROQ = '{}' WHERE UBIGEO = '{}'  UPDATE SEGM_R_DIST SET RUTA_WEB = '{}' WHERE UBIGEO = '{}'".format(ruta_croq, id, ruta_web, id))
        conn.commit()
        cursor.close()

def actualizaFase(fase, ubigeo, nivel, conn=conn):
    if nivel == 'Empadronador':
        cursor = conn.cursor()
        cursor.execute("UPDATE SEGM_R_EMP SET FASE = '{}' WHERE UBIGEO = '{}'".format(fase, ubigeo))
        conn.commit()
        cursor.close()
    elif nivel == 'Seccion':
        cursor = conn.cursor()
        cursor.execute("UPDATE SEGM_R_SCR SET FASE = '{}' WHERE UBIGEO = '{}'".format(fase, ubigeo))
        conn.commit()
        cursor.close()
    elif nivel == 'Distrito':
        cursor = conn.cursor()
        cursor.execute("UPDATE SEGM_R_DIST SET FASE = '{}' WHERE UBIGEO = '{}'".format(fase, ubigeo))
        conn.commit()
        cursor.close()

def actualizarModuloSegRural(ubigeo, tipo, conn=conn):
    cursor = conn.cursor()
    if tipo == 1:
        cursor.execute("UPDATE TB_MODULO_ASIGN_R SET FLAG_SEGM = 1 WHERE UBIGEO = '{}'".format(ubigeo))
        conn.commit()
    else:
        cursor.execute("UPDATE TB_MODULO_ASIGN_R SET FLAG_FEN = 1 WHERE UBIGEO = '{}'".format(ubigeo))
        conn.commit()
    cursor.close()

def mergeEmpadronadores(FileServer, pathlistados, pathcroquis, pathrutas, ubigeos, fase, tipo):

    nivel = 'Empadronador'
    if tipo == 1:
        area = 'Rural'
    else:
        area = 'Rural_FEN'
    for ubigeo in ubigeos:
        actualizaIDEMP(ubigeo)
        actualizaFase(fase, ubigeo, nivel)
        listados = '{}\{}\{}'.format(pathlistados, area, ubigeo)
        croquis = '{}\{}\{}'.format(pathcroquis, area, ubigeo)
        progrutas = '{}\{}\{}'.format(pathrutas, area, ubigeo)

        #####
        cursor = conn.cursor()
        # cursor.execute("SELECT IDEMP FROM SEGM_R_EMP WHERE UBIGEO = '{}' AND FASE = '{}'".format(ubigeo, fase))  # FLUJO NORMAL
        cursor.execute("SELECT IDEMP FROM SEGM_R_EMP WHERE UBIGEO = '{}' AND FASE = '{}' AND FLAG_NUEVO = 1".format(ubigeo, fase))  # CON CCPP NUEVOS
        informacion = [x[0] for x in cursor]
        cursor.close()
        #####
        namePDF = informacion
        ListadosList = [x for x in os.listdir(listados) if len(x) >= 26]
        croquisList = [x[0:22] for x in os.listdir(croquis) if len(x) == 26]
        progRutasEmp = [x for x in os.listdir(progrutas) if len(x) == 30]


        for x in namePDF:
            pdfname = x
            pathPDF = r'{}\{}\{}\{}\{}.pdf'.format(FileServer, area, fase, ubigeo, pdfname)
            pathPDF_nuevo = r'{}\{}\{}-nuevos\{}\{}.pdf'.format(FileServer, area, fase, ubigeo, pdfname)
            pathPDF_croquis = r'{}\{}\{}-croquis\{}\{}.pdf'.format(FileServer, area, fase, ubigeo, pdfname)
            ruta_croquis = pathPDF
            ruta_web = '/cpv2017/croquis-listado/{}/{}/{}/{}.pdf'.format(area, fase, ubigeo, pdfname)
            pdfDoc = arcpy.mapping.PDFDocumentCreate(pathPDF)
            pdfDoc_nuevo = arcpy.mapping.PDFDocumentCreate(pathPDF_nuevo)
            pathPDF_croquis = arcpy.mapping.PDFDocumentCreate(pathPDF_croquis)

            for m in croquisList:
                if m[0:20] == pdfname:
                    pdfDoc.appendPages(r'{}\{}\{}\{}.pdf'.format(pathcroquis, area, ubigeo, m))
                    pdfDoc_nuevo.appendPages(r'{}\{}\{}\{}.pdf'.format(pathcroquis, area, ubigeo, m))
                    pathPDF_croquis.appendPages(r'{}\{}\{}\{}.pdf'.format(pathcroquis, area, ubigeo, m))
            for m in ListadosList:
                if m[0:20] == pdfname:
                    nombre = (m.split("."))[0]
                    pdfDoc.appendPages(r'{}\{}\{}\{}.pdf'.format(pathlistados, area, ubigeo, nombre))
                    pdfDoc_nuevo.appendPages(r'{}\{}\{}\{}.pdf'.format(pathlistados, area, ubigeo, nombre))

            if arcpy.Exists(r'{}\{}\{}\{}-CI.pdf'.format(pathlistados, area, ubigeo, x)):
                pdfDoc.appendPages(r'{}\{}\{}\{}-CI.pdf'.format(pathlistados, area, ubigeo, x))

            #-------------Programacion de rutas-------------#
            for m in progRutasEmp:
                if m[0:20] == pdfname:
                    nombre = (m.split("_"))[0]
                    pdfDoc.appendPages(r'{}\{}\{}\{}_Empad.pdf'.format(pathrutas, area, ubigeo, nombre))
                    pdfDoc_nuevo.appendPages(r'{}\{}\{}\{}_Empad.pdf'.format(pathrutas, area, ubigeo, nombre))
            print pathPDF
            paginas = pdfDoc.pageCount
            actualizaRutaCroquis(ruta_croquis, ruta_web, x, nivel)
            actualizaEmpadronadores(paginas, x[:17], x[17:20]) # FUNCION DE ACTUALIZACION DE BD |||| EMP
            actualizaCodCroquis(pdfname, nivel)
            pdfDoc.saveAndClose()
            pdfDoc_nuevo.saveAndClose()
            pathPDF_croquis.saveAndClose()


def mergeSeccion(FileServer, pathcroquis, pathlistados, pathrutas, ubigeos, fase, conn=conn):
    nivel = 'Seccion'
    for ubigeo in ubigeos:
        actualizaIDEMP(ubigeo)
        actualizaFase(fase, ubigeo, nivel)
        progrutas = '{}\{}\{}'.format(pathrutas, 'Rural', ubigeo)
        progRutasSCR = [x for x in os.listdir(progrutas) if len(x) == 22]
        cursor = conn.cursor()
        # cursor.execute("SELECT IDSCR FROM SEGM_R_SCR WHERE UBIGEO = '{}' AND FASE = '{}'".format(ubigeo, fase)) # FLUJO NORMAL
        cursor.execute("SELECT IDSCR FROM SEGM_R_SCR WHERE UBIGEO = '{}' AND FASE = '{}' AND FLAG_NUEVO = 1".format(ubigeo, fase)) # CON CCPP NUEVOS
        informacion = [x[0] for x in cursor]
        cursor.close()

        # print r'{}\Rural\{}\{}.pdf'.format(pathlistados, ubigeo, x)

        for x in informacion:
            pathPDF = r'{}\Rural\{}\{}\{}.pdf'.format(FileServer, fase, ubigeo, x)
            pathPDF_nuevo = r'{}\Rural\{}-nuevos\{}\{}.pdf'.format(FileServer, fase, ubigeo, x)
            pathPDF_croquis = r'{}\Rural\{}-croquis\{}\{}.pdf'.format(FileServer, fase, ubigeo, x)
            ruta_croquis = pathPDF
            ruta_web = '/cpv2017/croquis-listado/{}/{}/{}/{}.pdf'.format('Rural', fase, ubigeo, x)
            pdfDoc = arcpy.mapping.PDFDocumentCreate(pathPDF)
            pdfDoc_nuevo = arcpy.mapping.PDFDocumentCreate(pathPDF_nuevo)
            pdfDoc_croquis = arcpy.mapping.PDFDocumentCreate(pathPDF_croquis)

            pdfDoc.appendPages(r'{}\Rural\{}\{}.pdf'.format(pathcroquis, ubigeo, x))
            pdfDoc_nuevo.appendPages(r'{}\Rural\{}\{}.pdf'.format(pathcroquis, ubigeo, x))
            pdfDoc_croquis.appendPages(r'{}\Rural\{}\{}.pdf'.format(pathcroquis, ubigeo, x))

            pdfDoc.appendPages(r'{}\Rural\{}\{}.pdf'.format(pathlistados, ubigeo, x))
            pdfDoc_nuevo.appendPages(r'{}\Rural\{}\{}.pdf'.format(pathlistados, ubigeo, x))
            # -------------Programacion de secciones-------------#
            for m in progRutasSCR:
                if m[0:14] == x:
                    nombre = (m.split("_"))[0]
                    pdfDoc.appendPages(r'{}\Rural\{}\{}_SCR.pdf'.format(pathrutas, ubigeo, nombre))
                    pdfDoc_nuevo.appendPages(r'{}\Rural\{}\{}_SCR.pdf'.format(pathrutas, ubigeo, nombre))
            print pathPDF
            paginas = pdfDoc.pageCount
            actualizaRutaCroquis(ruta_croquis, ruta_web, x, nivel)
            actualizaSecciones(paginas, x, conn=conn)    # FUNCION DE ACTUALIZACION DE BD |||| SCR
            actualizaCodCroquis(x, nivel)
            pdfDoc.saveAndClose()
            pdfDoc_nuevo.saveAndClose()
            pdfDoc_croquis.saveAndClose()

def mergeDistritos(FileServer, pathlistados, pathRutas, ubigeos, fase, tipo):
    nivel = 'Distrito'
    for ubigeo in ubigeos:
        if tipo == 1:
            area = 'Rural'
        else:
            area = 'Rural_FEN'
        # actualizaFase(fase, ubigeo, nivel)
        pathPDF = r'{}\{}\{}\{}\{}.pdf'.format(FileServer, area, fase, ubigeo, ubigeo)
        pathPDF_nuevo = r'{}\{}\{}-nuevos\{}\{}.pdf'.format(FileServer, area, fase, ubigeo, ubigeo)
        # ***************************************************************************************************
        ruta_croquis = pathPDF
        ruta_web = '/cpv2017/croquis-listado/{}/{}/{}/{}.pdf'.format('Rural', fase, ubigeo, ubigeo)
        pdfDoc = arcpy.mapping.PDFDocumentCreate(pathPDF)
        pdfDoc_nuevo = arcpy.mapping.PDFDocumentCreate(pathPDF_nuevo)
        print pathPDF
        pdfDoc.appendPages(r'{}\{}\{}\{}.pdf'.format(pathlistados, area, ubigeo, ubigeo))
        pdfDoc_nuevo.appendPages(r'{}\{}\{}\{}.pdf'.format(pathlistados, area, ubigeo, ubigeo))
        # AGREGAR LISTADO DE COMUNIDADES NATIVAS
        if arcpy.Exists(r'{}\{}\{}\{}-CI.pdf'.format(pathlistados, area, ubigeo, ubigeo)):
            pdfDoc.appendPages(r'{}\{}\{}\{}-CI.pdf'.format(pathlistados, area, ubigeo, ubigeo))
            pdfDoc_nuevo.appendPages(r'{}\{}\{}\{}-CI.pdf'.format(pathlistados, area, ubigeo, ubigeo))
        # AGREGAR RESUMEN DE PROGRAMACION DE RUTAS
        pdfDoc.appendPages(r'{}\{}\{}\{}_Resumen.pdf'.format(pathRutas, area, ubigeo, ubigeo))
        pdfDoc_nuevo.appendPages(r'{}\{}\{}\{}_Resumen.pdf'.format(pathRutas, area, ubigeo, ubigeo))

        paginas = pdfDoc.pageCount
        actualizaDistritos(paginas, ubigeo)     # FUNCION DE ACTUALIZACION DE BD |||| UBIGEO
        actualizarModuloSegRural(ubigeo, tipo)
        actualizaRutaCroquis(ruta_croquis, ruta_web, ubigeo, nivel)
        actualizaCodCroquis(ubigeo, nivel)
        pdfDoc.saveAndClose()

def mergeFinal(FileServer, ubigeos, fase, conn=conn):
    area = 'Rural'
    for ubigeo in ubigeos:
        cursor2 = conn.cursor()
        cursor2.execute("SELECT IDSCR FROM SEGM_R_SCR WHERE UBIGEO = '{}' AND FASE = '{}' ORDER BY IDSCR".format(ubigeo, fase))
        informacion2 = [x[0] for x in cursor2]
        cursor2.close()

        # Merge de Secciones
        pathPDF1 = r'{}\{}\{}\{}\{}_seccion.pdf'.format(FileServer, area, fase, ubigeo, ubigeo)
        pdfDoc1 = arcpy.mapping.PDFDocumentCreate(pathPDF1)
        print pathPDF1
        for m in informacion2:
            cursor = conn.cursor()
            cursor.execute("SELECT IDEMP FROM SEGM_R_EMP WHERE UBIGEO = '{}' AND IDSCR = '{}' AND FASE = '{}' ORDER BY IDEMP".format(ubigeo, m, fase))
            informacion1 = [x[0] for x in cursor]
            cursor.close()
            print informacion1
            pdfDoc1.appendPages(r'{}\{}\{}\{}\{}.pdf'.format(FileServer, area, fase, ubigeo, m))
            for y in informacion1:
                pdfDoc1.appendPages(r'{}\{}\{}\{}\{}.pdf'.format(FileServer, area, fase, ubigeo, y))
        pdfDoc1.saveAndClose()

        # Merge de Empadronadores
        pathPDF2 = r'{}\{}\{}\{}\{}_empadronador.pdf'.format(FileServer, area, fase, ubigeo, ubigeo)
        pdfDoc2 = arcpy.mapping.PDFDocumentCreate(pathPDF2)
        print pathPDF2
        for m in informacion2:
            cursor = conn.cursor()
            cursor.execute("SELECT IDEMP FROM SEGM_R_EMP WHERE UBIGEO = '{}' AND IDSCR = '{}' AND FASE = '{}' ORDER BY IDEMP".format(ubigeo, m, fase))
            informacion1 = [x[0] for x in cursor]
            cursor.close()
            for y in informacion1:
                pdfDoc2.appendPages(r'{}\{}\{}\{}\{}.pdf'.format(FileServer, area, fase, ubigeo, y))
        pdfDoc2.saveAndClose()

def mergeFinalProg(FileServer, pathRutas, ubigeos, fase, conn=conn):
    area = 'Rural'
    for ubigeo in ubigeos:
        cursor2 = conn.cursor()
        cursor2.execute("SELECT IDSCR FROM SEGM_R_SCR WHERE UBIGEO = '{}' AND FASE = '{}' ORDER BY IDSCR".format(ubigeo, fase))
        informacion = [x[0] for x in cursor2]
        cursor2.close()

        pathPDF = r'{}\{}\CPV2017-ProgRutas\{}.pdf'.format(FileServer, area, ubigeo)
        pdfDoc = arcpy.mapping.PDFDocumentCreate(pathPDF)

        print pathPDF
        # pdfDoc.appendPages(r'{}\{}\{}\{}_Resumen.pdf'.format(pathRutas, area, ubigeo, ubigeo))

        for m in informacion:
            cursor = conn.cursor()
            cursor.execute("SELECT IDEMP FROM SEGM_R_EMP WHERE UBIGEO = '{}' AND IDSCR = '{}' AND FASE = '{}' ORDER BY IDEMP".format(ubigeo, m, fase))
            informacion1 = [x[0] for x in cursor]
            cursor.close()
            pdfDoc.appendPages(r'{}\{}\{}\{}_SCR.pdf'.format(pathRutas, area, ubigeo, m))
            for y in informacion1:
                pdfDoc.appendPages(r'{}\{}\{}\{}_Empad.pdf'.format(pathRutas, area, ubigeo, y))
        pdfDoc.saveAndClose()

def mergeFinalCI(FileServer, ubigeos, fase):
    area = 'Rural'
    for ubigeo in ubigeos:
        pathPDF = r'{}\{}\{}\Comunidades\{}.pdf'.format(FileServer, area, fase, ubigeo)
        pdfDoc = arcpy.mapping.PDFDocumentCreate(pathPDF)

        print pathPDF
        pathUbigeo = r'D:\SegmentacionRuralV2\Procesamiento\Listados\Rural\{}\{}.pdf'.format(ubigeo,ubigeo)
        pathUbigeoCI = r'D:\SegmentacionRuralV2\Procesamiento\Listados\Rural\{}\{}-CI.pdf'.format(ubigeo,ubigeo)

        pdfDoc.appendPages(pathUbigeo)
        pdfDoc.appendPages(pathUbigeoCI)
        pdfDoc.saveAndClose()

def mergePDF(FileServer, pathlistados, pathcroquis, pathRutas, ubigeos, fase, tipo):
    # mergeEmpadronadores(FileServer, pathlistados, pathcroquis, pathRutas, ubigeos, fase, tipo)
    # if tipo == 1:
    #    mergeSeccion(FileServer, pathcroquis, pathlistados, pathRutas, ubigeos, fase)
    # else:
    #    pass
    #mergeDistritos(FileServer, pathlistados, pathRutas, ubigeos, fase, tipo)
    mergeFinalProg(FileServer, pathRutas, ubigeos, fase)
    # mergeFinalCI(FileServer, ubigeos, fase)