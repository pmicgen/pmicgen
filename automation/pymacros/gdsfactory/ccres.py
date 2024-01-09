import gdsfactory as gf

import sky130.components as sc
import sky130.tech as st
import sky130.pcells as pc

def pnpoly_matrix(rows: int, columns: int) -> gf.Component:
    ccm = gf.Component("CommonCentroidMatrix")
    p_poly_width = 0.35
    p_poly_length = 0.5
    pnpoly: gf.Component = pc.p_n_poly(p_poly_width=p_poly_width, p_poly_length=p_poly_length, )
    pnpoly.add_port("top", (0, p_poly_length/2.0), p_poly_width, layer=(66, 20))
    pnpoly.add_port("bot", (0, -p_poly_length/2.0), p_poly_width, layer=(66, 20))
    space_between_cells = (.5, .5)
    spacing = pnpoly.size + space_between_cells
    ref = ccm << gf.components.array(component=pnpoly, spacing=spacing, columns=columns, rows=rows)
    ccm.add_ports(ref.get_ports_list())
    print(ccm)
    return ccm

c = pnpoly_matrix(10, 10)
c.write_gds("build/pnpoly.gds")
c.show(show_ports=True, show_subports=True)