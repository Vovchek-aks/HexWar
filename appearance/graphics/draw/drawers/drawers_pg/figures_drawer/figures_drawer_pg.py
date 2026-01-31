from attrs import frozen
import pygame as pg

import appearance.protocols as proto
from core.protocols import Board
from mathematics.hex_geometry import get_world_position
from mathematics.vector import Vector2Int
import core.figures.figure as fig
from appearance.graphics.sprites import Sprite

SPRITES_SCALE_RATIO = 1.5


@frozen
class FiguresDrawer(proto.FiguresDrawer):
    _screen: pg.Surface
    _camera: proto.Camera
    _board: Board
    _figures_sprites: proto.FiguresSprites

    def draw_figures(self) -> None:
        for cell_coord in self._board:
            self.draw_figure(cell_coord)

    def draw_figure(self, cell_coord: Vector2Int) -> None:
        figure = self._board[cell_coord].figure
        if isinstance(figure, fig.Land):
            return

        sprite = self._figures_sprites.get(type(figure))
        sprite = sprite.resize(self._resizing_ratio_for(sprite))

        world_position = get_world_position(cell_coord)
        screen_position = self._camera.world_to_screen(world_position)

        sprite.blit_on(self._screen, screen_position)

    def _resizing_ratio_for(self, sprite: Sprite) -> float:
        bigger_side = max(sprite.shape.x, sprite.shape.y)
        return SPRITES_SCALE_RATIO * self._camera.orientation.zoom / bigger_side
