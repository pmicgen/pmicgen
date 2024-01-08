from __future__ import annotations

from .component import *

import sys
import os
sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), 
                                               '..') ))
from thirdparty.cca.cc import *

from typing import *
from dataclasses import dataclass

import numpy as np

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
        self.layer.rows[j][i] = self

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
MatrixElement = Union["Connection", "Cell", None]

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

    def __init__(self, element_count, ratio, row_number):
        self.element_count = element_count

        a_element_count = int(ratio * element_count)
        b_element_count = int((1-ratio) * element_count)

        a_list = list(range(1, a_element_count + 1))
        b_list = list(range(a_element_count + 1, b_element_count + 1))
        element_list = a_list + b_list
        #arr = cc_main_flow(element_list, True, "", 0, 4)

        output_from_ca = np.array(construction_algorithm_symmetry(
            element_list,
            square_array = True,
            orientation = 'hor',
            num_dummy_rows = 0,
            row_numbers = row_number)
        )

        if EvA(output_from_ca, output_from_ca.shape) != 0.0:
            arr =  ga_cc(output_from_ca.flatten(), output_from_ca.shape)
        else:
            arr = output_from_ca

        print(arr)

        arr = np.array(arr[:len(arr)]).reshape(output_from_ca.shape[0], output_from_ca.shape[1])
        #self.layers = [Layer(self, [np.zeros((output_from_ca.shape[0], output_from_ca.shape[1]), dtype=MatrixElement)])]
        self.layers = [Layer(self, [[None for _ in range(output_from_ca.shape[1])] for _ in range(output_from_ca.shape[0])])]

        for iy, ix in np.ndindex(arr.shape):
            ab_type = arr[iy, ix] > a_element_count + 1
            self.layers[0].rows[iy][ix] = Cell(self.layers[0], ix, iy, 10, 10, ab_type)        

    def connect_cells(x0, y0, x1, x2, z: int):
        pass

    def layer_repr():
        pass

    def cells_repr(self):
        repr: list[list[str]]
        for row, row_index in self.cell_matrix:
            for cell in row:
                repr[row_index] = cell.type_ab
        return repr
