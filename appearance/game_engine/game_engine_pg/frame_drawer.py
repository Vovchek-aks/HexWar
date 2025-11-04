from attrs import frozen
import pygame as pg

from appearance.graphics.draw import Draw
from appearance.input.cell_selector import CellSelector
from appearance.input.under_cursor_cell_getter import UnderCursorCellGetter
from mathematics.vector import Vector2
from statuses import MISSING


@frozen
class FrameDrawer:
    _draw: Draw
    _hovered_cell_getter: UnderCursorCellGetter
    _cell_selector: CellSelector

    def draw_frame(self, mouse_position: Vector2) -> None:
        self._draw.background()
        self._draw.board()

        if (hovered_coord := self._hovered_cell_getter.get_coord(mouse_position)) is not MISSING:
            self._draw.under_cursor_cell(hovered_coord)

        if (selected_coord := self._cell_selector.get_coord()) is not MISSING:
            self._draw.selected_cell(selected_coord)

        self._draw.figures()
        pg.display.flip()
