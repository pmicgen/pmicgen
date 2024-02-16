from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gfcells import *

from .typings import (
    MatrixDirection2D,
    CellCoord,
    RoutingCoord,
    LayoutCoord,
    RoutingMapCharRef,
)
from .cell import Cell

from dataclasses import dataclass
import math

from astar import AStar
import pandas as pd

@dataclass
class Connection:
    position: RoutingCoord
    previous: MatrixElement
    next: MatrixElement

    # TODO: Try to change the gf layer for the parent layer
    # This is problematic for now, because this generates a circular
    # reference that doesn't allow serialization from gf.cell decorator
    z: int

    @property
    def i(self) -> int:
        return self.position[0]

    @property
    def j(self) -> int:
        return self.position[1]

    def __str__(self) -> str:
        if self.previous == None and self.next == None:
            return RoutingMapCharRef.ROUTE_AVAILABLE.value
        if not self.previous and self.next:
            # if self.i == self.next.i and self.j == self.next.j
            if self.z < self.next.z:
                return RoutingMapCharRef.VIA_UP.value
            elif self.z > self.next.z:
                return RoutingMapCharRef.VIA_DOWN.value
            else:
                return RoutingMapCharRef.VIA_DOWN.value
            # else:
            #    return RoutingMapCharRef.VIA_DOWN.value
        if self.previous and not self.next:
            # if self.i == self.previous.i and self.j == self.previous.j:
            if self.z < self.previous.z:
                return RoutingMapCharRef.VIA_UP.value
            elif self.z > self.previous.z:
                return RoutingMapCharRef.VIA_DOWN.value
            else:
                return RoutingMapCharRef.VIA_DOWN.value
        if self.previous and self.next:
            if self.i == self.previous.i:
                return RoutingMapCharRef.ROUTE_VERTICAL.value
            if self.j == self.previous.j:
                return RoutingMapCharRef.ROUTE_HORIZONTAL.value
        return "#"

