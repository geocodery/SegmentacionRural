import arcpy
import os
from Generales import settings


conn = settings.conectionDB_pymmsql()


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
    cursor.execute("UPDATE TB_DISTRITO SET CANT_PAG_R = {} WHERE UBIGEO = '{}'".format(paginas, ubigeo))
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



def mergeEmpadronadores(FileServer, pathlistados, pathcroquis, ubigeos, tipo):

    if tipo == 1:
        area = 'Rural'
    else:
        area = 'Rural_FEN'

    for ubigeo in ubigeos:

        listados = '{}\{}\{}'.format(pathlistados, area, ubigeo)
        croquis = '{}\{}\{}'.format(pathcroquis, area, ubigeo)
        namePDF = list(set([x[0:18] for x in os.listdir(listados) if len(x) >= 24]))
        ListadosList = [x for x in os.listdir(listados) if len(x) >= 24]
        croquisList = [x[0:20] for x in os.listdir(croquis) if len(x) >= 24]
        # progRutasEmp = [x for x in os.listdir(listados) if len(x) >= 24]
        # progRutasSCR = [x for x in os.listdir(listados) if len(x) >= 24]

        for x in namePDF:
            pdfname = x
            pathPDF = r'{}\{}\{}\{}.pdf'.format(FileServer, area, ubigeo, pdfname)
            pdfDoc = arcpy.mapping.PDFDocumentCreate(pathPDF)

            for m in croquisList:
                if m[0:18] == pdfname:
                    print r'{}\{}\{}\{}.pdf'.format(pathcroquis, area, ubigeo, m)
                    pdfDoc.appendPages(r'{}\{}\{}\{}.pdf'.format(pathcroquis, area, ubigeo, m))
            for m in ListadosList:
                if m[0:18] == pdfname:
                    nombre = (m.split("."))[0]
                    pdfDoc.appendPages(r'{}\{}\{}\{}.pdf'.format(pathlistados, area, ubigeo, nombre))
            if arcpy.Exists(r'{}\{}\{}\{}-CI.pdf'.format(pathlistados, area, ubigeo, x)):
                pdfDoc.appendPages(r'{}\{}\{}\{}-CI.pdf'.format(pathlistados, area, ubigeo, x))


            paginas = pdfDoc.pageCount
            actualizaEmpadronadores(paginas, x[0], x[1])    # FUNCION DE ACTUALIZACION DE BD |||| EMP
            pdfDoc.saveAndClose()


def mergeSeccion(FileServer, pathcroquis, pathlistados, ubigeos, conn=conn):
    for ubigeo in ubigeos:
        print ubigeo
        cursor = conn.cursor()
        cursor.execute("SELECT IDSCR FROM SEGM_R_SCR WHERE UBIGEO = '{}'".format(ubigeo))
        informacion = [x[0] for x in cursor]
        cursor.close()
        for x in informacion:
            pathPDF = r'{}\Rural\{}\{}.pdf'.format(FileServer, ubigeo, x)
            pdfDoc = arcpy.mapping.PDFDocumentCreate(pathPDF)
            pdfDoc.appendPages(r'{}\Rural\{}\{}.pdf'.format(pathcroquis, ubigeo, x))
            print r'{}\Rural\{}\{}.pdf'.format(pathlistados, ubigeo, x)
            pdfDoc.appendPages(r'{}\Rural\{}\{}.pdf'.format(pathlistados, ubigeo, x))
            paginas = pdfDoc.pageCount
            actualizaSecciones(paginas, x, conn=conn)    # FUNCION DE ACTUALIZACION DE BD |||| SCR
            pdfDoc.saveAndClose()


def mergeDistritos(FileServer, pathlistados, ubigeos, tipo):
    for ubigeo in ubigeos:
        if tipo == 1:
            area = 'Rural'
        else:
            area = 'Rural_FEN'
        pathPDF = r'{}\{}\{}\{}.pdf'.format(FileServer, area, ubigeo, ubigeo)
        pdfDoc = arcpy.mapping.PDFDocumentCreate(pathPDF)
        print r'{}\{}\{}\{}.pdf'.format(pathlistados, area, ubigeo, ubigeo)
        pdfDoc.appendPages(r'{}\{}\{}\{}.pdf'.format(pathlistados, area, ubigeo, ubigeo))
        paginas = pdfDoc.pageCount
        actualizaDistritos(paginas, ubigeo)     # FUNCION DE ACTUALIZACION DE BD |||| UBIGEO
        actualizarModuloSegRural(ubigeo, tipo)
        pdfDoc.saveAndClose()


def mergePDF(FileServer, pathlistados, pathcroquis, ubigeos, tipo):
    mergeEmpadronadores(FileServer, pathlistados, pathcroquis, ubigeos, tipo)
    if tipo == 1:
        mergeSeccion(FileServer, pathcroquis, pathlistados, ubigeos)
    else:
        pass
    mergeDistritos(FileServer, pathlistados, ubigeos, tipo)