import arcpy
from Generales import settings

ubigeos = []

conn = settings.conectionDB_arcpy()

def extraerData(conn=conn):
    arcpy.MakeQueryLayerManagement(conn, "SELECT*FROM ")

