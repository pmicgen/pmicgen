from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gfcells import *

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import genutils

from .generic_res import resistor
import gdsfactory as gf
import pandas as pd
import numpy as np
from astar import AStar

from typing import NamedTuple, Union
from dataclasses import dataclass
from collections.abc import Callable
import math
import numbers
import re
import copy
from enum import Enum


@gf.cell
def empty_cell_matrix(
    label_matrix: list[list[str]] = [
        ["A", "B", "A"],
        ["B", "A", "B"],
        ["A", "B", "A"],
        ],
    components: CellTypes | None = None,
    resistor: gf.Component = resistor(),
    spacing_x: list[float] = [],
    spacing_y: list[float] = [],
) -> gf.Component:
    """Generate a non-routed array of cells

    :param label_matrix: A 2D array of string representation of the position of each sub-cell where its value represent its corresponding group
    :type label_matrix: list[list[str]]
    :param components: A dictionary containing all the components available
    :type components: CellTypes
    :param resistor: The sub-cell component
    :type resistor: gf.Component
    :param spacing_x: Starting width spacing for all columns, defaults to []
    :type spacing_x: list[float], optional
    :param spacing_y: Starting height spacing for all rows, defaults to []
    :type spacing_y: list[float], optional
    :return: The generated non-routed matrix component
    :rtype: gf.Component
    """
    matrix: gf.Component = gf.Component()
    rows = len(label_matrix)
    columns = len(label_matrix[0])

    y: float = 0.0
    for i in range(rows):
        x: float = 0.0
        for j in range(columns):
            label: str = label_matrix[i][j]
            resistor_type : gf.Component
            if components:
                resistor_type = components[label].obstacle
            else:
                resistor_type = resistor
            resistor_ref = matrix.add_ref(resistor_type, f"res_{j}_{i}")
            resistor_ref.movex(x + resistor.size[0].item() / 2.0)
            resistor_ref.movey(y + resistor.size[1].item() / 2.0)
            
            x += resistor.size[0].item()
            if j < len(spacing_y) and isinstance(spacing_y[j], numbers.Number):
                y += spacing_y[j]
        if i < len(spacing_x) and isinstance(spacing_x[i], numbers.Number):
            x += spacing_x[i]
        y += resistor.size[1].item()
    return matrix


# TODO: This function should be a method of MatrixCellRouter
def get_cell_types(label_matrix: list[list[str]], resistor: gf.Component) -> CellTypes:
    cell_types: CellTypes = {}
    flat_labels: list[str] = [char for row in label_matrix for char in row]
    unique_labels: list[str] = list(set(flat_labels))
    for label in unique_labels:
        marker_size = (100, 250)
        obstacle: gf.Component = MatrixCellRouter._resistor_obstacle(
            marker_size, resistor=resistor
        ).copy()
        obstacle.add_label(label)
        target: gf.Component = MatrixCellRouter._resistor_target(
            marker_size, resistor=resistor
        ).copy()
        target.add_label(label)
        cell_types[label] = RouteCellVariants(obstacle, target)
    return cell_types


def generic_m1_m2_route_cross_section_spec():
    m1_routing = gf.cross_section.cross_section(
        layer=(41, 0),
        width=10.0,
        port_names=gf.cross_section.port_names_electrical,
        port_types=gf.cross_section.port_types_electrical,
        radius=None,
        min_length=self.minimum_route_ends_spacing,
        gap=5,
    )

    m2_routing = gf.cross_section.cross_section(
        layer=(49, 0),
        width=10.0,
        port_names=gf.cross_section.port_names_electrical,
        port_types=gf.cross_section.port_types_electrical,
        radius=None,
        min_length=self.minimum_route_ends_spacing,
        gap=5,
    )

    multi_cross_section_angle_spec: gf.typings.MultiCrossSectionAngleSpec = [
        (m1_routing, (0, 180)),
        (m2_routing, (90, 270)),
    ]
    return multi_cross_section_angle_spec



@gf.cell
def common_centroid_resistor(
    matrix_cell_router: MatrixCellRouter,
    routing_fn: Callable[MatrixCellRouter, None],
    route_width: float = 10.0,
    cell_route_margin: float = 5.0,
) -> gf.Component:
    routing_fn(matrix_cell_router)
    return matrix_cell_router.routing_matrix


def generic_common_centroid_resistor(
    element_count: int = 15, ratio: float = 0.4, row_number: int = 5, routing_fn = routing_a
) -> gf.Component:
    genutils.CCResistor(tech=genutils.TechManager(genutils.PDK(genutils.PDK.SKY130A)))
    ccm = genutils.ccres.CommonCentroidMatrix(
        element_count=element_count, ratio=ratio, row_number=row_number
    )
    label_matrix: list[list[str]] = ccm.cells_repr()
    routing_matrix: gf.Component = gf.Component("ccres")
    non_routed_matrix = empty_cell_matrix(
        label_matrix=label_matrix,
        components=get_cell_types(label_matrix, resistor=resistor()),
        resistor=resistor(),
    )
    matrix: gf.Component = common_centroid_resistor(
        MatrixCellRouter(
            non_routed_matrix=non_routed_matrix,
            routing_matrix=routing_matrix,
            label_matrix=label_matrix,
            resistor=resistor(),
            cell_to_pad_enclosure_height=resistor().to_dict()["settings"]["enclosure"][
                1
            ],
        ),
        routing_fn=routing_fn,
    )
    return matrix
