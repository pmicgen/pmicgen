from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gfcells import *

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import genutils
from .ccres import *

import gdsfactory as gf

from typing import NamedTuple
from dataclasses import dataclass
import numbers
import re



def get_port_of_matrix(
    matrix: gf.Component, port: CCResistorCellPort
) -> gf.typings.Port:
    pad_port: str = "e2" if port.port_type.value == "top" else "e4"
    return matrix.named_references[f"res_{port.index[0]}_{port.index[1]}"].ports[
        f"{port.port_type.value}_{pad_port}"
    ]


@gf.cell
def _resistor_obstacle(
    marker_size: gf.typings.Float2, resistor: gf.Component = resistor()
):
    component: gf.Component = resistor.copy()
    component.add_ref(
        gf.components.rectangle(size=marker_size, layer=(66, 1), centered=True),
        "obstacle_marker",
    )
    return component


@gf.cell
def _resistor_target(
    marker_size: gf.typings.Float2, resistor: gf.Component = resistor()
):
    component: gf.Component = resistor.copy()
    component.add_ref(
        gf.components.rectangle(size=marker_size, layer=(66, 2), centered=True),
        "target_marker",
    )
    return component


def connect_cells(
    matrix: gf.ComponentReference,
    cell_matrix_map: CellMatrixMap,
    cell_orig: CCResistorCellPort,
    cell_dest: CCResistorCellPort,
    # TODO: Implement default cross section
    cross_section=[
        (gf.cross_section.metal2, (0, 180)),
        (gf.cross_section.metal3, (90, 270)),
    ],
    min_spacing: float = 10,
) -> None:
    port_orig: gf.typings.Port = get_port_of_matrix(matrix.parent, cell_orig)
    port_dest: gf.typings.Port = get_port_of_matrix(matrix.parent, cell_dest)
    cell_matrix_map.set_target_orig(matrix.parent, cell_orig.index)
    cell_matrix_map.set_target_dest(matrix.parent, cell_dest.index)
    
    m1_routing = gf.cross_section.cross_section(
        layer=(41, 0),
        width=10.0,
        port_names=gf.cross_section.port_names_electrical,
        port_types=gf.cross_section.port_types_electrical,
        radius=None,
        min_length=5,
        gap=5,
    )

    m2_routing = gf.cross_section.cross_section(
        layer=(49, 0),
        width=10.0,
        port_names=gf.cross_section.port_names_electrical,
        port_types=gf.cross_section.port_types_electrical,
        radius=None,
        min_length=5,
        gap=5,
    )

    multi_cross_section_angle_spec: gf.typings.MultiCrossSectionAngleSpec = [
        (m1_routing, (0, 180)),
        (m2_routing, (90, 270)),
    ]

    route: gf.typings.Route = gf.routing.get_route_astar(
        matrix.parent,
        port1=port_orig,
        port2=port_dest,
        resolution=10,
        avoid_layers=[(66, 1), (49, 0)],
        distance=30,
        cross_section=multi_cross_section_angle_spec,
    )

    matrix.parent.add(route.references)


@dataclass
class RouteCellVariants:
    obstacle: gf.Component
    target: gf.Component


CellTypes = dict[str, RouteCellVariants]


@dataclass
class CellMatrixMap:
    def __init__(self, label_matrix: list[list[str]], resistor=resistor()) -> None:
        self.label_matrix = label_matrix
        self.resistor = resistor
        self.components = self._get_cell_types()
        matrix = gf.Component()
        self.matrix = matrix.add_ref(self.empty_cell_matrix(resistor))

    empty_matrix: gf.Component
    resistor: gf.Component
    components: CellTypes
    label_matrix: list[list[str]]

    target_orig: gf.typings.Int2 | None = None
    target_dest: gf.typings.Int2 | None = None

    @gf.cell
    def empty_cell_matrix(
        self,
        resistor: gf.Component,
        spacing_x: list[float] = [],
        spacing_y: list[float] = [],
    ) -> gf.Component:
        matrix: gf.Component = gf.Component()
        rows = len(self.label_matrix)
        columns = len(self.label_matrix[0])

        x: float = 0.0
        for i in range(rows):
            y: float = 0.0
            x += resistor.size[0].item()
            for j in range(columns):
                y += resistor.size[1].item()
                label: str = self.label_matrix[i][j]
                resistor_type = self.components[label].obstacle
                resistor_ref = matrix.add_ref(resistor_type, f"res_{i}_{j}")
                resistor_ref.movex(x)
                resistor_ref.movey(y)
                if j < len(spacing_y) and isinstance(spacing_y[j], numbers.Number):
                    y += spacing_y[j]
            if i < len(spacing_x) and isinstance(spacing_x[i], numbers.Number):
                x += spacing_x[i]
        return matrix

    def _get_cell_types(self) -> CellTypes:
        cell_types: CellTypes = {}
        flat_labels: list[str] = [char for row in self.label_matrix for char in row]
        unique_labels: list[str] = list(set(flat_labels))
        for label in unique_labels:
            marker_size = (100, 250)
            obstacle: gf.Component = _resistor_obstacle(
                marker_size, resistor=self.resistor
            ).copy()
            obstacle.add_label(label)
            target: gf.Component = _resistor_target(
                marker_size, resistor=self.resistor
            ).copy()
            target.add_label(label)
            cell_types[label] = RouteCellVariants(obstacle, target)
        return cell_types

    def component_at(self, index: gf.typings.Int2) -> gf.Component:
        label = self.label_matrix[index[0]][index[1]]
        if index == self.target_orig or index == self.target_dest:
            return self.components[label].target
        else:
            return self.components[label].obstacle

    def set_target_orig(
        self, matrix_component: gf.Component, index_position: gf.typings.Int2
    ):
        if self.target_orig:
            self._switch_cell_marking(matrix_component, self.target_orig)
        self.target_orig = index_position
        self._switch_cell_marking(matrix_component, self.target_orig)

    def set_target_dest(
        self, matrix_component: gf.Component, index_position: gf.typings.Int2
    ):
        if self.target_dest:
            self._switch_cell_marking(matrix_component, self.target_dest)
        self.target_dest = index_position
        self._switch_cell_marking(matrix_component, self.target_dest)

    def is_obstacle(component: gf.Component) -> bool:
        ref: gf.ComponentReference
        for ref in component.references:
            if ref.name == "obstacle_marker":
                return True
        return False

    def _switch_cell_marking(
        self,
        matrix: gf.Component,
        cell_index: gf.typings.Int2,
    ):
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
        if CellMatrixMap.is_obstacle(old_component):
            new_res = matrix.add_ref(self.components[label].obstacle)
        else:
            new_res = matrix.add_ref(self.components[label].target)
        new_res.name = f"res_{cell_index[0]}_{cell_index[1]}"
        new_res.move(position)


def add_route_line(
    matrix: gf.ComponentReference, index: int, size: float, direction: bool = False
):
    refs: list[gf.ComponentReference] = matrix.parent
    for res in refs:
        pattern = r"res_(\d+)_(\d+)"
        match = re.search(pattern, res.name)
        if match:
            column = int(match.group(1))
            row = int(match.group(2))
            if direction:
                if index < column:
                    res.movex(size)
            else:
                if index < row:
                    res.movey(size)
        else:
            raise ValueError()

@gf.cell
def common_centroid_resistor_routing_a(
    non_routed_matrix: gf.Component,
    element_count: int = 15,
    ratio: float = 0.4,
    row_number: int = 10,
    resistor: gf.Component = resistor(),
    route_width: float = 10.0,
    cell_route_margin: float = 20.0,
):
    cell_pad_enclosure = resistor.to_dict()["settings"]["enclosure"]
    cell_route_margin = 20
    cell_to_route_spacing = cell_pad_enclosure[1] + cell_route_margin
    routing_line_size = 2 * cell_route_margin + route_width
    add_route_line(non_routed_matrix, 0, routing_line_size, direction=False)
    add_route_line(non_routed_matrix, 0, routing_line_size, direction=True)

    connect_cells(
        non_routed_matrix,
        cell_matrix_map=cell_matrix_map,
        cell_orig=CCResistorCellPort((0, 0), CCResistorCellPortType.TOP),
        cell_dest=CCResistorCellPort((1, 1), CCResistorCellPortType.BOT),
        min_spacing=cell_to_route_spacing,
    )
    """
    connect_cells(
        cell_matrix_map.matrix.ref(),
        cell_matrix_map=cell_matrix_map,
        cell_orig=CCResistorCellPort((0, 1), CCResistorCellPortType.BOT),
        cell_dest=CCResistorCellPort((1, 0), CCResistorCellPortType.TOP),
        min_spacing=cell_to_route_spacing,
    )
    """
    return cell_matrix_map.matrix

def test():
    genutils.CCResistor(tech=genutils.TechManager(genutils.PDK(genutils.PDK.SKY130A)))
    ccm = genutils.ccres.CommonCentroidMatrix(
        element_count=15, ratio=0.4, row_number=10
    )
    empty_cell_matrix = CellMatrixMap(ccm.cells_repr())