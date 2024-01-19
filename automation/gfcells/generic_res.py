from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gfcells import *


@gf.cell
def resistor(
    pad_separation: float = 50,
    enclosure: gf.typings.Float2 = (20, 20),
    pad: gf.Component = gf.components.pad(),
) -> gf.Component:
    """
    2 port generic component representation, containing 2 pads and a base.

    :param float pad_separation: The distance between both pads
    :param gf.typings.Float2 enclosure: The extension from the pads boundaries to the base size
    :param gf.Component pad: The pad component
    :return: The resistor component
    :rtype: gf.Component
    """
    resistor = gf.Component()
    pad_size: gf.typings.Float2 = pad.size
    cell_size = [
        pad_size[0] + enclosure[0],
        pad_size[1] * 2 + pad_separation + enclosure[1] * 2,
    ]
    resistor.add_ref(
        component=gf.components.rectangle(size=cell_size, layer=(1, 0), centered=True),
        alias="enclosure",
    )
    pad_ref_1 = resistor.add_ref(pad, "pad_top")
    pad_ref_2 = resistor.add_ref(pad, "pad_bot")
    pad_ref_1.movey((pad_separation + pad_size[1]) / 2.0)
    pad_ref_2.movey(-(pad_separation + pad_size[1]) / 2.0)
    resistor.add_ports(pad_ref_1.ports, "top_")
    resistor.add_ports(pad_ref_2.ports, "bot_")
    return resistor
