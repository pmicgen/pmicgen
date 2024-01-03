import pya

from .ccres import CCResistorPCell

class LDOPCellLib(pya.Library):
    def __init__(self):
        self.description = "description"
        self.layout().register_pcell("Common Centroid Resistance", CCResistorPCell())
        self.register("LDO PCell Library")