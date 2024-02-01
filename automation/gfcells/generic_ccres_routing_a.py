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
    for i in range(router.number_of_cell_columns-1):
        router.add_route_line(index=i, direction=MatrixDirection2D.Column)
        router.add_route_line(index=i, direction=MatrixDirection2D.Column)
        router.add_route_line(index=i, direction=MatrixDirection2D.Column)
        
    for j in range(router.number_of_cell_rows-1):    
        router.add_route_line(index=j, direction=MatrixDirection2D.Row)
        router.add_route_line(index=j, direction=MatrixDirection2D.Row)
        router.add_route_line(index=j, direction=MatrixDirection2D.Row)
    
    """
    router.connect_cells(
        cell_orig=CCResistorCellPort((0, 0), CCResistorCellPortType.BOT),
        cell_dest=CCResistorCellPort((1, 3), CCResistorCellPortType.TOP),
    )
    router.connect_cells(
        cell_orig=CCResistorCellPort((0, 0), CCResistorCellPortType.TOP),
        cell_dest=CCResistorCellPort((1, 3), CCResistorCellPortType.BOT),
    )
    router.connect_cells(
        cell_orig=CCResistorCellPort((0, 1), CCResistorCellPortType.BOT),
        cell_dest=CCResistorCellPort((2, 3), CCResistorCellPortType.TOP),
    )
    """
    connect_cells_in_series(router)

    
    
def connect_cells_in_series(router):
    for row in range(router.number_of_cell_rows):
        for col in range(router.number_of_cell_columns):
            current_label = router.label_matrix[row][col]

            if current_label == 'A':
                # Find the nearest 'A' cell and connect them in series
                nearest_a_coordinate = find_nearest_cell(router, 'A', (col, row))
                if nearest_a_coordinate:
                    #print(col, row)
                    router.connect_cells(
                        cell_orig=CCResistorCellPort((col, row), CCResistorCellPortType.BOT),
                        cell_dest=CCResistorCellPort(nearest_a_coordinate, CCResistorCellPortType.TOP),
                    )

            elif current_label == 'B':
                # Find the nearest 'B' cell and connect them
                nearest_b_coordinate = find_nearest_cell(router, 'B', (col, row))
                if nearest_b_coordinate:
                    #print(col, row)
                    router.connect_cells(
                        cell_orig=CCResistorCellPort((col, row), CCResistorCellPortType.BOT),
                        cell_dest=CCResistorCellPort(nearest_b_coordinate, CCResistorCellPortType.TOP),
                    )

def find_nearest_cell(router, label, current_coordinate):
    min_distance = float('inf')
    nearest_coordinate = None

    for row in range(router.number_of_cell_rows):
        for col in range(router.number_of_cell_columns):
            if router.label_matrix[row][col] == label and (col, row) != current_coordinate:
                distance = abs(col - current_coordinate[0]) + abs(row - current_coordinate[1])
                if distance < min_distance:
                    min_distance = distance
                    nearest_coordinate = (col, row)

    return nearest_coordinate
