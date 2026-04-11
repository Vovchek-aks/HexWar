from attrs import frozen

from core.protocols import Board, CellsChangesObserver
import appearance.protocols as proto
from mathematics.vector import Vector2Int
from ..draw import Draw
from ..drawers import BordDrawer, FiguresDrawer, BackgroundDrawer
from appearance.graphics.colors import BACKGROUND
from appearance.graphics.sprites import SpritesLoader
from appearance.graphics.draw.drawers.drawers_arc.figures_drawer import FiguresSpritesLoader
from core.figures.figure import Figure, get_figures


@frozen
class DrawMaker:
    @staticmethod
    def _on_no_figure_sprite(figure: type[Figure]) -> None:
        print(f"No sprite for [{figure.__name__}] figure was found.")

    def make(self,
             screen_shape: Vector2Int,
             on_board_sprites_drawer: proto.OnBoardSpritesDrawer,
             board: Board,
             cells_change_observer: CellsChangesObserver) -> tuple[Draw, FiguresDrawer, BordDrawer]:
        sprites_loader = SpritesLoader.from_meta()
        figures_sprites_loader = FiguresSpritesLoader(sprites_loader)
        figures_sprites = figures_sprites_loader.load(get_figures(), self._on_no_figure_sprite)
        figures_drawer = FiguresDrawer.make(board, figures_sprites, on_board_sprites_drawer)
        cells_change_observer.cell_changed_figure.subscribe(figures_drawer.update_cell)

        for figure in get_figures():
            index = on_board_sprites_drawer.add_sprite(figures_sprites.get(figure), Vector2Int.zero())
            on_board_sprites_drawer.remove_sprite(index)

        board_drawer = BordDrawer.make(board, cells_change_observer.cell_changed_owner)

        return (Draw(board_drawer, on_board_sprites_drawer, BackgroundDrawer(screen_shape, BACKGROUND)),
                figures_drawer, board_drawer)
