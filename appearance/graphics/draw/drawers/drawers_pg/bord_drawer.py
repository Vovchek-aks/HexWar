from attrs import frozen
import pygame as pg

from appearance import protocols as proto
from appearance.graphics.basic_colors import WHITE
from appearance.graphics.colors import BACKGROUND
from core.protocols import Board
from mathematics.hex_geometry import Neighbor, neighbors_vertexes, NEIGHBORS, neighbor_square_deltas, \
    OPPOSITE_NEIGHBOR, get_world_position
from mathematics.vector import Vector2Int

EDGES_WIDTH_RATIO = 1.1
EDGES_BRIGHTNESS_RATIO = .6
HIGHLIGHT_RATIO = .2


@frozen
class BordDrawer(proto.BordDrawer):
    _screen: pg.Surface
    _camera: proto.Camera
    _board: Board

    def draw_board(self) -> None:
        for cell_coord in self._board:
            self.draw_hex_background(cell_coord)
        for cell_coord in self._board:
            self.draw_edges(cell_coord)

    def draw_background(self) -> None:
        self._screen.fill(BACKGROUND)

    def draw_highlighted(self, cell_coord: Vector2Int) -> None:
        color = self._get_hex_color(cell_coord).lerp(WHITE, HIGHLIGHT_RATIO)
        self.draw_hex_background_no_auto_color(cell_coord, color)
        self.draw_edges(cell_coord)

    def draw_edge(self, cell_coord: Vector2Int, neighbor: Neighbor) -> None:
        color = self._get_hex_color(cell_coord).lerp(WHITE, EDGES_BRIGHTNESS_RATIO)

        cell_coord = cell_coord + neighbor_square_deltas()[neighbor]
        neighbor = OPPOSITE_NEIGHBOR[neighbor]

        world_position = get_world_position(cell_coord)

        left_vertex, right_vertex = neighbors_vertexes()[neighbor]
        left_vertex_far = left_vertex * EDGES_WIDTH_RATIO
        right_vertex_far = right_vertex * EDGES_WIDTH_RATIO
        vertexes = [left_vertex, left_vertex_far, right_vertex_far, right_vertex]

        pg.draw.polygon(self._screen, color, [self._camera.world_to_screen(vertex + world_position)
                                              for vertex in vertexes])

    def draw_edges(self, cell_coord: Vector2Int) -> None:
        for neighbor in NEIGHBORS:
            if self._should_draw_edge(cell_coord, neighbor):
                self.draw_edge(cell_coord, neighbor)

    def draw_hex_background(self, cell_coord: Vector2Int) -> None:
        self.draw_hex_background_no_auto_color(cell_coord, self._get_hex_color(cell_coord))

    def _get_hex_color(self, cell_coord: Vector2Int) -> pg.Color:
        return self._board[cell_coord].owner.color

    def draw_hex_background_no_auto_color(self, cell_coord: Vector2Int, color: pg.Color) -> None:
        world_position = get_world_position(cell_coord)
        points = [self._camera.world_to_screen(vertex_pair[0] + world_position)
                  for vertex_pair in neighbors_vertexes().values()]
        pg.draw.polygon(self._screen, color, points)

    def _should_draw_edge(self, cell_coord: Vector2Int, neighbor: Neighbor) -> bool:
        cell = self._board[cell_coord]
        neighbor_coord = cell_coord + neighbor_square_deltas()[neighbor]
        if neighbor_coord not in self._board:
            return True

        neighbor_cell = self._board[neighbor_coord]
        return cell.owner != neighbor_cell.owner
