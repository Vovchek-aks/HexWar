import math
import random

from attrs import frozen

import appearance.protocols as proto
from appearance.graphics.sprites import SpritesLoader
from core.cells import Cells
from core.protocols import Board, Cell


@frozen
class WavesDrawer:
    _board: Board
    _sprites_loader: SpritesLoader
    _on_board_sprites_drawer: proto.OnBoardSpritesDrawer

    def draw(self) -> None:
        sprite = self._sprites_loader.load_waves()
        regions = (self._board.cells.
                   filter(lambda cell: not cell.figure.is_on_land())
                   .split(self._board))

        for region in regions:
            count = self._get_count_for(region)
            boundry = region.at_inner_boundry(self._board)
            inside = region - boundry

            for cell in random.sample(inside.as_list(), min(count, len(inside))):
                self._draw_on(cell, sprite)

            count -= len(inside)
            if count <= 0:
                continue

            for cell in random.sample(boundry.as_list(), count):
                self._draw_on(cell, sprite)

    def _draw_on(self, cell: Cell, sprite: proto.Sprite) -> None:
        coord = self._board.coordinates_of(cell)
        self._on_board_sprites_drawer.add_sprite(sprite, coord, scale_ratio=1.5)

    # https://www.desmos.com/calculator/zd10venezx
    @staticmethod
    def _get_count_for(region: Cells) -> int:
        x = len(region)
        density = 1 / (2.5 * math.log(x + 0.5))
        return min(math.ceil(x * density), x)
