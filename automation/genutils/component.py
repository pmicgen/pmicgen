from enum import Enum
from pathlib import Path
from dataclasses import dataclass

class PDK(Enum):
    SKY130A = "sky130A"
    GF180MCUD = "gf180mcuD"

@dataclass
class TechManager():
    pdk: PDK

    def pdk_root_path(self):
        return f"{str(Path.home())}/.volare/{self.pdk.value}"
    
    def magicrc_path(self):
        return f"{self.pdk_root_path()}/libs.tech/magic/{self.pdk.value}.magicrc"

class LDOComponentType(Enum):
    PASS_TRANSISTOR = "pass-transistor"
    OTA = "ota"
    CCRESISTOR = "ccres"
    BANDGAP =  "bandgap"
    LDO = "ldo"

    def __str__(self):
        return self.value

@dataclass
class LDOComponent:
    tech: TechManager

    def area(self):
        pass
    def width(self):
        pass
    def height(self):
        pass
    def generate(self):
        pass
