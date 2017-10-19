from Generales import settings

conn = settings.conectionDB_pymmsql()

def borrarEMPant(ubigeo, conn=conn):
    cursor1 = conn.cursor()
    cursor1.execute("DELETE FROM CALIDAD_R_EMP WHERE UBIGEO = '{}'     DELETE FROM CALIDAD_R_SCR WHERE UBIGEO = '{}'     DELETE FROM  CALIDAD_R_LEGAJO_EMP WHERE UBIGEO = '{}'".format(ubigeo, ubigeo, ubigeo))
    conn.commit()
    cursor1.close()

def extraerEmp(ubigeo, conn=conn):
    cursor = conn.cursor()
    cursor.execute("SELECT IDEMP, UBIGEO, EMP, SCR FROM SEGM_R_EMP WHERE UBIGEO = '{}' AND FASE = 'CPV2017'".format(ubigeo))
    informacion = [[x[0], x[1], x[2], x[3]] for x in cursor]
    cursor.close()
    return informacion

def extraerScr(ubigeo, conn=conn):
    cursor = conn.cursor()
    cursor.execute("SELECT IDSCR, UBIGEO, SCR FROM SEGM_R_SCR WHERE UBIGEO = '{}'".format(ubigeo))
    informacion = [[x[0], x[1], x[2]] for x in cursor]
    cursor.close()
    return informacion

def consultaScr(ubigeo, conn=conn):
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT FLAG_CALID_ESTADO FROM CALIDAD_R_SCR WHERE FLAG_CALID_ESTADO IN (1,2,9) AND UBIGEO = '{}'".format(ubigeo))
    informacion = [x[0] for x in cursor]
    cursor.close()
    return informacion

def subirValores(idemp, idscr, estado,conn=conn):
    cursor = conn.cursor()
    for x in idemp:
        cursor.execute("INSERT INTO CALIDAD_R_EMP (ID, UBIGEO, EMP, SCR, IND1, IND2, IND3, IND4, FLAG_CALIDAD)   VALUES ('{}', '{}', '{}', '{}', 0,0,0,0,0)     INSERT INTO CALIDAD_R_LEGAJO_EMP (ID, UBIGEO, EMP, SCR, IND1, IND2, IND3, FLAG_CALID_LEG, FECH_REV, NUM_REV) VALUES ('{}', '{}', '{}', '{}', 0,0,0,0,0,0)".format(x[0], x[1], x[2], x[3], x[0], x[1], x[2], x[3]))
        conn.commit()
    for y in idscr:
        cursor.execute("INSERT INTO CALIDAD_R_SCR (ID, UBIGEO, SCR, FLAG_CALID_ESTADO, NUM_REV, FECH_REV, FLAG_CALID_ESTADO_LEG, FECH_REV_LEG, NUM_REV_LEG) VALUES ('{}', '{}', '{}', '{}', 0, 0, '{}',0,0)".format(y[0], y[1], y[2], estado, estado))
        conn.commit()
    cursor.close()


def actualizarCalidad(ubigeos):
    for ubigeo in ubigeos:
        idscrCon = consultaScr(ubigeo)
        if len(idscrCon) == 0:
            estado = 0
        else:
            estado = 9
        borrarEMPant(ubigeo)
        idemp = extraerEmp(ubigeo)
        idscr = extraerScr(ubigeo)
        subirValores(idemp, idscr, estado)