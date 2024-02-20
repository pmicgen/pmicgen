import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import genutils
import gfcells
import gdsfactory as gf

class TestEmptyCellMatrix(unittest.TestCase):
    def test_instance_with_defaults(self):
        ota = gfcells.ota()

if __name__ == "__main__":
    unittest.main()
