from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gfcells import *

import pandas as pd

from .typings import MatrixDirection2D, CCResistorCellPort, CCResistorCellPortType
import gdsfactory as gf


def routing_a(router: MatrixCellRouter) -> None:
    """Simple routing function for demonstration purposes

    :param matrix_cell_router: The cell router
    :type matrix_cell_router: MatrixCellRouter
    """
    router.add_route_line(index=0, direction=MatrixDirection2D.Column)
    #router.add_route_line(index=0, direction=MatrixDirection2D.Row)
    print(pd.DataFrame(router.routing_matrix_arr))

    router.connect_cells(
        cell_orig=CCResistorCellPort((0, 0), CCResistorCellPortType.TOP),
        cell_dest=CCResistorCellPort((1, 1), CCResistorCellPortType.BOT),
    )
