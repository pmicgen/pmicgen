from .component import *

import gdsfactory as gf
import sky130

class LDO(LDOComponent):

    def __init__(self, tech: TechManager):
        super().__init__(tech)

    def generate(self):
        bgr = gf.read.import_gds("build/sky130_bgr/gds/bgr.gds")
        erroramp = gf.read.import_gds("build/sky130_erroramp/gds/erroramp.gds").flatten_offgrid_references()
        pmosw = gf.read.import_gds("build/sky130_pmosw/gds/pmosw.gds")

        ldo = gf.pack([bgr, erroramp, pmosw])
        ldo[0].flatten_offgrid_references().write_gds("build/sky130_ldo/gds/ldo.gds")

