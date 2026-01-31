import random
from collections import defaultdict

from attrs import define, field
import arcade as arc

from appearance.graphics.basic_colors import WHITE
from appearance.graphics.colors import WATER
from appearance import protocols as proto
from color import Color
from core.protocols import Board
from mathematics.hex_geometry import Neighbor, neighbors_vertexes, NEIGHBORS, neighbor_square_deltas, \
    OPPOSITE_NEIGHBOR, get_world_position
from mathematics.vector import Vector2Int

ShapeList = arc.shape_list.ShapeElementList
Shape = arc.shape_list.Shape

EDGES_WIDTH_RATIO = 1.1
EDGES_BRIGHTNESS_RATIO = .6

AVERAGE_COLOR_VARIATION_AMPLITUDE = 50
MAX_COLOR_VARIATION_AMPLITUDE = 10
MAJOR_COLOR_VARIATION_FREQUENCY = 0.05


@define
class BordDrawer(proto.BordDrawer):
    @classmethod
    def make(cls, board: Board) -> "BordDrawer":
        self = cls(board)

        for cell_coord in board.cell_coords:
            self.append_hex_background(cell_coord)
        for cell_coord in board.cell_coords:
            self.append_edges(cell_coord)

        return self

    _board: Board

    _shape_list: ShapeList = field(init=False, factory=ShapeList)
    _backgrounds: dict[Vector2Int, Shape] = field(init=False, factory=dict)
    _edges: dict[Vector2Int, list[Shape]] = field(init=False, factory=lambda: defaultdict(list))

    def draw_board(self) -> None:
        self._shape_list.draw()

    def draw_highlighted(self, cell_coord: Vector2Int, highlight_ratio: float) -> None:
        color = self._get_hex_color(cell_coord).lerp(WHITE, highlight_ratio)
        self._make_hex_background_no_auto_color(cell_coord, color).draw()
        self.draw_edges(cell_coord)

    def make_edge(self, cell_coord: Vector2Int, neighbor: Neighbor) -> Shape:
        color = self._get_edges_color(cell_coord)

        cell_coord = cell_coord + neighbor_square_deltas()[neighbor]
        neighbor = OPPOSITE_NEIGHBOR[neighbor]

        world_position = get_world_position(cell_coord)

        left_vertex, right_vertex = neighbors_vertexes()[neighbor]
        left_vertex_far = left_vertex * EDGES_WIDTH_RATIO
        right_vertex_far = right_vertex * EDGES_WIDTH_RATIO
        vertexes = [left_vertex, left_vertex_far, right_vertex_far, right_vertex]

        points = [vertex + world_position for vertex in vertexes]
        edge = arc.shape_list.create_polygon(points, color)
        return edge

    def draw_edges(self, cell_coord: Vector2Int) -> None:
        for neighbor in NEIGHBORS:
            if self._should_draw_edge(cell_coord, neighbor):
                self.make_edge(cell_coord, neighbor).draw()

    def make_hex_background(self, cell_coord: Vector2Int) -> Shape:
        return self._make_hex_background_no_auto_color(cell_coord, self._get_hex_color(cell_coord))

    def append_edges(self, cell_coord: Vector2Int) -> None:
        for neighbor in NEIGHBORS:
            if self._should_draw_edge(cell_coord, neighbor):
                edge = self.make_edge(cell_coord, neighbor)
                self._edges[cell_coord].append(edge)
                self._shape_list.append(edge)

    def append_hex_background(self, cell_coord: Vector2Int) -> None:
        hexagon = self.make_hex_background(cell_coord)
        self._backgrounds[cell_coord] = hexagon
        self._shape_list.append(hexagon)

    def update_cell(self, cell_coord: Vector2Int) -> None:
        for cell in self._board.get_neighbors(self._board[cell_coord], include_cell=True):
            self._update_cell_color(self._board.coordinates_of(cell))

    def _update_cell_color(self, cell_coord: Vector2Int) -> None:
        assert cell_coord in self._backgrounds
        self._shape_list.remove(self._backgrounds[cell_coord])
        self.append_hex_background(cell_coord)

        if cell_coord in self._edges:
            for edge in self._edges[cell_coord]:
                self._shape_list.remove(edge)
            self._edges[cell_coord].clear()
        self.append_edges(cell_coord)

    def _get_hex_color(self, cell_coord: Vector2Int) -> Color:
        figure = self._board[cell_coord].figure
        hex_color = self._board[cell_coord].owner.data.color if figure.is_on_land() else WATER
        state = random.getstate()
        random.seed(str(cell_coord.tuple))
        color = Color(
            r=self._get_variated_channel(hex_color.r),
            g=self._get_variated_channel(hex_color.g),
            b=self._get_variated_channel(hex_color.b)
        )
        random.setstate(state)
        return color

    @staticmethod
    def _get_variated_channel(channel: int) -> int:
        max_value = min(255, channel + MAX_COLOR_VARIATION_AMPLITUDE)
        min_value = max(0, channel - MAX_COLOR_VARIATION_AMPLITUDE)
        return max(min_value, min(max_value, channel + round(random.gauss(sigma=MAJOR_COLOR_VARIATION_FREQUENCY) *
                                                             AVERAGE_COLOR_VARIATION_AMPLITUDE)))

    def _get_edges_color(self, cell_coord):
        return self._get_hex_color(cell_coord).lerp(WHITE, EDGES_BRIGHTNESS_RATIO)

    @staticmethod
    def _make_hex_background_no_auto_color(cell_coord: Vector2Int, color: Color) -> Shape:
        world_position = get_world_position(cell_coord)
        points = [vertex_pair[0] + world_position
                  for vertex_pair in neighbors_vertexes().values()]
        hexagon = arc.shape_list.create_polygon(points, color)
        return hexagon

    def _should_draw_edge(self, cell_coord: Vector2Int, neighbor: Neighbor) -> bool:
        cell = self._board[cell_coord]
        neighbor_coord = cell_coord + neighbor_square_deltas()[neighbor]
        if neighbor_coord not in self._board:
            return True

        neighbor_cell = self._board[neighbor_coord]
        is_neighbor_on_land = neighbor_cell.figure.is_on_land()
        if not cell.figure.is_on_land():
            return is_neighbor_on_land

        if not is_neighbor_on_land:
            return True

        neighbor_cell = self._board[neighbor_coord]
        return cell.owner != neighbor_cell.owner
