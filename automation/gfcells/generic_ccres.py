from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gfcells import *

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import genutils

from .generic_res import resistor
from .generic_ccres_routing_a import routing_a
from .typings import (
    MatrixDirection2D,
    CCResistorCellPort,
    CCResistorCellPortType,
    CellCoord,
    RoutingCoord,
    LayoutCoord,
    RoutingMapCharRef,
)
from .route_solver import Connection, RouteSolver
from .cell import Cell
from .connection import Connection

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


@dataclass
class RouteCellVariants:
    obstacle: gf.Component
    target: gf.Component


CellTypes = dict[str, RouteCellVariants]


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


@dataclass
class Layer:
    rows: list[list[MatrixElement]]
    layer: gf.typings.Layer

    def __str__(self) -> str:
        def format_char(element):
            if element is not None:
                return str(element)
            else:
                return RoutingMapCharRef.ROUTE_AVAILABLE.value

        formatted_rows = [
            "".join([format_char(element) for element in row]) for row in self.rows
        ]

        return "\n".join(formatted_rows)

    @property
    def number_of_rows(self):
        return len(self.rows)

    @property
    def number_of_columns(self):
        return len(self.rows[0])

    def add_routing_line(
        self, index: int, direction: MatrixDirection2D = MatrixDirection2D.Column
    ) -> None:
        """Add a route line to the routing matrix array

        :param index: The index of the row or column before the spacing
        :type index: int
        :param direction: Enum for selecting column or row insertion
        :type direction: MatrixDirection2D, optional
        """
        arr = np.array(self.rows)
        if direction == MatrixDirection2D.Column:
            new_line = [None] * arr.shape[0]
            new_arr = np.insert(arr, index + 1, new_line, axis=1)
        elif direction == MatrixDirection2D.Row:
            new_line = [None] * arr.shape[1]
            new_arr = np.insert(arr, index + 1, new_line, axis=0)
        else:
            return ValueError()
        self.rows = new_arr.tolist()


@dataclass
class Port:
    name: str
    position: LayoutCoord

@dataclass
class MatrixCellRouter:
    """Helper Class for routing a matrix of cells during its construction"""

    # TODO: parse labels from component
    def __init__(
        self,
        non_routed_matrix: gf.Component,
        routing_matrix: gf.Component,
        label_matrix: list[list[str]],
        resistor=resistor(),
        route_width=10,
        cell_to_pad_enclosure_height=20,
        cell_to_route_spacing=20,
        horizontal_layer: gf.typings.Layer = "M1",
        vertical_layer: gf.typings.Layer = "M2",
        cell_port_map: list[list[Port | None]] = [["T"], ["B"]],
        
    ) -> None:
        self.label_matrix = label_matrix
        self.resistor = resistor
        self.components = get_cell_types(label_matrix=label_matrix, resistor=resistor)
        self.non_routed_matrix = non_routed_matrix
        self._route_width = route_width
        self._cell_to_pad_enclosure_height = cell_to_pad_enclosure_height
        self._cell_to_route_spacing = cell_to_route_spacing
        self._horizontal_layer = horizontal_layer
        self._vertical_layer = vertical_layer
        self._cell_port_map = cell_port_map
        self.routing_matrix = non_routed_matrix.copy("routing_matrix")

        horizontal_layer: Layer = self._init_routing_map()
        vertical_layer: Layer = copy.deepcopy(horizontal_layer)
        vertical_layer.layer = (1, 0)
        self._routing_map = [horizontal_layer, vertical_layer]

    non_routed_matrix: gf.Component
    routing_matrix: gf.Component
    resistor: gf.Component
    components: CellTypes
    label_matrix: list[list[str]]

    _target_orig: gf.typings.Int2 | None = None
    _target_dest: gf.typings.Int2 | None = None

    def component_at(self, index: gf.typings.Int2) -> gf.Component:
        label = self.label_matrix[index[1]][index[0]]
        if index == self.target_orig or index == self.target_dest:
            return self.components[label].target
        else:
            return self.components[label].obstacle

    @property
    def number_of_cell_columns(self):
        return len(self.label_matrix[0])

    @property
    def number_of_cell_rows(self):
        return len(self.label_matrix)

    @property
    def number_of_route_subcells_columns(self) -> int:
        return len(self._routing_map[0].rows[0])

    @property
    def number_of_route_subcells_rows(self) -> int:
        return len(self._routing_map[0].rows)

    @property
    def target_orig(self) -> gf.typings.Int2:
        return self._target_orig

    @target_orig.setter
    def target_orig(self, index_position: gf.typings.Int2) -> None:
        if self.target_orig:
            self._switch_cell_marking(self.routing_matrix, self.target_orig)
        self._target_orig = index_position
        self._switch_cell_marking(self.routing_matrix, self.target_orig)

    @property
    def target_dest(self) -> gf.typings.Int2:
        return self._target_dest

    @target_dest.setter
    def target_dest(self, index_position: gf.typings.Int2) -> None:
        if self._target_dest:
            self._switch_cell_marking(self.routing_matrix, self._target_dest)
        self._target_dest = index_position
        self._switch_cell_marking(self.routing_matrix, self._target_dest)

    @property
    def route_width(self) -> float:
        return self._route_width

    @property
    def cell_to_pad_enclosure_height(self) -> float:
        return self._cell_to_pad_enclosure_height

    @property
    def cell_to_route_spacing(self) -> float:
        return self._cell_to_route_spacing

    @property
    def routing_spacing_line_width(self) -> float:
        """Width of the spacing added to fit a straight route including margins

        :return: Width in um
        :rtype: float
        """
        return 2 * self.cell_to_route_spacing + self.route_width

    @property
    def minimum_route_ends_spacing(self) -> float:
        """Minimum spacing between the port of the cell and a route bend

        :return: Size in um
        :rtype: float
        """
        return self.cell_to_pad_enclosure_height + self.cell_to_route_spacing

    @property
    def horizontal_layer(self) -> gf.typings.Layer:
        return self._horizontal_layer

    @horizontal_layer.setter
    def horizontal_layer(self, horizontal_layer: gf.typings.Layer) -> None:
        self._horizontal_layer = horizontal_layer

    @property
    def vertical_layer(self) -> gf.typings.Layer:
        return self._vertical_layer

    @vertical_layer.setter
    def vertical_layer(self, vertical_layer: gf.typings.Layer) -> None:
        self._vertical_layer = vertical_layer

    @property
    def multi_cross_section_angle_spec(self) -> gf.typings.MultiCrossSectionAngleSpec:
        horizontal_cross_section_spec: gf.typings.CrossSection = (
            gf.cross_section.cross_section(
                layer=self.horizontal_layer,
                width=self.route_width,
                port_names=gf.cross_section.port_names_electrical,
                port_types=gf.cross_section.port_types_electrical,
                radius=None,
                min_length=self.minimum_route_ends_spacing,
                gap=5,  # TODO: No idea what this is
            )
        )

        vertical_cross_section_spec: gf.typings.CrossSection = (
            gf.cross_section.cross_section(
                layer=self.vertical_layer,
                width=self.route_width,
                port_names=gf.cross_section.port_names_electrical,
                port_types=gf.cross_section.port_types_electrical,
                radius=None,
                min_length=self.minimum_route_ends_spacing,
                gap=5,
            )
        )

        return [
            (horizontal_cross_section_spec, (0, 180)),
            (vertical_cross_section_spec, (90, 270)),
        ]

    def routing_map(
        self, direction: MatrixDirection2D = MatrixDirection2D.Column
    ) -> Layer:
        if direction == MatrixDirection2D.Column:
            return self._routing_map[1]
        elif direction == MatrixDirection2D.Row:
            return self._routing_map[0]
        else:
            raise ValueError()

    @property
    def horizontal_routing_map(self) -> Layer:
        """Routing map of the horizontal metal layer"""
        return self.routing_map[0]

    @property
    def vertical_routing_map(self) -> Layer:
        """Routing map of the vertical metal layer"""
        return self.routing_map[1]

    def is_obstacle(component: gf.Component) -> bool:
        """Returns true if the component has an obstacle marking

        :param component: The component queried
        :type component: gf.Component
        :return: True if the component has an obstacle marking, false otherwise
        :rtype: bool
        """
        ref: gf.ComponentReference
        for ref in component.references:
            if ref.name == "obstacle_marker":
                return True
        return False

    def _init_routing_map(self) -> Layer:
        routing_map = self.label_matrix

        # Determine the dimensions of the new map
        new_rows = len(routing_map) * len(self._cell_port_map)
        new_cols = len(routing_map[0]) * len(self._cell_port_map[0])

        # Create an empty new map
        new_map = [
            [Connection((i, j), None, None, 0) for i in range(new_cols)]
            for j in range(new_rows)
        ]

        # Iterate through the cell map
        for i in range(len(routing_map)):
            for j in range(len(routing_map[0])):
                cell_char = self.label_matrix[i][j]
                # Iterate through the ports
                for pi in range(len(self._cell_port_map)):
                    for pj in range(len(self._cell_port_map[0])):
                        # Calculate the position in the new map
                        new_i = i * len(self._cell_port_map) + pi
                        new_j = j * len(self._cell_port_map[0]) + pj

                        # Create the new map entry
                        new_map[new_i][new_j] = Cell(
                            f"{cell_char}.{self._cell_port_map[pi][pj]}", new_i, new_j
                        )
        return Layer(new_map, (0, 0))

    def is_line_a_route_space(self, index: int, direction : MatrixDirection2D = MatrixDirection2D.Row) -> bool:
        n: int
        line: list[MatrixElement]
        if direction == MatrixDirection2D.Column:
            n = self.routing_map().number_of_columns
            line = [row[index] for row in self.routing_map(direction).rows]
        elif direction == MatrixDirection2D.Row:
            n = self.routing_map().number_of_rows
            line = self.routing_map().rows[index]
        else:
            ValueError()
        
        if 0 <= index < n:
            return all(
                not element or str(element) == RoutingMapCharRef.ROUTE_AVAILABLE for element in line
            )
        else:
            return False

    def layout_map(self) -> list[list[float]]:
        component: gf.Component = self.resistor
        
        y: float = component.size[1] / 2.0
        layout_matrix: list[list[float]] = []
        for j, row in enumerate(self._routing_map[0].rows):
            new_row: list[float] = []
            spacing_y: float

            x: float = component.size[0] / 2.0
            for i, column in enumerate(row):
                spacing_x: float
                if type(self.routing_map().rows[j][i]) == Cell:
                    spacing_x = component.size[0]
                    spacing_y = component.size[1]
                else:
                    # TODO: Generalize float 2.0 in function of the port map
                    spacing_x = self.routing_spacing_line_width
                    spacing_y = self.routing_spacing_line_width
                    
                new_row.append((x, y))
                x += spacing_x
            y += spacing_y

            layout_matrix.append(new_row)
        return layout_matrix

    @gf.cell
    def _resistor_obstacle(
        marker_size: gf.typings.Float2, resistor: gf.Component = resistor()
    ) -> gf.Component:
        """Resistor marked as an obstacle for pathfinding in routing phase

        :param marker_size: The width and height of the marking box
        :type marker_size: gf.typings.Float2
        :param resistor: The base component, defaults to resistor()
        :type resistor: gf.Component, optional
        :return: The resistor component with the added obstacle layer
        :rtype: gf.Component
        """
        component: gf.Component = resistor.copy()
        component.add_ref(
            gf.components.rectangle(size=marker_size, layer=(66, 1), centered=True),
            "obstacle_marker",
        )
        return component

    @gf.cell
    def _resistor_target(
        marker_size: gf.typings.Float2, resistor: gf.Component = resistor()
    ) -> gf.Component:
        """Resistor marked as a target for pathfinding in routing phase

        :param marker_size: The width and height of the marking box
        :type marker_size: gf.typings.Float2
        :param resistor: The base component, defaults to resistor()
        :type resistor: gf.Component, optional
        :return: The resistor component with the added target layer
        :rtype: gf.Component
        """
        component: gf.Component = resistor.copy()
        component.add_ref(
            gf.components.rectangle(size=marker_size, layer=(66, 2), centered=True),
            "target_marker",
        )
        return component

    def _switch_cell_marking(
        self,
        matrix: gf.Component,
        cell_index: gf.typings.Int2,
    ):
        """Changes cell marking from obstacle to target or vice versa
        (must be applied to a matrix during construction)

        :param matrix: The matrix component
        :type matrix: gf.Component
        :param cell_index: Matrix index position for the targeted cell
        :type cell_index: gf.typings.Int2
        """
        # Get previous component properties and remove the old component
        old_component: gf.Component = self.component_at(cell_index)
        old_res: gf.ComponentReference = matrix.named_references[
            f"res_{cell_index[0]}_{cell_index[1]}"
        ]
        position: gf.typings.Float2 = old_res.center
        label: str = old_component.labels[0].text
        matrix.remove(old_res)

        # Create new component
        new_res: gf.ComponentReference
        if MatrixCellRouter.is_obstacle(old_component):
            new_res = matrix.add_ref(self.components[label].obstacle)
        else:
            new_res = matrix.add_ref(self.components[label].target)
        new_res.name = f"res_{cell_index[0]}_{cell_index[1]}"
        new_res.move(position)

    def get_port_of_matrix(
        matrix: gf.Component, port: CCResistorCellPort
    ) -> gf.typings.Port:
        """Get layout port of a matrix

        :param matrix: The matrix component
        :type matrix: gf.Component
        :param port: The selected port
        :type port: CCResistorCellPort
        :return: The layout port
        :rtype: gf.typings.Port
        """
        pad_port: str = "e2" if port.port_type.value == "top" else "e4"
        return matrix.named_references[f"res_{port.index[0]}_{port.index[1]}"].ports[
            f"{port.port_type.value}_{pad_port}"
        ]

    def connect_cells(
        self,
        cell_orig: CCResistorCellPort,
        cell_dest: CCResistorCellPort,
    ) -> None:
        """Connect two cells together

        :param cell_orig: Origin cell port
        :type cell_orig: CCResistorCellPort
        :param cell_dest: Destiny cell port
        :type cell_dest: CCResistorCellPort
        :param cross_section: Cross section spec, defaults to [ (gf.cross_section.metal2, (0, 180)), (gf.cross_section.metal3, (90, 270)), ]
        :type cross_section: gf.typings.MultiCrossSectionAngleSpec , optional
        :param min_spacing: Start and end minimum space for the route, defaults to 10
        :type min_spacing: float, optional
        """
        port_orig: gf.typings.Port = MatrixCellRouter.get_port_of_matrix(
            self.routing_matrix, cell_orig
        )
        port_dest: gf.typings.Port = MatrixCellRouter.get_port_of_matrix(
            self.routing_matrix, cell_dest
        )
        self.target_orig = cell_orig.index
        self.target_dest = cell_dest.index
        
        layout_map = self.layout_map()
        print(pd.DataFrame(layout_map))

        solver: RouteSolver = RouteSolver(
            self._routing_map,
            layout_map,
        )
        orig = self.map_coord_from_layout_to_routing(tuple(port_orig.center.tolist()))
        dest = self.map_coord_from_layout_to_routing(tuple(port_dest.center.tolist()))

        solver.target_orig = orig
        solver.target_dest = dest
        path = solver.astar(orig, dest)
        if path:
            path = solver.routing_path_to_layout(list(path))

            route: gf.typings.Route = gf.routing.get_route_from_waypoints(
                path,
                cross_section=self.multi_cross_section_angle_spec,
                bend=gf.components.via_corner,
            )

            self.routing_matrix.add(route.references)

    def map_index_from_cell_to_routing(
        self, index: int, direction: MatrixDirection2D
    ) -> int:
        cell_count: int = 0
        cell_length: int = 0

        arr : list[list[MatrixElement]] = np.array(self.routing_map(direction).rows)
        line: list[MatrixElement]
        if direction == MatrixDirection2D.Column:
            n = self.number_of_route_subcells_columns
            cell_length = len(self._cell_port_map[0])
            line = arr[0, :]
        elif direction == MatrixDirection2D.Row:
            n = self.number_of_route_subcells_rows
            cell_length = len(self._cell_port_map)
            line = arr[:, 0]
        else:
            raise ValueError()

        inside_cell_count: int = 0
        for i in range(n):
            if not self.is_line_a_route_space(i, direction):
                inside_cell_count += 1
                if inside_cell_count == 1:
                    cell_count += 1
                if inside_cell_count >= cell_length:
                    inside_cell_count = 0

            if cell_count == index + 1 and inside_cell_count == 0:
                return i
        raise IndexError()

    def map_coord_from_cell_to_routing(
        self, cell_coord: gf.typings.Int2
    ) -> gf.typings.Int2:
        return (
            self.map_index_from_cell_to_routing(
                cell_coord[0], direction=MatrixDirection2D.Column
            ),
            self.map_index_from_cell_to_routing(
                cell_coord[1], direction=MatrixDirection2D.Row
            ),
        )

    def map_coord_from_layout_to_routing(
        self, layout_coord: gf.typings.Float2
    ) -> gf.typings.Int2:
        map = self.layout_map()
        min_distance = float("inf")
        nearest_position = None
        x, y = layout_coord

        for i in range(len(map)):
            for j in range(len(map[i])):
                ix, jy = map[i][j]
                distance = math.sqrt((ix - x) ** 2 + (jy - y) ** 2)

                if distance < min_distance:
                    min_distance = distance
                    nearest_position = (i, j)

        return nearest_position

    def _add_route_line_lay(
        self,
        index: int,
        direction: MatrixDirection2D = MatrixDirection2D.Column,
    ) -> None:
        """Add space for a routing line

        :param matrix: The matrix component reference
        :type matrix: gf.ComponentReference
        :param index: The index of the row or column before the spacing
        :type index: int
        :param size: The size of the spacing
        :type size: float
        :param direction: Enum for selecting column or row insertion
        :type direction: MatrixDirection2D, optional
        :raises ValueError: _description_
        """
        refs: list[gf.Component] = self.routing_matrix.references
        routing_index = self.map_index_from_cell_to_routing(index, direction)
        for res in refs:
            pattern = r"res_(\d+)_(\d+)"
            match = re.search(pattern, res.name)
            if match:
                column = int(match.group(1))
                row = int(match.group(2))
                if bool(direction.value):
                    if index < row:
                        res.movey(self.routing_spacing_line_width)
                else:
                    if index < column:
                        res.movex(self.routing_spacing_line_width)
            else:
                raise ValueError()

    def add_route_line(self, index: int, direction: MatrixDirection2D):
        """Adds a line of space for routing

        :param index: The index of the row or column before the spacing
        :type index: int
        :param direction: Enum for selecting column or row insertion
        :type direction: MatrixDirection2D
        """
        for layer in self._routing_map:
            layer.add_routing_line(
                self.map_index_from_cell_to_routing(index, direction), direction
            )
        self._add_route_line_lay(index, direction)


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
