import math
import random
from contextlib import contextmanager
from typing import Iterator

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
from core.protocols import Board, Cells
from mathematics.hex_geometry import Neighbor, neighbors_vertexes, NEIGHBORS, neighbor_square_deltas, \
    OPPOSITE_NEIGHBOR, get_world_position, DISTANCE_BETWEEN_CENTERS
from mathematics.vector import Vector2Int, Vector2
from observer import OnEventSubscriber
from statuses import MISSING

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
             draw_event_finished: OnEventSubscriber[None],
             cell_changed_owner: OnEventSubscriber[Vector2Int, None]) -> "BoardDrawer":
        self = cls(board, hatching_map, on_board_sprites_drawer, cell_changed_owner, draw_event_finished)
        cell_changed_owner.subscribe(self.update_cell)

        backgrounds = [
            sprites_loader.load_background1(),
            # sprites_loader.load_background2(),
            sprites_loader.load_background3(),
        ]
        for coord in board.cell_coords:
            color = self._get_hex_color(coord)
            background = random.choice(backgrounds)
            idx = on_board_sprites_drawer.add_sprite(background, coord,
                                                     scale_ratio=SIZE_RATIO * 1.01,
                                                     color=color,
                                                     need_rotation=False)
            self._backgrounds[coord] = on_board_sprites_drawer.get_sprite(idx)

        hatching = self.make_hatching()
        for coord in board.cell_coords:
            color = self._get_hatching_color(coord)
            idx = on_board_sprites_drawer.add_sprite(hatching, coord,
                                                     scale_ratio=SIZE_RATIO,
                                                     color=color,
                                                     need_rotation=False)
            self._hatchings[coord] = on_board_sprites_drawer.get_sprite(idx)

        neighbors_and_sprites = [(neighbor, self.make_edge(neighbor)) for neighbor in NEIGHBORS]
        for coord in board.cell_coords:
            self._edges[coord] = {}
            for neighbor, sprite in neighbors_and_sprites:
                color = self._get_edges_color(coord, neighbor)
                idx = on_board_sprites_drawer.add_sprite(sprite, coord,
                                                         scale_ratio=SIZE_RATIO,
                                                         color=color,
                                                         need_rotation=False)
                self._edges[coord][neighbor] = on_board_sprites_drawer.get_sprite(idx)

        return self

    _board: Board
    _hatching_map: proto.HatchingMap
    _on_board_sprites_drawer: proto.OnBoardSpritesDrawer
    _cell_changed_owner: OnEventSubscriber[Vector2Int, None]
    _draw_event_finished: OnEventSubscriber[None]

    _backgrounds: dict[Vector2Int, arc.Sprite] = field(init=False, factory=dict)
    _edges: dict[Vector2Int, dict[Neighbor, arc.Sprite]] = field(init=False, factory=dict)
    _hatchings: dict[Vector2Int, arc.Sprite] = field(init=False, factory=dict)

    def draw_board(self) -> None:
        # self._on_board_sprites_drawer.draw()
        ...

    def draw_highlighted(self, coord: Vector2Int, highlight_ratio: float) -> None:
        color = self._get_hex_color(coord).lerp(WHITE, highlight_ratio)
        self._backgrounds[coord].color = color
        if self._hatching_map.color_at(coord) is not MISSING:
            color = self._get_hatching_color(coord).lerp(WHITE, highlight_ratio)
            self._hatchings[coord].color = color

        def on_draw_event_finished() -> None:
            self._backgrounds[coord].color = self._get_hex_color(coord)
            self._hatchings[coord].color = self._get_hatching_color(coord)
            self._draw_event_finished.unsubscribe(on_draw_event_finished)

        self._draw_event_finished.subscribe(on_draw_event_finished)

    def make_edge(self, neighbor: Neighbor) -> arc.Sprite:
        neighbor = NEIGHBORS[(NEIGHBORS.index(neighbor) + 1) % len(NEIGHBORS)]
        square_delta = neighbor_square_deltas()[neighbor]
        position = get_world_position(square_delta)
        neighbor = OPPOSITE_NEIGHBOR[neighbor]

        left_vertex, right_vertex = neighbors_vertexes()[neighbor]
        left_vertex_far = left_vertex * EDGES_WIDTH_RATIO
        right_vertex_far = right_vertex * EDGES_WIDTH_RATIO
        vertexes = [left_vertex, left_vertex_far, right_vertex_far, right_vertex]
        vertexes = [point + position for point in vertexes]
        return self._get_sprite_from(vertexes)

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

        self._backgrounds[coord].color = self._get_hex_color(coord)
        self._hatchings[coord].color = self._get_hatching_color(coord)
        for neighbor, edge in self._edges[coord].items():
            edge.color = self._get_edges_color(coord, neighbor)

    def _get_hex_color(self, coord: Vector2Int) -> Color:
        figure = self._board[coord].figure
        hex_color = (self._board[coord].owner.data.color
                     if figure.is_on_land() else
                     self._get_water_color(coord))
        state = random.getstate()
        random.seed(str(coord.tuple))
        color = Color(
            r=self._get_variated_channel(hex_color.r),
            g=self._get_variated_channel(hex_color.g),
            b=self._get_variated_channel(hex_color.b)
        )
        random.setstate(state)
        return color

    def _get_water_color(self, coord: Vector2Int) -> Color:
        water = self._board[coord]
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

    def _get_edges_color(self, coord: Vector2Int, neighbor: Neighbor) -> Color:
        if not self._should_draw_edge(coord, neighbor):
            return Color.zero()

        return self._get_hex_color(coord).lerp(WHITE, EDGES_BRIGHTNESS_RATIO)

    def _get_hatching_color(self, coord: Vector2Int) -> Color:
        if self._hatching_map.color_at(coord) is MISSING:
            return Color.zero()

        return self._get_hex_color(coord).lerp(self._hatching_map.color_at(coord), HATCHING_BRIGHTNESS_RATIO)

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
