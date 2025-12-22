from attrs import define, field
import arcade as arc

from appearance import protocols as proto
from appearance.graphics.basic_colors import WHITE
from appearance.graphics.colors import BACKGROUND
from core.protocols import Board
from mathematics.hex_geometry import Neighbor, neighbors_vertexes, NEIGHBORS, neighbor_square_deltas, \
    OPPOSITE_NEIGHBOR, get_world_position
from mathematics.vector import Vector2Int

EDGES_WIDTH_RATIO = 1.1
EDGES_BRIGHTNESS_RATIO = .6


@define
class BordDrawer(proto.BordDrawer):
    @classmethod
    def make(cls,
             screen_shape: Vector2Int,
             camera: proto.Camera,
             board: Board) -> "BordDrawer":
        self = cls(screen_shape, camera, board)
        self._update_shape_list()
        camera.orientation.has_changed.subscribe(self._update_shape_list)
        return self

    _screen_shape: Vector2Int
    _camera: proto.Camera
    _board: Board
    _shape_list: arc.shape_list.ShapeElementList = field(init=False, factory=arc.shape_list.ShapeElementList)

    def draw_board(self) -> None:
        self._shape_list.draw()

    def draw_background(self) -> None:
        rectangle = arc.rect.LBWH(*Vector2Int.zero().tuple, *self._screen_shape.tuple)
        arc.draw_rect_filled(rectangle, BACKGROUND)

    def draw_highlighted(self, cell_coord: Vector2Int, highlight_ratio: float) -> None:
        color = self._get_hex_color(cell_coord).lerp(WHITE, highlight_ratio)
        self._make_hex_background_no_auto_color(cell_coord, color).draw()
        self._draw_edges(cell_coord)

    def _update_shape_list(self) -> None:
        self._shape_list.clear()

        for cell_coord in self._board:
            self._append_hex_background(cell_coord)

        for cell_coord in self._board:
            self._append_edges(cell_coord)

    def _make_edge(self, cell_coord: Vector2Int, neighbor: Neighbor) -> arc.shape_list.Shape:
        color = self._get_hex_color(cell_coord).lerp(WHITE, EDGES_BRIGHTNESS_RATIO)

        cell_coord = cell_coord + neighbor_square_deltas()[neighbor]
        neighbor = OPPOSITE_NEIGHBOR[neighbor]

        world_position = get_world_position(cell_coord)

        left_vertex, right_vertex = neighbors_vertexes()[neighbor]
        left_vertex_far = left_vertex * EDGES_WIDTH_RATIO
        right_vertex_far = right_vertex * EDGES_WIDTH_RATIO
        vertexes = [left_vertex, left_vertex_far, right_vertex_far, right_vertex]

        points = [self._camera.world_to_screen(vertex + world_position) for vertex in vertexes]
        edge = arc.shape_list.create_polygon(points, color)
        return edge

    def _draw_edges(self, cell_coord: Vector2Int) -> None:
        for neighbor in NEIGHBORS:
            if self._should_draw_edge(cell_coord, neighbor):
                self._make_edge(cell_coord, neighbor).draw()

    def _append_edges(self, cell_coord: Vector2Int) -> None:
        for neighbor in NEIGHBORS:
            if self._should_draw_edge(cell_coord, neighbor):
                edge = self._make_edge(cell_coord, neighbor)
                self._shape_list.append(edge)

    def _append_hex_background(self, cell_coord: Vector2Int) -> None:
        hexagon = self._make_hex_background(cell_coord)
        self._shape_list.append(hexagon)

    def _make_hex_background(self, cell_coord: Vector2Int) -> arc.shape_list.Shape:
        return self._make_hex_background_no_auto_color(cell_coord, self._get_hex_color(cell_coord))

    def _get_hex_color(self, cell_coord: Vector2Int) -> arc.color.Color:
        return self._board[cell_coord].owner.data.color

    def _make_hex_background_no_auto_color(self, cell_coord: Vector2Int,
                                           color: arc.color.Color) -> arc.shape_list.Shape:
        world_position = get_world_position(cell_coord)
        points = [self._camera.world_to_screen(vertex_pair[0] + world_position)
                  for vertex_pair in neighbors_vertexes().values()]
        hexagon = arc.shape_list.create_polygon(points, color)
        return hexagon

    def _should_draw_edge(self, cell_coord: Vector2Int, neighbor: Neighbor) -> bool:
        cell = self._board[cell_coord]
        neighbor_coord = cell_coord + neighbor_square_deltas()[neighbor]
        if neighbor_coord not in self._board:
            return True

        neighbor_cell = self._board[neighbor_coord]
        return cell.owner != neighbor_cell.owner
