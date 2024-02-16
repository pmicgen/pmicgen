import numpy as np
import scipy as sci
import sympy as sym
from sympy.physics.control.lti import TransferFunctionMatrix
from sympy.physics.control.control_plots import bode_plot

s = sym.Symbol('s')

## OTA params
roa = 50
gm = 1
c1 = 100e-12

## LDO params
gm1 = 1
rds = 50

## LOAD
rL = 1000
cL = 10e-12

def G_matrix(roa, gm, c1, gm1, r1, r2, rds, rL, cL, s):
    z1 = 1/(s*c1)
    zL = 1/(s*cL)
    G = sym.Matrix(([1/rds+gm1, -1/rds, -gm1, 0, -1]
             ,[-1/rds-gm1, 1/rds+1/rL+1/zL, gm1, -1/r1, 0]
             ,[0, 0, 1/roa+1/z1, gm, 0]
               ,[0, -1/r1, 0, 1/r1+1/r2, 0]
                ,[1, 0, 0, 0, 0]))
    return G

def G_openloop(roa, gm, c1, gm1, r1, r2, rds, rL, cL, s, cgs):
    z1 = 1/(s*c1)
    zL = 1/(s*cL)
    zgs = 1/(s*cgs)
    G = sym.Matrix(([0, 0, 0, -1]
             ,[0, 1/rL+1/zL, gm1, 0]
             ,[gm, 0, 1/roa+1/z1+1/zgs, 0]
                ,[1, 0, 0, 0]))
    return G

def symbol_G_openloop():
    s = sym.Symbol('s')
    roa = sym.Symbol('roa')
    gm = sym.Symbol('gm')
    z1 = sym.Symbol('z1')
    gm1 = sym.Symbol('gm1')
    r1 = sym.Symbol('r1')
    r2 = sym.Symbol('r2')
    rds = sym.Symbol('rds')
    rL = sym.Symbol('rL')
    zL = sym.Symbol('zL')

    zgs = sym.Symbol('zgs')
    
    G = sym.Matrix(([0, 0, 0, -1]
             ,[0, 1/rL+1/zL, gm1, 0]
             ,[gm, 0, 1/roa+1/z1+1/zgs, 0]
                ,[1, 0, 0, 0]))
    return G

def G_matrix_with_parasitics(roa, gm, c1, gm1, r1, r2, rds, rL, cL, s, cgs, cgd):
    z1 = 1/(s*c1)
    zL = 1/(s*cL)
    zgs = 1/(s*cgs)
    zgd = 1/(s*cgd)
    G = sym.Matrix(([1/rds+gm1+1/zgs, -1/rds, -gm1-1/zgs, 0, -1]
             ,[-1/rds-gm1, 1/rds+1/rL+1/zL+1/zgd, gm1-1/zgd, -1/r1, 0]
             ,[-1/zgs, -1/zgd, 1/roa+1/z1+1/zgs+1/zgd, gm, 0]
               ,[0, -1/r1, 0, 1/r1+1/r2, 0]
                ,[1, 0, 0, 0, 0]))
    return G

def psr_tf(G, B):
    G_inv = G.inv()
    A = sym.simplify(G_inv*B)
    tf = TransferFunctionMatrix.from_Matrix(A, s)
    return tf

def symbol_G():
    s = sym.Symbol('s')
    roa = sym.Symbol('roa')
    gm = sym.Symbol('gm')
    z1 = sym.Symbol('z1')
    gm1 = sym.Symbol('gm1')
    r1 = sym.Symbol('r1')
    r2 = sym.Symbol('r2')
    rds = sym.Symbol('rds')
    rL = sym.Symbol('rL')
    zL = sym.Symbol('zL')
    
    G = sym.Matrix(([1/rds+gm1, -1/rds, -gm1, 0, -1]
             ,[-1/rds-gm1, 1/rds+1/rL+1/zL, gm1, -1/r1, 0]
             ,[0, 0, 1/roa+1/z1, gm, 0]
               ,[0, -1/r1, 0, 1/r1+1/r2, 0]
                ,[1, 0, 0, 0, 0]))
    return G