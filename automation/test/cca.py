import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import gdsfactory as gf
import gfcells
import genutils


def main():
    top : gf.Component = gf.Component("top")
    top.add_ref(gfcells.generic_common_centroid_resistor())
    top.show(show_ports=True, show_subports=True)

class CCATest(unittest.TestCase):
    pass


if __name__ == "__main__":
    main()
