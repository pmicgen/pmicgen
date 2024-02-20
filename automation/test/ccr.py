import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import gdsfactory as gf


class CCATest(unittest.TestCase):
    def generic(self):
        import gfcells.generic as gfc
        top : gf.Component = gf.Component("top")
        top.add_ref(gfc.generic_centroid_resistor())
    
    def test_sky130(self):
        import gfcells.sky130 as gfc
        top : gf.Component = gf.Component("top")
        top.add_ref(gfc.sky130_common_centroid_resistor())
        top.show(show_ports=True, show_subports=True)
    


if __name__ == "__main__":
    unittest.main()
