from attrs import frozen

import appearance.protocols as proto
from mathematics.vector import Vector2
from statuses import MISSING


@frozen
class BoardDrawableLayer(proto.DrawableLayer):
    _draw: proto.Draw
    _hovered_cell_getter: proto.UnderCursorCellGetter
    _cell_selector: proto.CellSelector
    _camera_assistant: proto.CameraAssistant

    def draw(self, mouse_position: Vector2) -> None:
        with self._camera_assistant:
            self._draw_layer(mouse_position)

    def _draw_layer(self, mouse_position: Vector2) -> None:
        self._draw.board()

        if (hovered_coord := self._hovered_cell_getter.get_coord(mouse_position)) is not MISSING:
            self._draw.under_cursor_cell(hovered_coord)

        if (selected_coord := self._cell_selector.get_coord()) is not MISSING:
            self._draw.selected_cell(selected_coord)

        self._draw.board_sprites()
