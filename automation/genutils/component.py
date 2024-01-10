from enum import Enum

class LDOComponentType(Enum):
    PASS_TRANSISTOR = "pass-transistor"
    OTA = "ota"
    CCRESISTOR = "ccres"
    BANDGAP =  "bandgap"
    LDO = "ldo"

    def __str__(self):
        return self.value

class LDOComponent:
    def area(self):
        pass
    def width(self):
        pass
    def height(self):
        pass
    def generate(self):
        pass
