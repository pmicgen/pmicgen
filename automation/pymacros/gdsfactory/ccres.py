import gdsfactory as gf

def demo_polygons():
    c = gf.Component("demo")

    c.add_polygon(
        [(-8, 6, 7, 9), (-6, 8, 17, 5)], layer=(1, 0)
    )
    return c

c = demo_polygons()
c.write_gds("demo.gds")
c.show()