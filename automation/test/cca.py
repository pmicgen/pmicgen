import unittest
import sys
import os

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), 
                                               '..') ))

from src.ccres import *

cm = CommonCentroidMatrix(1,1)

class CCATest(unittest.TestCase):
    pass
