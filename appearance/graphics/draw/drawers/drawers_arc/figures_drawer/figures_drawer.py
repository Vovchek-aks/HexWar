from attrs import frozen, field
import arcade as arc

import appearance.protocols as proto
from core.protocols import Board
from mathematics.hex_geometry import get_world_position
from mathematics.vector import Vector2Int, Vector2
import core.figures.figure as fig
from appearance.graphics.sprites import Sprite

SpriteList = arc.sprite_list.SpriteList

SPRITES_SCALE_RATIO = 1.6


@frozen
class FiguresDrawer(proto.FiguresDrawer):
    @classmethod
    def make(cls,
             board: Board,
             figures_sprites: proto.FiguresSprites,
             camera_orientation: proto.ReadonlyCameraOrientation) -> "FiguresDrawer":
        self = cls(board, figures_sprites, camera_orientation)
        camera_orientation.has_changed.subscribe(self._rotate_figures)
        for cell_coord in self._board:
            self._add_figure_sprite(cell_coord)
        return self

    _board: Board
    _figures_sprites: proto.FiguresSprites
    _camera_orientation: proto.ReadonlyCameraOrientation

    _figures: dict[Vector2Int, arc.Sprite] = field(init=False, factory=dict)
    _sprite_list: SpriteList = field(init=False, factory=SpriteList)

    def draw_figures(self) -> None:
        self._sprite_list.draw()

    def update_cell(self, cell_coord: Vector2Int) -> None:
        if cell_coord in self._figures:
            self._sprite_list.remove(self._figures.pop(cell_coord))

        self._add_figure_sprite(cell_coord)

    def _rotate_figures(self) -> None:
        for figure in self._figures.values():
            figure.angle = self._camera_orientation.rotation.degrees

    def _add_figure_sprite(self, cell_coord: Vector2Int) -> None:
        assert cell_coord not in self._figures

        figure = self._board[cell_coord].figure
        if isinstance(figure, fig.Empty):
            return

        sprite = self._make_figure_sprite(cell_coord)
        self._figures[cell_coord] = sprite
        self._sprite_list.append(sprite)

    def _make_figure_sprite(self, cell_coord: Vector2Int) -> arc.Sprite:
        figure = self._board[cell_coord].figure
        assert not isinstance(figure, fig.Empty)

        sprite = self._figures_sprites.get(type(figure))
        world_position = get_world_position(cell_coord)
        return self._get_arc_sprite(sprite, world_position)

    def _get_arc_sprite(self, sprite: Sprite, position: Vector2) -> arc.Sprite:
        arc_sprite = arc.Sprite()
        arc_sprite.texture = sprite.get()
        arc_sprite.center_x = sprite.pivot.x
        arc_sprite.center_y = sprite.pivot.y
        arc_sprite.scale = self._resizing_ratio_for(sprite)
        arc_sprite.position = position.tuple
        arc_sprite.angle = self._camera_orientation.rotation.degrees
        return arc_sprite

    @staticmethod
    def _resizing_ratio_for(sprite: Sprite) -> float:
        bigger_side = max(sprite.shape.x, sprite.shape.y)
        return SPRITES_SCALE_RATIO / bigger_side
