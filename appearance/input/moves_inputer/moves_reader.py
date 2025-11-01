from typing import Callable

from attrs import frozen

from appearance.input.clicks_catcher.click import Buttons
from appearance.input.moves_inputer.input_actions import CellClickAction, InputAction
from core.moves import Relocation, Capture
from core.protocols import Board, ValidMove
from statuses import Status, CAN_BECOME_CORRECT, INVALID


@frozen
class MoveReaders:
    _board: Board

    @property
    def readers(self) -> list[Callable[[list[InputAction]], ValidMove | Status]]:
        return [
            self._try_read_relocation_move,
            self._try_read_capture_move,
        ]

    def _try_read_relocation_move(self, actions: list[InputAction]) -> ValidMove | Status:
        match actions:
            case [CellClickAction(coord=from_coord,
                                  buttons=Buttons(is_left=True)),
                  CellClickAction(coord=to_coord,
                                  buttons=Buttons(is_right=True))]:
                return Relocation(from_coord, to_coord).validate(self._board)

            case [CellClickAction(buttons=Buttons(is_left=True))]:
                return CAN_BECOME_CORRECT

            case _:
                return INVALID

    def _try_read_capture_move(self, actions: list[InputAction]) -> ValidMove | Status:
        match actions:
            case [CellClickAction(coord=from_coord,
                                  buttons=Buttons(is_left=True)),
                  CellClickAction(coord=to_coord,
                                  buttons=Buttons(is_right=True))]:
                return Capture(from_coord, to_coord).validate(self._board)

            case [CellClickAction(buttons=Buttons(is_left=True))]:
                return CAN_BECOME_CORRECT

            case _:
                return INVALID
