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
from .typings import MatrixDirection2D, CCResistorCellPort, CCResistorCellPortType

import gdsfactory as gf
import pandas as pd
import numpy as np

from typing import NamedTuple
from dataclasses import dataclass
from collections.abc import Callable
import numbers
import re
from enum import Enum


# TODO: This cell should not have knowledge of obstacles and targets
@gf.cell
def empty_cell_matrix(
    label_matrix: list[list[str]],
    components: CellTypes,
    resistor: gf.Component,
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

    x: float = 0.0
    for i in range(rows):
        y: float = 0.0
        x += resistor.size[0].item()
        for j in range(columns):
            y += resistor.size[1].item()
            label: str = label_matrix[i][j]
            resistor_type = components[label].obstacle
            resistor_ref = matrix.add_ref(resistor_type, f"res_{i}_{j}")
            resistor_ref.movex(x)
            resistor_ref.movey(y)
            if j < len(spacing_y) and isinstance(spacing_y[j], numbers.Number):
                y += spacing_y[j]
        if i < len(spacing_x) and isinstance(spacing_x[i], numbers.Number):
            x += spacing_x[i]
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
        cell_to_pad_enclosure_height=15,
        cell_to_route_spacing=10,
        horizontal_layer: gf.typings.Layer = "M1",
        vertical_layer: gf.typings.Layer = "M2",
    ) -> None:
        self.label_matrix = label_matrix
        self.resistor = resistor
        self.components = get_cell_types(label_matrix=label_matrix, resistor=resistor)
        self.non_routed_matrix = non_routed_matrix
        self.routing_matrix = non_routed_matrix.copy("routing_matrix")
        self._routing_matrix_arr = label_matrix
        self._route_width = route_width
        self._cell_to_pad_enclosure_height = cell_to_pad_enclosure_height
        self._cell_to_route_spacing = cell_to_route_spacing
        self._horizontal_layer = horizontal_layer
        self._vertical_layer = vertical_layer

    non_routed_matrix: gf.Component
    routing_matrix: gf.Component
    resistor: gf.Component
    components: CellTypes
    label_matrix: list[list[str]]
    _routing_matrix_arr: list[list[str]]

    _target_orig: gf.typings.Int2 | None = None
    _target_dest: gf.typings.Int2 | None = None

    def component_at(self, index: gf.typings.Int2) -> gf.Component:
        label = self.label_matrix[index[0]][index[1]]
        if index == self.target_orig or index == self.target_dest:
            return self.components[label].target
        else:
            return self.components[label].obstacle

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

    @property
    def routing_matrix_arr(self):
        return self._routing_matrix_arr

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

        points: gf.typings.Coordinates = gf.routing.get_points_astar(
            self.routing_matrix,
            port1=port_orig,
            port2=port_dest,
            resolution=10,
            avoid_layers=[(66, 1)],
            distance=5,
            cross_section=self.multi_cross_section_angle_spec,
        )
        # for coord in points:
        #    print(coord)

        route: gf.typings.Route = gf.routing.get_route_from_waypoints(
            points,
            cross_section=self.multi_cross_section_angle_spec,
            bend=gf.components.via_corner,
        )

        self.routing_matrix.add(route.references)

    def _add_route_line_arr(
        self, index: int, direction: MatrixDirection2D = MatrixDirection2D.Column
    ) -> None:
        """Add a route line to the routing matrix array

        :param index: The index of the row or column before the spacing
        :type index: int
        :param direction: Enum for selecting column or row insertion
        :type direction: MatrixDirection2D, optional
        """
        free_char = "."
        arr = np.array(self._routing_matrix_arr)
        if direction == MatrixDirection2D.Column:
            new_line = [free_char] * arr.shape[0]
            new_arr = np.insert(arr, index + 1, new_line, axis=1)
        elif direction == MatrixDirection2D.Row:
            new_line = [free_char] * arr.shape[1]
            new_arr = np.insert(arr, index + 1, new_line, axis=0)
        else:
            return ValueError()
        
        self._routing_matrix_arr = new_arr.tolist()

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
        for res in refs:
            pattern = r"res_(\d+)_(\d+)"
            match = re.search(pattern, res.name)
            if match:
                column = int(match.group(1))
                row = int(match.group(2))
                if direction:
                    if index < column:
                        res.movex(self.routing_spacing_line_width)
                else:
                    if index < row:
                        res.movey(self.routing_spacing_line_width)
            else:
                raise ValueError()

    def add_route_line(self, index: int, direction: MatrixDirection2D):
        """Adds a line of space for routing

        :param index: The index of the row or column before the spacing
        :type index: int
        :param direction: Enum for selecting column or row insertion
        :type direction: MatrixDirection2D
        """
        self._add_route_line_arr(index, direction)
        self._add_route_line_lay(index, direction)


@gf.cell
def common_centroid_resistor(
    matrix_cell_router: MatrixCellRouter,
    routing_fn: Callable[MatrixCellRouter, None],
    route_width: float = 10.0,
    cell_route_margin: float = 20.0,
) -> gf.Component:
    routing_fn(matrix_cell_router)
    return matrix_cell_router.routing_matrix


def generic_common_centroid_resistor(
    element_count: int = 15, ratio: float = 0.4, row_number: int = 10
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
        routing_fn=routing_a,
    )
    return matrix


def test():
    genutils.CCResistor(tech=genutils.TechManager(genutils.PDK(genutils.PDK.SKY130A)))
    ccm = genutils.ccres.CommonCentroidMatrix(
        element_count=15, ratio=0.4, row_number=10
    )
    empty_cell_matrix = CellMatrixMap(ccm.cells_repr())
