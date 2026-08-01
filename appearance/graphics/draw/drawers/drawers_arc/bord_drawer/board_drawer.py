import math
import random
from collections import defaultdict
from contextlib import contextmanager
from typing import Iterator, Callable
from time import time

from PIL import Image, ImageDraw
from attrs import define, field
import arcade as arc

from appearance.graphics.colors import WHITE
from appearance.graphics.colors import WATER, SHORE
from appearance import protocols as proto
from appearance.graphics.draw.drawers.drawers_arc.on_board_sprites_drawer import SPRITES_SCALE_RATIO
from appearance.graphics.sprites import Sprite, SpritesLoader
from color import Color
from core.distant_neighbors_getter import DistantNeighborsGetter
from core.protocols import Board, Cells, AtWater
from mathematics.hex_geometry import Neighbor, neighbors_vertexes, NEIGHBORS, neighbor_square_deltas, \
    OPPOSITE_NEIGHBOR, get_world_position, DISTANCE_BETWEEN_CENTERS
from mathematics.vector import Vector2Int, Vector2
from observer import OnEventSubscriber
from statuses import MISSING
from .shape_list import ShapeList

Shape = arc.shape_list.Shape

EDGES_WIDTH_RATIO = 1.1
EDGES_BRIGHTNESS_RATIO = .6

HATCHING_WIDTH = .25
HATCHING_BRIGHTNESS_RATIO = .2

AVERAGE_COLOR_VARIATION_AMPLITUDE = 50
MAX_COLOR_VARIATION_AMPLITUDE = 10
MAJOR_COLOR_VARIATION_FREQUENCY = 0.05

SPRITE_SIZE_MULTIPLIER = 500
SIZE_RATIO = 2 / SPRITES_SCALE_RATIO


@define
class BoardDrawer(proto.BoardDrawer):
    @classmethod
    def make(cls,
             board: Board,
             hatching_map: proto.HatchingMap,
             sprites_loader: SpritesLoader,
             on_board_sprites_drawer: proto.OnBoardSpritesDrawer,
             make_water_animator: Callable[[dict[Vector2Int, arc.Sprite]], proto.WaterAnimator],
             draw_event_finished: OnEventSubscriber[None],
             cell_changed_owner: OnEventSubscriber[Vector2Int, None]) -> "BoardDrawer":
        background_sprites = [
            sprites_loader.load_background1(),
            # sprites_loader.load_background2(),
            sprites_loader.load_background3(),
        ]
        water = sprites_loader.load_water()
        backgrounds = dict[Vector2Int, arc.Sprite]()
        for coord in board.cell_coords:
            color = cls._get_hex_color(coord, board)
            background = water if AtWater in board[coord].figure.FLAGS else random.choice(background_sprites)
            idx = on_board_sprites_drawer.add_sprite(background, coord,
                                                     scale_ratio=SIZE_RATIO * 1.01,
                                                     color=color,
                                                     need_rotation=False)
            backgrounds[coord] = on_board_sprites_drawer.get_sprite(idx)

        water = {coord: sprite
                 for coord, sprite in backgrounds.items()
                 if AtWater in board[coord].figure.FLAGS}

        self = cls(board, hatching_map, on_board_sprites_drawer, make_water_animator(water),
                   backgrounds, cell_changed_owner, draw_event_finished)
        cell_changed_owner.subscribe(self.update_cell)

        hatching = self.make_hatching()
        for coord in board.cell_coords:
            color = self._get_hatching_color(coord)
            idx = on_board_sprites_drawer.add_sprite(hatching, coord,
                                                     scale_ratio=SIZE_RATIO,
                                                     color=color,
                                                     need_rotation=False)
            self._hatchings[coord] = on_board_sprites_drawer.get_sprite(idx)

        for cell_coord in board.cell_coords:
            self._append_edges(cell_coord)

        return self

    _board: Board
    _hatching_map: proto.HatchingMap
    _on_board_sprites_drawer: proto.OnBoardSpritesDrawer
    _water_animator: proto.WaterAnimator
    _backgrounds: dict[Vector2Int, arc.Sprite]
    _cell_changed_owner: OnEventSubscriber[Vector2Int, None]
    _draw_event_finished: OnEventSubscriber[None]

    _hatchings: dict[Vector2Int, arc.Sprite] = field(init=False, factory=dict)
    _shape_list: ShapeList = field(init=False, factory=ShapeList)
    _edges: dict[Vector2Int, list[Shape]] = field(init=False, factory=lambda: defaultdict(list))

    def draw_board(self) -> None:
        self._on_board_sprites_drawer.draw()
        self._shape_list.draw()
        self._water_animator.update_all(time())

    def draw_highlighted(self, coord: Vector2Int, highlight_ratio: float) -> None:
        initial_color = (self._backgrounds[coord].color
                         if AtWater in self._board[coord].figure.FLAGS else
                         self._get_hex_color(coord, self._board))
        color = Color.lerp(initial_color, WHITE, highlight_ratio)
        self._backgrounds[coord].color = color
        if self._hatching_map.color_at(coord) is not MISSING:
            color = self._get_hatching_color(coord).lerp(WHITE, highlight_ratio)
            self._hatchings[coord].color = color

        def on_draw_event_finished() -> None:
            self._backgrounds[coord].color = self._get_hex_color(coord, self._board)
            self._hatchings[coord].color = self._get_hatching_color(coord)
            self._draw_event_finished.unsubscribe(on_draw_event_finished)

            if AtWater in self._board[coord].figure.FLAGS:
                self._water_animator.update_cell_at(coord, time())

        self._draw_event_finished.subscribe(on_draw_event_finished)

    def make_edge(self, cell_coord: Vector2Int, neighbor: Neighbor) -> Shape:
        color = self._get_edge_color(cell_coord)

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

    def make_hatching(self) -> Sprite:
        polygons = list[list[Vector2]]()

        neighbor1 = NEIGHBORS[1]
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

        polygons.append([center1 + delta,
                         center1 - delta,
                         center2 - delta,
                         center2 + delta])

        polygons.append([point1 + delta,
                         point1,
                         point1 - delta - cutoff,
                         point4 - delta + cutoff,
                         point4,
                         point4 + delta])

        polygons.append([point3 + delta + cutoff,
                         point3,
                         point3 - delta,
                         point2 - delta,
                         point2,
                         point2 + delta - cutoff])

        polygons.append([point5,
                         point5 + delta + cutoff,
                         point5 + delta - cutoff])

        polygons.append([point6,
                         point6 - delta + cutoff,
                         point6 - delta - cutoff])

        return self._get_sprite_from(*polygons)

    @contextmanager
    def not_updating_cells(self, cells: Cells) -> Iterator[None]:
        self._cell_changed_owner.unsubscribe(self.update_cell)
        yield
        self._cell_changed_owner.subscribe(self.update_cell)
        self.update_cells(cells)

    def update_hatching(self, coord: Vector2Int) -> None:
        self._hatchings[coord].color = self._get_hatching_color(coord)

    def update_cell(self, coord: Vector2Int) -> None:
        for cell in self._board.get_neighbors(self._board[coord], include_cell=True):
            self._update_cell_color(self._board.coordinates_of(cell))

    def update_cells(self, cells: Cells) -> None:
        front = cells.at_inner_boundry(self._board)
        for cell in cells - front:
            self._update_cell_color(self._board.coordinates_of(cell))
        for cell in front:
            self.update_cell(self._board.coordinates_of(cell))

    def _update_cell_color(self, coord: Vector2Int) -> None:
        assert coord in self._backgrounds

        self._backgrounds[coord].color = self._get_hex_color(coord, self._board)
        self._hatchings[coord].color = self._get_hatching_color(coord)

        self._shape_list.remove_many(*self._edges[coord])
        self._edges[coord].clear()
        self._append_edges(coord)

    def _append_edges(self, cell_coord: Vector2Int) -> None:
        assert not self._edges[cell_coord]

        for neighbor in NEIGHBORS:
            if self._should_draw_edge(cell_coord, neighbor):
                self._edges[cell_coord].append(self.make_edge(cell_coord, neighbor))

        self._shape_list.extend(*self._edges[cell_coord])

    @staticmethod
    def _get_hex_color(coord: Vector2Int, board: Board) -> Color:
        figure = board[coord].figure
        hex_color = (board[coord].owner.data.color
                     if figure.is_on_land() else
                     BoardDrawer._get_water_color(coord, board))
        state = random.getstate()
        random.seed(str(coord.tuple))
        color = Color(
            r=BoardDrawer._get_variated_channel(hex_color.r),
            g=BoardDrawer._get_variated_channel(hex_color.g),
            b=BoardDrawer._get_variated_channel(hex_color.b)
        )
        random.setstate(state)
        return color

    @staticmethod
    def _get_water_color(coord: Vector2Int, board: Board) -> Color:
        water = board[coord]
        neighbors = DistantNeighborsGetter(water, board).get_all_not_farther_than(2, include_cell=True)

        return Color.weighted_average(*((SHORE, 1)
                                        if cell.figure.is_on_land() else
                                        (WATER, 1)
                                        for cell in neighbors))

    @staticmethod
    def _get_variated_channel(channel: int) -> int:
        max_value = min(255, channel + MAX_COLOR_VARIATION_AMPLITUDE)
        min_value = max(0, channel - MAX_COLOR_VARIATION_AMPLITUDE)
        return max(min_value, min(max_value, channel + round(random.gauss(sigma=MAJOR_COLOR_VARIATION_FREQUENCY) *
                                                             AVERAGE_COLOR_VARIATION_AMPLITUDE)))

    def _get_edge_color(self, coord: Vector2Int) -> Color:
        return self._get_hex_color(coord, self._board).lerp(WHITE, EDGES_BRIGHTNESS_RATIO)

    def _get_hatching_color(self, coord: Vector2Int) -> Color:
        if self._hatching_map.color_at(coord) is MISSING:
            return Color.zero()

        return self._get_hex_color(coord, self._board).lerp(self._hatching_map.color_at(coord),
                                                            HATCHING_BRIGHTNESS_RATIO)

    def _should_draw_edge(self, coord: Vector2Int, neighbor: Neighbor) -> bool:
        cell = self._board[coord]
        neighbor_coord = coord + neighbor_square_deltas()[neighbor]
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

    @staticmethod
    def _get_sprite_from(*polygons: list[Vector2]) -> Sprite:
        size = Vector2(SPRITE_SIZE_MULTIPLIER * 2,
                       SPRITE_SIZE_MULTIPLIER * DISTANCE_BETWEEN_CENTERS)
        size_int = Vector2Int.from_vector2(size, strict=False)
        center = size / 2
        image = Image.new("RGBA",
                          size_int.tuple,
                          (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        for polygon in polygons:
            polygon = [(point * SPRITE_SIZE_MULTIPLIER + center) for point in polygon]
            polygon = [(point.with_y(size.y - point.y)).tuple for point in polygon]
            draw.polygon(polygon,
                         WHITE.tuple4)

        texture = arc.Texture(image)
        return Sprite(texture, size_int)
