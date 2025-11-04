from typing import Callable

from attrs import frozen

from appearance.input.clicks_catcher.click import Buttons
from appearance.input.moves_inputer.input_actions import CellClickAction, InputAction
from core.moves import Relocation, Capture
from core.protocols import Board, ValidMove
from statuses import Status, CAN_BECOME_CORRECT, INVALID, MISSING
import appearance.protocols as proto


@frozen
class MoveReaders:
    _board: Board
    _cell_selector: proto.CellSelector

    @property
    def readers(self) -> list[Callable[[list[InputAction]], ValidMove | Status]]:
        return [
            self._try_read_relocation_move,
            self._try_read_capture_move,
        ]

    def _try_read_relocation_move(self, actions: list[InputAction]) -> ValidMove | Status:
        match actions:
            case [CellClickAction(coord=to_coord,
                                  buttons=Buttons(is_right=True))]:
                if (coord := self._cell_selector.get_coord()) is MISSING:
                    return INVALID

                return Relocation(coord, to_coord).validate(self._board)

            case _:
                return INVALID

    def _try_read_capture_move(self, actions: list[InputAction]) -> ValidMove | Status:
        match actions:
            case [CellClickAction(coord=to_coord,
                                  buttons=Buttons(is_right=True))]:
                if (coord := self._cell_selector.get_coord()) is MISSING:
                    return INVALID

                return Capture(coord, to_coord).validate(self._board)

            case _:
                return INVALID
