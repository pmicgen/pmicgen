from .component import *

import align
import os


class OTA(LDOComponent):

    schematic_path: os.PathLike

    def __init__(self, tech: TechManager, netlist: os.PathLike):
        super().__init__(tech)
        self.netlist = netlist

    def generate(self):
        align.schematic2layout(self.netlist.resolve(), "thirdparty/align-sky130/SKY130_PDK")
        
