from attrs import frozen

from core.moves.capture import Capture
from core.moves.relocations import Assault
from core.protocols import Board, MovesMaker, ValidMove
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

    def make(self, screen_shape: Vector2Int, camera: proto.Camera, board: Board, moves_maker: MovesMaker) -> Draw:
        sprites_loader = SpritesLoader.from_meta()
        figures_sprites_loader = FiguresSpritesLoader(sprites_loader)
        figures_sprites = figures_sprites_loader.load(get_figures(), self._on_no_figure_sprite)
        figures_drawer = FiguresDrawer(camera, board, figures_sprites)

        board_drawer = BordDrawer.make(screen_shape, camera, board)

        def _temp(move: ValidMove) -> None:
            match move.move:
                case Assault(to_coord=coord) | Capture(to_coord=coord):
                    board_drawer.update_cell_color(coord)

        moves_maker.board_move_was_made.subscribe(_temp)

        return Draw(board_drawer, figures_drawer)
