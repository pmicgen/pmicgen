import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import genutils
import gdsfactory as gf


class TestEmptyCellMatrix(unittest.TestCase):
    def test_instance_with_defaults(self):
        tech = genutils.TechManager(genutils.PDK.SKY130A)
        bgr = genutils.BGR(tech)
        bgr.generate()
        bgr : gf.Component = gf.read.import_gds("bgr.gds")
        bgr.show()
        

if __name__ == "__main__":
    unittest.main()
