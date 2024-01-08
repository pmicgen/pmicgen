import unittest
import sys
import os

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), 
                                               '..') ))

from src.ccres import *

cm = CommonCentroidMatrix(4, 0.2, 4)
print(cm.cells_repr())

class CCATest(unittest.TestCase):
    pass
