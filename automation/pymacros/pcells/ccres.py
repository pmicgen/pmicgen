import pya
import math

class CCResistorPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(CCResistorPCell, self).__init__()
        self.param("x", self.TypeDouble, "Position X", default = 0)
        self.param("y", self.TypeDouble, "Position Y", default = 0)
        self.param("w", self.TypeDouble, "Width", default = 10)
        self.param("h", self.TypeDouble, "Height", default = 5)
        self.param("l", self.TypeLayer, "Layer", default = pya.LayerInfo(66, 13))

    def display_text_impl(self):
        return "CC Resistor"

    def coerce_parameters_impl(self):    
        pass

    def can_create_from_shape_impl(self):
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()

    def parameters_from_shape_impl(self):
        self.w = self.shape.bbox().width()
        self.h = self.shape.bbox().height()
        self.l = self.layout.get_info(self.layer)

    def transformation_from_shape_impl(self):
        return pya.Trans(self.shape.bbox().center())

    def produce_impl(self):
        rect = pya.DBox(self.w, self.h)
        rect = rect.transformed(pya.DCplxTrans(1.0, 0.0, False, self.x, self.y))
        self.cell.shapes(self.l_layer).insert(rect)