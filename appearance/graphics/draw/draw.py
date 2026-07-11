from attrs import frozen

import appearance.protocols as proto
from mathematics.vector import Vector2Int
from .drawers import BoardDrawer, OnBoardSpritesDrawer, BackgroundDrawer

INTEREST_HIGHLIGHT_RATIO = .10
HOVER_HIGHLIGHT_RATIO = .15
SELECT_HIGHLIGHT_RATIO = .25


@frozen
class Draw(proto.Draw):
    _bord_drawer: BoardDrawer
    _on_board_sprites_drawer: OnBoardSpritesDrawer
    _background_drawer: BackgroundDrawer

    def background(self) -> None:
        self._background_drawer.draw_background()

    def board(self) -> None:
        self._bord_drawer.draw_board()

    def under_cursor_cell(self, cell_coord: Vector2Int) -> None:
        self._bord_drawer.draw_highlighted(cell_coord, HOVER_HIGHLIGHT_RATIO)

    def selected_cell(self, cell_coord: Vector2Int) -> None:
        self._bord_drawer.draw_highlighted(cell_coord, SELECT_HIGHLIGHT_RATIO)

    def interest_cell(self, cell_coord: Vector2Int) -> None:
        self._bord_drawer.draw_highlighted(cell_coord, INTEREST_HIGHLIGHT_RATIO)

    def board_sprites(self) -> None:
        self._on_board_sprites_drawer.draw()
