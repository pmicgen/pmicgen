import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import gfcells
import gdsfactory as gf

from astar import AStar
import numpy as np
import pandas as pd


class TestEmptyCellMatrix(unittest.TestCase):
    def test_instance_with_defaults(self):
        top : gf.Component = gf.Component("TOP")
        matrix = top.add_ref(gfcells.empty_cell_matrix())
        self.assertGreater(matrix.size[0], 0)
        self.assertGreater(matrix.size[1], 0)

if __name__ == "__main__":
    unittest.main()
