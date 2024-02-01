import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import gfcells

from astar import AStar
import gdsfactory as gf
import numpy as np
import pandas as pd


class TestRouteSolver(unittest.TestCase):
    def test(self):
        top_component: gf.Component = gf.Component("TOP")

        def routing(router: gfcells.MatrixCellRouter) -> None:
            for i in range(router.number_of_cell_columns - 1):
                router.add_route_line(
                    index=i, direction=gfcells.MatrixDirection2D.Column
                )
                """
                router.add_route_line(
                    index=i, direction=gfcells.MatrixDirection2D.Column
                )
                router.add_route_line(
                    index=i, direction=gfcells.MatrixDirection2D.Column
                )
                """
            for j in range(router.number_of_cell_rows - 1):
                router.add_route_line(index=j, direction=gfcells.MatrixDirection2D.Row)
                """
                router.add_route_line(index=j, direction=gfcells.MatrixDirection2D.Row)
                router.add_route_line(index=j, direction=gfcells.MatrixDirection2D.Row)
                """
            # router.add_route_line(index=0, direction=gfcells.MatrixDirection2D.Column)
            # router.add_route_line(index=1, direction=gfcells.MatrixDirection2D.Column)
            print(pd.DataFrame(router.routing_map().rows))

            router.connect_cells(
                cell_orig=gfcells.CCResistorCellPort(
                    (0, 0), gfcells.CCResistorCellPortType.BOT
                ),
                cell_dest=gfcells.CCResistorCellPort(
                    (1, 2), gfcells.CCResistorCellPortType.TOP
                ),
            )

        ccr = gfcells.generic_common_centroid_resistor(element_count=6, row_number=3, routing_fn=routing)
        top_component.add_ref(ccr)
        top_component.show()


if __name__ == "__main__":
    unittest.main()
