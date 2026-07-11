from attrs import frozen

from core.cells import Cells
from core.protocols import Board, CellsChangesObserver
import appearance.protocols as proto
from mathematics.vector import Vector2Int
from observer import OnEventSubscriber
from ..draw import Draw
from ..drawers import BoardDrawer, FiguresDrawer, BackgroundDrawer
from appearance.graphics.colors import BACKGROUND
from appearance.graphics.sprites import SpritesLoader
from appearance.graphics.draw.drawers.drawers_arc.figures_drawer import FiguresSpritesLoader
from core.figures.figure import Figure, get_figures
from ..drawers.drawers_arc.on_board_sprites_drawer import OnBoardSpritesDrawer
from ..drawers.drawers_arc.waves_drawer import WavesDrawer


@frozen
class DrawMaker:
    @staticmethod
    def _on_no_figure_sprite(figure: type[Figure]) -> None:
        print(f"No sprite for [{figure.__name__}] figure was found.")

    def make(self,
             screen_shape: Vector2Int,
             on_board_sprites_drawer: proto.OnBoardSpritesDrawer,
             board: Board,
             camera_orientation: proto.ReadonlyCameraOrientation,
             hatching_map: proto.HatchingMap,
             cells_change_observer: CellsChangesObserver,
             draw_event_finished: OnEventSubscriber[None]) -> tuple[Draw, FiguresDrawer, BoardDrawer]:
        sprites_loader = SpritesLoader.from_meta()
        figures_sprites_loader = FiguresSpritesLoader(sprites_loader)
        figures_sprites = figures_sprites_loader.load(get_figures(), self._on_no_figure_sprite)
        figures_drawer = FiguresDrawer.make(board, figures_sprites, on_board_sprites_drawer)
        cells_change_observer.cell_changed_figure.subscribe(figures_drawer.update_cell)

        for figure in get_figures():
            index = on_board_sprites_drawer.add_sprite(figures_sprites.get(figure), Vector2Int.zero())
            on_board_sprites_drawer.remove_sprite(index)

        board_drawer = BoardDrawer.make(board, hatching_map, sprites_loader,
                                        OnBoardSpritesDrawer.make(camera_orientation),
                                        draw_event_finished, cells_change_observer.cell_changed_owner)

        WavesDrawer(board, sprites_loader, on_board_sprites_drawer).draw()

        return (Draw(board_drawer, on_board_sprites_drawer, BackgroundDrawer(screen_shape, BACKGROUND)),
                figures_drawer, board_drawer)
