from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gfcells import *

import gdsfactory as gf

from enum import Enum
from typing import NamedTuple, Union


Float2 = tuple[float, float]
Int2 = tuple[int, int]


CellCoord = Int2
RoutingCoord = Int2
LayoutCoord = Float2

""" Type alias for each element in the common centroid matrix """
MatrixElement = Union["Connection", "Cell", None]


class MatrixDirection2D(Enum):
    Column = 0
    Row = 1
    
    def opposite(direction: MatrixDirection2D) -> MatrixDirection2D:
        if MatrixDirection2D == Column:
            return Row
        elif MatrixDirection2D == Row:
            return Column
        else:
            raise ValueError()


class CCResistorCellPortType(Enum):
    TOP = "top"
    BOT = "bot"
    BULK = 3


class CCResistorCellPort(NamedTuple):
    index: CellCoord
    port_type: CCResistorCellPortType


class RoutingMapCharRef(Enum):
    ROUTE_AVAILABLE = " "
    ROUTE_HORIZONTAL = "―"
    ROUTE_VERTICAL = "|"
    VIA_UP = "↑"
    VIA_DOWN = "↓"
    ERROR = "!"


ConnectionMap = list[list["Connection"]]
