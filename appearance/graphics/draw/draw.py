from attrs import frozen

import appearance.protocols as proto
from mathematics.vector import Vector2Int
from .drawers import BordDrawer, FiguresDrawer


@frozen
class Draw(proto.Draw):
    _bord_drawer: BordDrawer
    _figures_drawer: FiguresDrawer

    def background(self) -> None:
        self._bord_drawer.draw_background()

    def board(self) -> None:
        self._bord_drawer.draw_board()

    def highlighted(self, cell_coord: Vector2Int) -> None:
        self._bord_drawer.draw_highlighted(cell_coord)

    def figures(self) -> None:
        self._figures_drawer.draw_figures()
