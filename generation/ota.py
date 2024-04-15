from .component import *

import align
import os

import subprocess

class OTA(LDOComponent):

    schematic_path: os.PathLike

    def __init__(self, tech: TechManager, netlist: os.PathLike):
        super().__init__(tech)
        self.netlist = netlist

    def generate(self):
        align.schematic2layout(self.netlist.resolve(), "thirdparty/align-sky130/SKY130_PDK")

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
        
