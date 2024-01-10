import gdsfactory as gf

import sky130.components as sc
import sky130.tech as st
import sky130.pcells as pc

@gf.cell
def pnpoly_matrix(columns: int, rows: int) -> gf.Component:
    ccm = gf.Component("CommonCentroidMatrix")
    p_poly_width = 0.35
    p_poly_length = 0.5
    pnpoly: gf.Component = pc.p_n_poly(p_poly_width=p_poly_width, p_poly_length=p_poly_length)
    pnpoly.add_port("top", (0, p_poly_length/2.0), p_poly_width, layer=(66, 20), port_type="electrical")
    pnpoly.add_port("bot", (0, -p_poly_length/2.0), p_poly_width, layer=(66, 20), port_type="electrical")
    
    space_between_cells = (.5, .5)
    spacing = pnpoly.size + space_between_cells

    ref: gf.ComponentReference = ccm.add_ref(gf.components.array(component=pnpoly, spacing=spacing, columns=columns, rows=rows))
    ccm.add_ports(ref.get_ports_list())

    gf.add_pins.add_pin_triangle(component=ccm, port=ccm.ports["top_1_1"], layer=(124, 40))
    print(ref.ports)
    ref.connect(port=ref.ports["top_1_1"], destination=ref.ports["bot_1_1"])
    return ccm

c: gf.Component = pnpoly_matrix(10, 5)
c.write_gds("build/pnpoly.gds", with_metadata=True)
print(c)
c.show(show_ports=True, show_subports=True, with_metadata=True)