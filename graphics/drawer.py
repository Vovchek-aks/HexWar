from attrs import frozen
import pygame as pg
from pygame import Vector2

from graphics import protocols as proto
from gameplay.protocols import Board
from hex_geometry import Neighbor, X_NORM, Y_NORM, neighbors_vertexes, NEIGHBORS, neighbor_square_deltas, \
    OPPOSITE_NEIGHBOR
from vector import Vector2Int

BORDER_WIDTH_RATIO = 1.1
BORDER_BRIGHTNESS_RATIO = .6


@frozen
class Draw:
    _screen: pg.Surface
    _camera: proto.Camera
    _board: Board

    def board(self) -> None:
        for cell_coord in self._board.get_all_coords():
            self.hex_background(cell_coord)
        for cell_coord in self._board.get_all_coords():
            self.edges(cell_coord)

    def edge(self, cell_coord: Vector2Int, neighbor: Neighbor) -> None:
        color = self._board[cell_coord].owner.color.lerp(pg.Color(255, 255, 255), BORDER_BRIGHTNESS_RATIO)

        cell_coord = cell_coord + neighbor_square_deltas()[neighbor]
        neighbor = OPPOSITE_NEIGHBOR[neighbor]

        world_position = _get_world_position(cell_coord)

        left_vertex, right_vertex = neighbors_vertexes()[neighbor]
        left_vertex_far = left_vertex * BORDER_WIDTH_RATIO
        right_vertex_far = right_vertex * BORDER_WIDTH_RATIO
        vertexes = [left_vertex, left_vertex_far, right_vertex_far, right_vertex]

        pg.draw.polygon(self._screen, color, [self._camera.world_to_screen(vertex + world_position)
                                              for vertex in vertexes])

    def thin_edge(self, cell_coord: Vector2Int, neighbor: Neighbor) -> None:
        color = self._board[cell_coord].owner.color
        c = 5
        color += pg.Color(c, c, c)

        world_position = _get_world_position(cell_coord)
        left_vertex, right_vertex = (self._camera.world_to_screen(vertex + world_position)
                                     for vertex in neighbors_vertexes()[neighbor])

        pg.draw.line(self._screen, color, left_vertex, right_vertex)

    def edges(self, cell_coord: Vector2Int) -> None:
        for neighbor in NEIGHBORS:
            if self._should_draw_edge(cell_coord, neighbor):
                self.edge(cell_coord, neighbor)

    def hex_background(self, cell_coord: Vector2Int) -> None:
        world_position = _get_world_position(cell_coord)
        points = [self._camera.world_to_screen(vertex_pair[0] + world_position)
                  for vertex_pair in neighbors_vertexes().values()]

        color = self._board[cell_coord].owner.color
        pg.draw.polygon(self._screen, color, points)

    def _should_draw_edge(self, cell_coord: Vector2Int, neighbor: Neighbor) -> bool:
        cell = self._board[cell_coord]
        neighbor_coord = cell_coord + neighbor_square_deltas()[neighbor]
        if neighbor_coord not in self._board:
            return True

        neighbor_cell = self._board[neighbor_coord]
        return cell.owner != neighbor_cell.owner


def _get_world_position(cell_coord: Vector2Int) -> Vector2:
    return cell_coord.x * X_NORM + cell_coord.y * Y_NORM
