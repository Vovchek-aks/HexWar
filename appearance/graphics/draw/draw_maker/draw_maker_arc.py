from attrs import frozen

from core.protocols import Board
import appearance.protocols as proto
from mathematics.vector import Vector2Int
from ..draw import Draw
from ..drawers import BordDrawer, FiguresDrawer
from appearance.graphics.sprites import SpritesLoader
from appearance.graphics.draw.drawers.drawers_pg.figures_drawer import FiguresSpritesLoader
from core.figures.figures import Figure, get_figures


@frozen
class DrawMaker:
    @staticmethod
    def _on_no_figure_sprite(figure: type[Figure]) -> None:
        print(f"No sprite for [{figure.__name__}] figure was found.")

    def make(self, screen_shape: Vector2Int, camera: proto.Camera, board: Board) -> Draw:
        sprites_loader = SpritesLoader.from_meta()
        figures_sprites_loader = FiguresSpritesLoader(sprites_loader)
        figures_sprites = figures_sprites_loader.load(get_figures(), self._on_no_figure_sprite)
        figures_drawer = FiguresDrawer(camera, board, figures_sprites)

        board_drawer = BordDrawer(screen_shape, camera, board)

        return Draw(board_drawer, figures_drawer)
