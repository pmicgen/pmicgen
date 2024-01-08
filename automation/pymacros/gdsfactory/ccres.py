import gdsfactory as gf

import sky130.components as sc
import sky130.tech as st
import sky130.pcells as pc

def pnpoly():
    c = gf.Component("pnpoly")
    c = pc.p_n_poly()
    return c

c = pnpoly()
c.write_gds("build/pnpoly.gds")
c.show()