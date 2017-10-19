import arcpy
import pythonaddins

class sumaviv(object):
    """Implementation for PruebaSuma_addin.sumaviv (Tool)"""
    def __init__(self):
        self.enabled = True
        self.cursor = 3
        self.shape = "Line" # Can set to "Line", "Circle" or "Rectangle" for interactive shape drawing and to activate the onLine/Polygon/Circle event sinks.
    def onMouseDown(self, x, y, button, shift):
        pass
    def onMouseDownMap(self, x, y, button, shift):
        pass
    def onMouseUp(self, x, y, button, shift):
        pass
    def onMouseUpMap(self, x, y, button, shift):
        pass
    def onMouseMove(self, x, y, button, shift):
        pass
    def onMouseMoveMap(self, x, y, button, shift):
        pass
    def onDblClick(self):
        pass
    def onKeyDown(self, keycode, shift):
        pass
    def onKeyUp(self, keycode, shift):
        pass
    def deactivate(self):
        pass
    def onCircle(self, circle_geometry):
        pass
    def onLine(self, line_geometry):
        array = arcpy.Array()
        part = line_geometry.getPart(0)
        for pt in part:
            array.add(pt)
        array.add(line_geometry.firstPoint)
        polygon = arcpy.Polygon(array)
        if arcpy.Exists("in_memory/polygons"):
            arcpy.Delete_management("in_memory/polygons")
        arcpy.RefreshActiveView()
        arcpy.CopyFeatures_management(polygon, "in_memory/polygons")
        mxd = arcpy.mapping.MapDocument("CURRENT")
        ccpp = [x for x in arcpy.mapping.ListLayers(mxd) if x.name == 'CCPP'][0]
        poligono = [x for x in arcpy.mapping.ListLayers(mxd) if x.name == 'polygons'][0]
        arcpy.SelectLayerByLocation_management(ccpp, "INTERSECT", poligono, "#", "NEW_SELECTION")
        suma = sum([x[0] for x in arcpy.da.SearchCursor(ccpp, ["VIV_CCPP"])])
        arcpy.RefreshActiveView()
        pythonaddins.MessageBox("Viviendas Totales: {}".format(suma), "INEI", 0)
        arcpy.SelectLayerByAttribute_management(ccpp, "CLEAR_SELECTION")
        arcpy.RefreshActiveView()


    def onRectangle(self, rectangle_geometry):
        pass


