import math
import random
from collections import defaultdict
from contextlib import contextmanager
from typing import Iterator

from attrs import define, field
import arcade as arc

from appearance.graphics.colors import WHITE
from appearance.graphics.colors import WATER, SHORE
from appearance import protocols as proto
from color import Color
from core.distant_neighbors_getter import DistantNeighborsGetter
from core.protocols import Board, Cells
from mathematics.hex_geometry import Neighbor, neighbors_vertexes, NEIGHBORS, neighbor_square_deltas, \
    OPPOSITE_NEIGHBOR, get_world_position
from mathematics.vector import Vector2Int
from observer import OnEventSubscriber
from statuses import MISSING

ShapeList = arc.shape_list.ShapeElementList
Shape = arc.shape_list.Shape

EDGES_WIDTH_RATIO = 1.1
EDGES_BRIGHTNESS_RATIO = .6

HATCHING_WIDTH = .1
HATCHING_BRIGHTNESS_RATIO = .8

AVERAGE_COLOR_VARIATION_AMPLITUDE = 50
MAX_COLOR_VARIATION_AMPLITUDE = 10
MAJOR_COLOR_VARIATION_FREQUENCY = 0.05


@define
class BordDrawer(proto.BordDrawer):
    @classmethod
    def make(cls,
             board: Board,
             hatching_map: proto.HatchingMap,
             cell_changed_owner: OnEventSubscriber[Vector2Int, None]) -> "BordDrawer":
        self = cls(board, hatching_map, cell_changed_owner)
        cell_changed_owner.subscribe(self.update_cell)

        for cell_coord in board.cell_coords:
            self._append_hex_background(cell_coord)
        for cell_coord in board.cell_coords:
            self._append_edges(cell_coord)

        return self

    _board: Board
    _hatching_map: proto.HatchingMap
    _cell_changed_owner: OnEventSubscriber[Vector2Int, None]

    _shape_list: ShapeList = field(init=False, factory=ShapeList)
    _backgrounds: dict[Vector2Int, Shape] = field(init=False, factory=dict)
    _edges: dict[Vector2Int, list[Shape]] = field(init=False, factory=lambda: defaultdict(list))
    _hatchings: dict[Vector2Int, list[Shape]] = field(init=False, factory=lambda: defaultdict(list))

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

    def make_hatching(self, cell_coord: Vector2Int) -> list[Shape]:
        lines = list[Shape]()
        world_position = get_world_position(cell_coord)
        color = self._get_hatching_color(cell_coord)

        neighbor1 = NEIGHBORS[0]
        neighbor2 = OPPOSITE_NEIGHBOR[neighbor1]

        point1, point2 = neighbors_vertexes()[neighbor1]
        point3, point4 = neighbors_vertexes()[neighbor2]

        point5, point6 = sorted({pair[0] for pair in neighbors_vertexes().values()} -
                                {point1, point2, point3, point4},
                                key=lambda point: point.tuple)

        center1 = (point1 + point2) / 2
        center2 = (point3 + point4) / 2

        vector = (point2 - point1).normalize()

        delta = vector * HATCHING_WIDTH / 2
        cutoff = vector.perpendicular * delta.length() * math.tan(math.pi / 3)

        lines.append(arc.shape_list.create_polygon([vertex + world_position
                                                    for vertex in (center1 + delta,
                                                                   center1 - delta,
                                                                   center2 - delta,
                                                                   center2 + delta)],
                                                   color))
        #
        lines.append(arc.shape_list.create_polygon([vertex + world_position
                                                    for vertex in (point1 + delta,
                                                                   point1,
                                                                   point1 - delta - cutoff,
                                                                   point4 - delta + cutoff,
                                                                   point4,
                                                                   point4 + delta)],
                                                   color))

        lines.append(arc.shape_list.create_polygon([vertex + world_position
                                                    for vertex in (point3 + delta + cutoff,
                                                                   point3,
                                                                   point3 - delta,
                                                                   point2 - delta,
                                                                   point2,
                                                                   point2 + delta - cutoff)],
                                                   color))

        lines.append(arc.shape_list.create_polygon([vertex + world_position
                                                    for vertex in (point5,
                                                                   point5 + delta + cutoff,
                                                                   point5 + delta - cutoff)],
                                                   color))

        lines.append(arc.shape_list.create_polygon([vertex + world_position
                                                    for vertex in (point6,
                                                                   point6 - delta + cutoff,
                                                                   point6 - delta - cutoff)],
                                                   color))

        return lines

    def draw_hatching(self, cell_coord: Vector2Int) -> None:
        for shape in self.make_hatching(cell_coord):
            shape.draw()

    def make_hex_background(self, cell_coord: Vector2Int) -> Shape:
        return self._make_hex_background_no_auto_color(cell_coord, self._get_hex_color(cell_coord))

    @contextmanager
    def not_updating_cells(self, cells: Cells) -> Iterator[None]:
        self._cell_changed_owner.unsubscribe(self.update_cell)
        yield
        self._cell_changed_owner.subscribe(self.update_cell)
        self.update_cells(cells)

    def update_cell(self, cell_coord: Vector2Int) -> None:
        for cell in self._board.get_neighbors(self._board[cell_coord], include_cell=True):
            self._update_cell_color(self._board.coordinates_of(cell))
        self._shape_list.update()

    def update_cells(self, cells: Cells) -> None:
        front = cells.at_inner_boundry(self._board)
        for cell in cells - front:
            self._update_cell_color(self._board.coordinates_of(cell))
        self._shape_list.update()
        for cell in front:
            self.update_cell(self._board.coordinates_of(cell))

    def _update_cell_color(self, cell_coord: Vector2Int) -> None:
        assert cell_coord in self._backgrounds

        self._shape_list.remove(self._backgrounds[cell_coord])
        self._append_hex_background(cell_coord)

        for line in self._hatchings.get(cell_coord, []):
            self._shape_list.remove(line)
        self._hatchings.get(cell_coord, []).clear()

        if self._hatching_map.color_at(cell_coord) is not MISSING:
            self._append_hatching(cell_coord)

        if cell_coord in self._edges:
            for edge in self._edges[cell_coord]:
                self._shape_list.remove(edge)
            self._edges[cell_coord].clear()
        self._append_edges(cell_coord)

    def _append_hex_background(self, cell_coord: Vector2Int) -> None:
        hexagon = self.make_hex_background(cell_coord)
        self._backgrounds[cell_coord] = hexagon
        self._shape_list.append(hexagon)

    def _append_edges(self, cell_coord: Vector2Int) -> None:
        for neighbor in NEIGHBORS:
            if self._should_draw_edge(cell_coord, neighbor):
                edge = self.make_edge(cell_coord, neighbor)
                self._edges[cell_coord].append(edge)
                self._shape_list.append(edge)

    def _append_hatching(self, cell_coord: Vector2Int) -> None:
        hatching = self.make_hatching(cell_coord)
        self._hatchings[cell_coord] = hatching
        for line in hatching:
            self._shape_list.append(line)

    def _get_hex_color(self, cell_coord: Vector2Int) -> Color:
        figure = self._board[cell_coord].figure
        hex_color = (self._board[cell_coord].owner.data.color
                     if figure.is_on_land() else
                     self._get_water_color(cell_coord))
        state = random.getstate()
        random.seed(str(cell_coord.tuple))
        color = Color(
            r=self._get_variated_channel(hex_color.r),
            g=self._get_variated_channel(hex_color.g),
            b=self._get_variated_channel(hex_color.b)
        )
        random.setstate(state)
        return color

    def _get_water_color(self, cell_coord: Vector2Int) -> Color:
        water = self._board[cell_coord]
        neighbors = DistantNeighborsGetter(water, self._board).get_all_not_farther_than(2, include_cell=True)

        return Color.weighted_average(*((SHORE, .5)
                                        if cell.figure.is_on_land() else
                                        (WATER, 1)
                                        for cell in neighbors))

    @staticmethod
    def _get_variated_channel(channel: int) -> int:
        max_value = min(255, channel + MAX_COLOR_VARIATION_AMPLITUDE)
        min_value = max(0, channel - MAX_COLOR_VARIATION_AMPLITUDE)
        return max(min_value, min(max_value, channel + round(random.gauss(sigma=MAJOR_COLOR_VARIATION_FREQUENCY) *
                                                             AVERAGE_COLOR_VARIATION_AMPLITUDE)))

    def _get_edges_color(self, cell_coord: Vector2Int) -> Color:
        return self._get_hex_color(cell_coord).lerp(WHITE, EDGES_BRIGHTNESS_RATIO)

    def _get_hatching_color(self, cell_coord: Vector2Int) -> Color:
        return self._get_hex_color(cell_coord).lerp(self._hatching_map.color_at(cell_coord), HATCHING_BRIGHTNESS_RATIO)

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
