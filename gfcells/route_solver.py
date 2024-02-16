from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gfcells import *

from .typings import (
    MatrixDirection2D,
    CellCoord,
    RoutingCoord,
    LayoutCoord,
    RoutingMapCharRef,
)
from .cell import Cell
from .connection import Connection

from dataclasses import dataclass
import math

from astar import AStar
import pandas as pd

class RouteSolver(AStar):
    _routing_map: list[Layer]

    def __init__(self, routing_map, layout_map):
        self._routing_map = routing_map
        self._horizontal_map = routing_map[0]
        self._vertical_map = routing_map[1]
        self.layout_map = layout_map
        self._target_orig = None
        self._target_dest = None

    def routing_map(
        self, direction: MatrixDirection2D = MatrixDirection2D.Column
    ) -> Layer:
        if direction == MatrixDirection2D.Column:
            return self._routing_map[1]
        elif direction == MatrixDirection2D.Row:
            return self._routing_map[0]
        else:
            raise ValueError()

    @property
    def horizontal_map(self) -> Layer:
        return self.routing_map(MatrixDirection2D.Row)

    @property
    def vertical_map(self) -> Layer:
        return self.routing_map(MatrixDirection2D.Column)

    @property
    def target_orig(self) -> RoutingCoord:
        return self._target_orig

    @target_orig.setter
    def target_orig(self, value) -> None:
        self._target_orig = value

    @property
    def target_dest(self) -> RoutingCoord:
        return self._target_dest

    @target_dest.setter
    def target_dest(self, value) -> None:
        self._target_dest = value

    @property
    def rows(self) -> int:
        return len(self._routing_map[0].rows)

    @property
    def columns(self) -> int:
        return len(self._routing_map[0].rows[0])

    def heuristic_cost_estimate(self, n1, n2):
        """Computes the 'direct' distance between two (x,y) tuples"""
        (i1, j1) = n1
        (i2, j2) = n2

        # Check if i1 and j1 are within bounds
        if not (0 <= i1 < len(self.layout_map[0]) and 0 <= j1 < len(self.layout_map)):
            return float("inf")

        # Check if i2 and j2 are within bounds
        if not (0 <= i2 < len(self.layout_map[0]) and 0 <= j2 < len(self.layout_map)):
            return float("inf")

        x1, y1 = self.layout_map[j1][i1]
        x2, y2 = self.layout_map[j2][i2]
        return math.hypot(x2 - x1, y2 - y1)

    def distance_between(self, n1, n2):
        """This method always returns 1, as two 'neighbors' are always adajcent"""
        return 1

    def is_target(self, point: gf.typings.Int2):
        return point == self.target_orig or point == self.target_dest

    def is_obstacle(self, point: RoutingCoord, direction: MatrixDirection2D) -> bool:
        """Checks if routing item is an obstacle for the direction a route is traversing

        :param point: The routing coord of the obstacle to check
        :type point: RoutingCoord
        :param direction: The direction that the route is traversing
        :type direction: MatrixDirection2D
        :raises ValueError: If the direction is not a valid matrix direction
        :return: True if the object at point position is an obstacle, false otherwise
        :rtype: bool
        """
        i, j = point
        
        element: MatrixElement = self.routing_map(direction).rows[j][i]
        if element == None:
            return False
        elif type(element) == Connection:
            return element != RoutingMapCharRef.ROUTE_AVAILABLE
        elif type(element) == Cell:
            return True
        else:
            raise ValueError()

    def _expand_connection(
        self,
        current: RoutingCoord,
        previous: RoutingCoord,
    ):
        i1, j1 = current
        i0, j0 = previous

        direction: MatrixDirection2D
        if previous[0] == current[0]:
            direction = MatrixDirection2D.Column
        else:
            direction = MatrixDirection2D.Row

        if type(self.routing_map(direction).rows[j1][i1] ) != Cell:
            self.routing_map(direction).rows[j1][i1] = Connection(
                position=current,
                previous=self.routing_map(direction).rows[j0][i0],
                next=None,
                z=direction.value,
            )
        if type(self.routing_map(direction).rows[j0][i0]) == Connection:
            self.routing_map(direction).rows[j0][i0].next = self.routing_map(
                direction
            ).rows[j1][i1]
        elif not self.routing_map(direction).rows[j0][i0]:
            self.routing_map(direction).rows[j0][i0] = Connection(
                position=previous,
                previous=None,
                next=self.routing_map(direction).rows[j1][i1],
                z=direction.value,
            )
            self.routing_map(direction).rows[j1][i1].previous = self.routing_map(
                direction
            ).rows[j0][i0]

    def neighbors(self, node):
        """For a given coordinate in the maze, returns up to 4 adjacent(north, east, south, west)
        nodes that can be reached (=any adjacent coordinate that is not a wall)
        """
        i, j = tuple(map(int, node))

        neighbors = []
        #if j > 0 and i > 0 and j < self.rows - 1 and i < self.columns - 1:
        north = (i, j - 1)
        if j > 0 and (
            self.is_target(north)
            or not self.is_obstacle(north, MatrixDirection2D.Column)
        ):
            neighbors.append(north)

        east = (i + 1, j)
        if i < self.columns - 1 and (
            self.is_target(east) or not self.is_obstacle(east, MatrixDirection2D.Row)
        ):
            neighbors.append(east)

        west = (i - 1, j)
        if i > 0 and (
            self.is_target(west) or not self.is_obstacle(west, MatrixDirection2D.Row)
        ):
            neighbors.append(west)

        south = (i, j + 1)
        if j < self.rows - 1 and (
            self.is_target(south)
            or not self.is_obstacle(south, MatrixDirection2D.Column)
        ):
            neighbors.append(south)

        return neighbors

    def routing_path_to_layout(self, route: list[RoutingCoord]) -> list[LayoutCoord]:
        path = [self.layout_map[j][i] for i, j in route]
        return path

    def get_route(self, orig: RoutingCoord, dest: RoutingCoord) -> list[Connection]:
        self._target_orig = orig
        self._target_dest = dest

        path: list[RoutingCoord] = list(self.astar(orig, dest))
        for i, current_point in enumerate(path):
            if i > 0:
                previous_point = path[i - 1]
            else:
                previous_point = None
            if previous_point:
                self._expand_connection(
                    current_point,
                    previous_point,
                )
        route = self.routing_path_to_layout(path)
        return route
