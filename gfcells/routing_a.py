from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gfcells import *

import pandas as pd

from .typings import MatrixDirection2D, CCResistorCellPort, CCResistorCellPortType
import gdsfactory as gf

import math


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
    
    connect_cells_in_series(router)


def connect_cells_in_series(router : MatrixCellRouter) -> None:
    """Routing function that connect cells in series starting from the cell at (0, 0)
    jumping each time to the nearest cell (in cell units) that has the same
    label as the one before. This process is repeated to each label until
    all the cells are connected.
    """
    # List of labels connected
    labels_connected : list[str] = []
    # List of coordinates traversed in the current iteration
    traversed_coords = [(0, 0)]
    # List of coordinates available to traverse in the current iteration
    matrix = [[(j, i) for j in range(router.number_of_cell_columns)] for i in range(router.number_of_cell_rows)]
    flat_matrix = [coord for row in matrix for coord in row]
    available_coords = flat_matrix
    # List of coordinates which their labels have not yet been traversed
    leftovers_coords = []
    # Current coordinate being processed
    current_coordinate = (0, 0)
    x, y = current_coordinate 

    # Loop if its the first iteration (no labels connected)
    # or if there leftovers coords not connected
    while not labels_connected or leftovers_coords:
        if leftovers_coords:
            untraversed_coords = leftovers_coords
            available_coords = leftovers_coords
            leftovers_coords = []
            
            current_coordinate = untraversed_coords[0]
            x, y = current_coordinate
            
        current_label = router.label_matrix[y][x]
        current_port_type = CCResistorCellPortType.TOP
        nearest_coordinate = nearest_untraversed_coordinate(available_coords, traversed_coords, (x, y))
        while nearest_coordinate:
            nearest_x, nearest_y = nearest_coordinate
            nearest_label = router.label_matrix[nearest_y][nearest_x]
            if current_label == nearest_label:
                if current_coordinate != nearest_coordinate:
                    if y < nearest_y:
                        current_port_type = CCResistorCellPortType.TOP
                        router.connect_cells(
                            cell_orig=CCResistorCellPort(current_coordinate, current_port_type),
                            cell_dest=CCResistorCellPort(nearest_coordinate, CCResistorCellPortType.BOT),
                        )
                    elif y > nearest_y:
                        current_port_type = CCResistorCellPortType.BOT
                        router.connect_cells(
                            cell_orig=CCResistorCellPort(current_coordinate, current_port_type),
                            cell_dest=CCResistorCellPort(nearest_coordinate, CCResistorCellPortType.TOP),
                        )
                    else:
                        router.connect_cells(
                            cell_orig=CCResistorCellPort(current_coordinate, current_port_type),
                            cell_dest=CCResistorCellPort(nearest_coordinate, current_port_type),
                        )
                current_coordinate = nearest_coordinate
                x, y = current_coordinate
            else:
                leftovers_coords.append(nearest_coordinate)
            traversed_coords.append(nearest_coordinate)
            nearest_coordinate = nearest_untraversed_coordinate(available_coords, traversed_coords, (x, y))
 
        traversed_coords = []
        labels_connected.append(current_label)

def distance(coord1, coord2):
    x1, y1 = coord1
    x2, y2 = coord2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def nearest_untraversed_coordinate(available_coordinates, traversed_coordinates, origin):
    min_distance = float('inf')
    nearest_coordinate = None

    for coord in available_coordinates:
        if coord not in traversed_coordinates:
            dist = distance(origin, coord)
            if dist < min_distance:
                min_distance = dist
                nearest_coordinate = coord

    return nearest_coordinate