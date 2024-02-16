import numpy as np
import sympy as sp

A = sp.Symbol('A')
B = sp.Symbol('B')

M_in = sp.Matrix([[A, A], [B, B]])
M_pi = sp.Matrix([[1, 2], [1, 2]])

print(M_in*M_pi)