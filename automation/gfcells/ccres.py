
import gdsfactory as gf

from enum import Enum
from typing import NamedTuple

class CCResistorCellPortType(Enum):
    TOP = "top"
    BOT = "bot"
    BULK = 3

class CCResistorCellPort(NamedTuple):
    index: gf.typings.Int2
    port_type: CCResistorCellPortType


