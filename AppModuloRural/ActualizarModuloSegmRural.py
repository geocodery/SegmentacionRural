from Generales import settings


conn = settings.conectionDB_pymmsql()

def ubigeosTBModuloSegmRural(conn=conn):
    cursor = conn.cursor()
    cursor.execute("EXEC USP_ACTUALIZA_MODULO_R")
    ubigeos = [[x[0], x[1], x[2], x[3]] for x in cursor]
    cursor.close()
    return ubigeos

def actualizaTBModuloSegmRural(ubigeos, conn=conn):
    cursor = conn.cursor()
    cursor.execute("SELECT UBIGEO FROM TB_MODULO_ASIGN_R")
    ubigeosModulo = [x[0] for x in cursor]
    cursor.close()
    for ubigeo in ubigeos:
        if ubigeo[3] in ubigeosModulo:
            # Actualizar
            print "No entra: {}".format(ubigeo[3])
        else:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO TB_MODULO_ASIGN_R (CCDD, CCPP, CCDI, UBIGEO, SEGMENTISTA, ESTADO) VALUES ('{}', '{}', '{}', '{}', 8719, 2)".format(ubigeo[0], ubigeo[1], ubigeo[2], ubigeo[3]))
            print "Inserta: {}".format(ubigeo[3])
            conn.commit()
            cursor.close()

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

# FUNCION MAIN

def actualizar():
    ubigeos = ubigeosTBModuloSegmRural()
    actualizaTBModuloSegmRural(ubigeos)


#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
