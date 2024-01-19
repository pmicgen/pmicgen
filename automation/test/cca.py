import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import gdsfactory as gf
import gfcells
import genutils


def main():
    matrix : gf.Component = gfcells.cc_pnpoly_matrix()
    matrix.show(show_ports=True, show_subports=True)
    """
    m1_routing = gf.cross_section.cross_section(
        layer=(41, 2),
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

    c = gf.Component("get_route_astar_avoid_layers")
    cross_section = gf.get_cross_section("xs_m1", width=3)
    w = gf.components.straight(cross_section=cross_section)

    left = c << w
    right = c << w
    right.move((100, 80))

    obstacle = gf.components.rectangle(size=(100, 3), layer="WG")
    obstacle1 = c << obstacle
    obstacle2 = c << obstacle
    obstacle1.ymin = 40
    obstacle2.xmin = 25

    port1 = left.ports["e2"]
    port2 = right.ports["e2"]

    routes = gf.routing.get_route_astar(
        component=c,
        port1=port1,
        port2=port2,
        cross_section=multi_cross_section_angle_spec,
        resolution=10,
        distance=10,
        avoid_layers=[(1, 0), (41, 0)],
    )

    c.add(routes.references)
    c.show()
    """


class CCATest(unittest.TestCase):
    pass


if __name__ == "__main__":
    main()
