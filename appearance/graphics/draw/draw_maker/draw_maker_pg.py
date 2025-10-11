import pygame as pg

from core.protocols import Board
import appearance.protocols as proto
from ..draw import Draw
from ..drawers.drawers_pg.bord_drawer import BordDrawer
from appearance.graphics.draw.drawers.drawers_pg.figures_drawer import FiguresDrawer, FiguresSpritesBuilder
from appearance.graphics.sprite import Sprite
import core.figures.figures as fig

NO_SPRITE = "no_sprite.png"
TEST_SPRITE = "chess.png"


def make_draw[T: Draw](cls: type[T], screen: pg.Surface, camera: proto.Camera, board: Board) -> T:
    no_sprite = Sprite.load_raw_image(NO_SPRITE).with_pivot_from_ratios(.55, .55)
    test_sprite = Sprite.load_raw_image(TEST_SPRITE).with_pivot_from_ratios(.55, .55)

    figures_sprites_builder = FiguresSpritesBuilder(no_sprite)
    figures_sprites_builder.register(fig.Tree, test_sprite)
    figures_drawer = FiguresDrawer(screen, camera, board, figures_sprites_builder.build())

    board_drawer = BordDrawer(screen, camera, board)

    return cls(board_drawer, figures_drawer)
