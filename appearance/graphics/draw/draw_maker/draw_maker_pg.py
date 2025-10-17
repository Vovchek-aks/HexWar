from attrs import frozen
import pygame as pg

from core.protocols import Board
import appearance.protocols as proto
from ..draw import Draw
from ..drawers.drawers_pg.bord_drawer import BordDrawer
from appearance.graphics.draw.drawers.figures_drawer import FiguresDrawer
from appearance.graphics.sprites import SpritesLoader
from appearance.graphics.draw.drawers.figures_drawer import FiguresSpritesLoader
from core.figures import Figure, get_figures


@frozen
class DrawMaker[T: Draw]:
    @staticmethod
    def _on_no_figure_sprite(figure: type[Figure]) -> None:
        print(f"No sprite for [{figure.__name__}] figure was found.")

    _draw_class: type[T]

    def make(self, screen: pg.Surface, camera: proto.Camera, board: Board) -> T:
        sprites_loader = SpritesLoader.from_meta()
        figures_sprites_loader = FiguresSpritesLoader(sprites_loader)
        figures_sprites = figures_sprites_loader.load(get_figures(), self._on_no_figure_sprite)
        figures_drawer = FiguresDrawer(screen, camera, board, figures_sprites)

        board_drawer = BordDrawer(screen, camera, board)

        return self._draw_class(board_drawer, figures_drawer)
