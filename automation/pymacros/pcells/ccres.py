import pya

class CCResistorPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(CCResistorPCell, self).__init__()
        self.param("l", self.TypeDouble, "length", default=1, unit="um")
        self.param("w", self.TypeDouble, "width", default=1, unit="um")
    
    def produce_impl(self):
        pass