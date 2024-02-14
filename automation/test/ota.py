import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from gfcells.sky130 import sky130_ota
import gdsfactory as gf

class TestEmptyCellMatrix(unittest.TestCase):
    def test_instance_with_defaults(self):
        ota : gf.Component = sky130_ota()
        ota.show()

if __name__ == "__main__":
    unittest.main()
