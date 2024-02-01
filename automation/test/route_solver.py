import unittest
import sys
import os
import copy

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import gfcells

from astar import AStar
import numpy as np
import pandas as pd


class TestRouteSolver(unittest.TestCase):
    def generate_test_routing_map(columns: int = 5, rows: int = 5):
        horizontal_map: gfcells.Layer = gfcells.Layer(
            np.full((columns, rows), None), (0, 0)
        )
        vertical_map: gfcells.Layer = gfcells.Layer(
            np.full((columns, rows), None), (1, 0)
        )
        return [horizontal_map, vertical_map]

    def generate_test_layout_map(
        columns: int = 5, rows: int = 5, tl_corner=(0, 0), br_corner=(100, 100)
    ):
        layout_map = np.zeros((columns, rows), dtype=tuple)

        for i in range(columns):
            for j in range(rows):
                x = np.interp(j, [0, columns - 1], [tl_corner[0], br_corner[0]])
                y = np.interp(i, [0, rows - 1], [tl_corner[1], br_corner[1]])
                layout_map[i, j] = (x, y)
        return layout_map

    def empty_map_routing(self):
        """Test A* pathfinding against a 5x5 matrix of interpolated positions as the layout map
        and a empry matrix as the routing matrix.
        """
        routing_map = TestRouteSolver.generate_test_matrix()
        layout_map = TestRouteSolver.generate_test_routing_map()
        solver: gfcells.RouteSolver = gfcells.RouteSolver(routing_map, layout_map)

        route = solver.get_route((0, 0), (1, 1))

        self.assertIn(
            route,
            [
                [(0.0, 0.0), (25.0, 0.0), (25.0, 25.0)],
                [(0.0, 0.0), (0.0, 25.0), (25.0, 25.0)],
            ],
        )
        route = solver.get_route((1, 1), (4, 4))

        self.assertEqual(route[0], (25 * 1, 25 * 1))
        self.assertEqual(route[-1], (25 * 4, 25 * 4))
        # solver.get_route((0, 1), (0, 5))

        # solver.get_route((1, 1), (4, 4))

    def intersection_without_route_collision(self):
        routing_map = TestRouteSolver.generate_test_routing_map()
        layout_map = TestRouteSolver.generate_test_layout_map()
        solver: gfcells.RouteSolver = gfcells.RouteSolver(routing_map, layout_map)

        horizontal_route = solver.get_route((0, 2), (4, 2))
        vertical_route = solver.get_route((2, 0), (2, 4))

        self.assertEqual(
            horizontal_route,
            [(0.0, 50.0), (25.0, 50.0), (50.0, 50.0), (75.0, 50.0), (100.0, 50.0)],
        )
        self.assertEqual(
            vertical_route,
            [(50.0, 0.0), (50.0, 25.0), (50.0, 50.0), (50.0, 75.0), (50.0, 100.0)],
        )

    def test_intersection_with_route_collision(self):
        horizontal_map: gfcells.Layer = gfcells.Layer(
            np.full((5, 5), None), (0, 0)
        )
        horizontal_map.rows[3, 1] = gfcells.Cell("C", 1, 3)
        horizontal_map.rows[3, 2] = gfcells.Cell("C", 2, 3)
        horizontal_map.rows[3, 3] = gfcells.Cell("C", 3, 3)
        horizontal_map.rows[4, 0] = gfcells.Cell("A", 0, 4)
        horizontal_map.rows[2, 3] = gfcells.Cell("A", 3, 2)
        horizontal_map.rows[4, 4] = gfcells.Cell("B", 4, 4)
        horizontal_map.rows[2, 1] = gfcells.Cell("B", 1, 2)
        
        vertical_map = copy.deepcopy(horizontal_map)
        
        vertical_map.layer = (1, 0)
        
        routing_map = [horizontal_map, vertical_map]
        layout_map = TestRouteSolver.generate_test_layout_map()

        solver: gfcells.RouteSolver = gfcells.RouteSolver(routing_map, layout_map)

        route_1 = solver.get_route((0, 4), (3, 2))
        route_2 = solver.get_route((4, 4), (1, 2))

        print("horizontal")
        print(pd.DataFrame(routing_map[0].rows))
        print("vertical")
        print(pd.DataFrame(routing_map[1].rows))


if __name__ == "__main__":
    unittest.main()
