import unittest
import sys
import os

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '..') ))

from src.ccres import *

ccm = CommonCentroidMatrix(4, 0.2, 4)
ccm.layout.show()
ccm.connect_cells(0, 0, 1, 1, 1)

class CCATest(unittest.TestCase):
    pass
