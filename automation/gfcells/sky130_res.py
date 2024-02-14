from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gfcells import *

import gdsfactory as gf

import sky130.components as sc
import sky130.tech as st
import sky130.pcells as pc

from .generic_res import resistor

@gf.cell
def sky130_resistor(
    pad_separation: float = 50,
    enclosure: gf.typings.Float2 = (20, 20),
) -> gf.Component:
    """
    2 port generic component representation, containing 2 pads and a base.

    :param float pad_separation: The distance between both pads
    :param gf.typings.Float2 enclosure: The extension from the pads boundaries to the base size
    :param gf.Component pad: The pad component
    :return: The resistor component
    :rtype: gf.Component
    """
    resistor = pc.p_n_poly()
    return resistor