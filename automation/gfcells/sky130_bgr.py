from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gfcells import *

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import genutils

import gdsfactory as gf

@gf.cell
def sky130_bgr() -> gf.Component:
    tech = genutils.TechManager(genutils.PDK.SKY130A)
    bgrgen = genutils.BGR(tech)
    bgrgen.generate()
    bgrcomp : gf.Component = gf.read.import_gds("build/sky130_bgr/gds/bgr.gds")
    return bgrcomp