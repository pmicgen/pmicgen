from .component import *

import gdsfactory as gf
import sky130

import subprocess
import os

class LDO(LDOComponent):

    def __init__(self, tech: TechManager):
        super().__init__(tech)

    def generate(self):
        bgr = gf.read.import_gds("build/sky130_bgr/gds/bgr.gds")
        erroramp = gf.read.import_gds("build/sky130_erroramp/gds/erroramp.gds").flatten_offgrid_references()
        pmosw = gf.read.import_gds("build/sky130_pmosw/gds/pmosw.gds")

        ldo = gf.pack([bgr, erroramp, pmosw])
        ldo[0].flatten_offgrid_references().write_gds("build/sky130_ldo/gds/ldo.gds")

        proc = subprocess.Popen(
            [
                "ngspice",
                "-b",
                "-a",
                "-o",
                "/content/pmicgen/build/sky130_erroramp/erroramp.report",
                "-r",
                "/content/pmicgen/build/sky130_erroramp/ota.raw",
                "/root/.xschem/simulations/tb_ota.spice",
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd="xschem",
            env=os.environ,
            universal_newlines=True,
        )
        proc.communicate()
