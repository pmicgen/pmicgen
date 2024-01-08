from __future__ import annotations

from .component import *

import sys
import os
sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), 
                                               '..') ))
from thirdparty.cca.cc import *

from typing import *
from dataclasses import dataclass

class CCResistor(LDOComponent):
    common_centroid_matrix: CommonCentroidMatrix

class Cell:
    layer: Layer
    width: float
    height: float
    type_ab: bool

    preroute_i: int
    preroute_j: int

    def __init__(self, layer: Layer, i: int, j: int, width: float, height: float, type_ab: bool):
        self.layer = layer
        self.width = width
        self.height = height
        self.type_ab = type_ab
        self.layer.rows[i][j] = self

    @property
    def i(self):
        return self._i
    
    @i.setter
    def i(self, i):
        self._i = i
        self.layer.rows[i][self.j()]

    @property
    def j(self):
        return self._j
    
    @j.setter
    def j(self, j):
        self._j = j

""" Type alias for each element in the common centroid matrix """
MatrixElement = Union["Connection", Cell, None]

@dataclass
class Connection:
    i: int
    j: int
    width: float
    previous: MatrixElement
    next: MatrixElement

@dataclass
class Layer:
    matrix: CommonCentroidMatrix
    rows: list[list[MatrixElement]]

    def z():
        pass

class CommonCentroidMatrix:
    layers: list[Layer]
    cell_matrix: list[list[Cell]]
    element_count: int
    ratio: float

    def __init__(self, element_count, ratio):
        self.element_count = element_count

        a_element_count = int(ratio * element_count)
        b_element_count = int((1-ratio) * element_count)

        a_list = list(range(1, a_element_count + 1))
        b_list = list(range(a_element_count + 1, b_element_count + 1))
        print(a_list)
        print(b_list)
        arr = cc_main_flow(a_list + b_list, True, "", 0, 3)
        arr = np.array(arr[:len(arr)]).reshape((len(arr) ** 0.5, len(arr) ** 0.5))

        for index, value in enumerate(arr):
            ab_type = False
            if value > a_element_count + 1:
                ab_type = True
            self.layers[0].rows[index] = Cell(1, 1, ab_type)

    def connect_cells(x0, y0, x1, x2, z: int):
        pass

    def layer_repr():
        pass

    def cells_repr():
        repr: list[list[str]]
        for row, row_index in cellmatrix:
            for cell in row:
                repr[row_index] = cell.type_ab
        return repr
