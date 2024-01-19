import gdsfactory as gf

import sky130.components as sc
import sky130.tech as st
import sky130.pcells as pc

import math


@gf.cell
def pnpoly_matrix(columns: int, rows: int) -> gf.Component:
    ccm = gf.Component("CommonCentroidMatrix")
    p_poly_width = 0.35
    p_poly_length = 0.5
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

    ref: gf.ComponentReference = ccm.add_ref(
        gf.components.array(
            component=pnpoly, spacing=spacing, columns=columns, rows=rows
        )
    )

    return ccm


def connect_cells(
    ref: gf.ComponentReference, c1: gf.typings.Float2, c2: gf.typings.Float2
):
    mcas: gf.cross_section.MultiCrossSectionAngleSpec() = (
        (st.xs_metal1, (0, 180)),
        (st.xs_metal1, (90, 270)),
    )
    via: gf.Component = pc.via_generator()

    via.info["size"] = via.to_dict()["settings"]["full"]["via_size"]
    via.info["enclosure"] = via.to_dict()["settings"]["full"]["via_enclosure"][0]
    via.info["spacing"] = via.to_dict()["settings"]["full"]["via_spacing"]

    via_corner: gf.Component = gf.components.via_corner(mcas, (via, via), ("m1", "m2"))
    print(via_corner.ports)
    """
    route = gf.routing.get_route_electrical(
        ref.ports[f"top_{c1[1]}_{c1[0]}"],
        ref.ports[f"bot_{c2[1]}_{c2[0]}"],
        bend=via_corner,
        cross_section=st.xs_metal1,
    )

    ref.parent.add(route.references)
    """
    port_top: gf.typings.Port = ref.ports[f"top_{c1[1]}_{c1[0]}"]
    port_bot: gf.typings.Port = ref.ports[f"bot_{c2[1]}_{c2[0]}"]
    route = gf.routing.get_route_electrical_multilayer(port_top, port_bot)

    ref.parent.add(route.references)
