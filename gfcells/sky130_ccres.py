import gdsfactory as gf

import sky130.components as sc
import sky130.tech as st
import sky130.pcells as pc

from .routing_a import routing_a
from .generic_ccres import empty_cell_matrix, get_cell_types, common_centroid_resistor, MatrixCellRouter
from .sky130_res import sky130_resistor

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import genutils

import math


@gf.cell
def resistor(w: float = 0.35, h: float = 0.5) -> gf.Component:
    res = gf.Component("sky130_unit_resistor")
    p_poly_width = w
    p_poly_length = h
    contact_size: gf.typings.Float2 = (0.17, 0.17)
    contact_spacing: gf.typings.Float2 = (0.17, 0.17)
    licon_slots_size = (0.19, 2)
    licon_slots_spacing = (0.51, 0.51)
    contact_enclosure = (0.06, 0.06)
    li_enclosure = 0.08
    mcon_enclosure = (0.09, 0.09)
    pnpoly: gf.Component = pc.p_n_poly(
        p_poly_width=p_poly_width,
        p_poly_length=p_poly_length,
        contact_size=contact_size,
        contact_spacing=contact_spacing,
        licon_slots_size=licon_slots_size,
        licon_slots_spacing=licon_slots_spacing,
        contact_enclosure=contact_enclosure,
        li_enclosure=li_enclosure,
        mcon_enclosure=mcon_enclosure,
    )

    rect_li_m1_ymin = -(licon_slots_size[1] + contact_enclosure[1] + li_enclosure)
    rect_li_m1_ymax = rect_li_m1_ymin + (licon_slots_size[1] + 2 * li_enclosure)
    nr_m = math.ceil(
        (rect_li_m1_ymax - rect_li_m1_ymin) / (contact_size[1] + contact_spacing[1])
    )
    if (
        rect_li_m1_ymax
        - rect_li_m1_ymin
        - nr_m * contact_size[1]
        - (nr_m - 1) * contact_spacing[1]
    ) / 2 < contact_enclosure[1]:
        nr_m -= 1

    pnpoly.add_port(
        "top",
        (
            0,
            (p_poly_length / 2.0 + (contact_spacing[1] + contact_size[1]) * nr_m)
            + 0.24,
        ),
        p_poly_width,
        layer=(68, 20),
        port_type="electrical",
        cross_section=st.xs_metal1,
    )
    pnpoly.add_port(
        "bot",
        (
            0,
            -(p_poly_length / 2.0 + (contact_spacing[1] + contact_size[1]) * nr_m)
            + 0.24,
        ),
        p_poly_width,
        layer=(68, 20),
        port_type="electrical",
        cross_section=st.xs_metal1,
    )

    space_between_cells = (0.5, 0.5)
    spacing = pnpoly.size + space_between_cells

    return res


def sky130_common_centroid_resistor(
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
        components=get_cell_types(label_matrix, resistor=sky130_resistor()),
        resistor=resistor(),
    )
    matrix: gf.Component = common_centroid_resistor(
        MatrixCellRouter(
            non_routed_matrix=non_routed_matrix,
            routing_matrix=routing_matrix,
            label_matrix=label_matrix,
            resistor=sky130_resistor(),
            cell_to_pad_enclosure_height=10,
        ),
        routing_fn=routing_fn,
    )
    return matrix