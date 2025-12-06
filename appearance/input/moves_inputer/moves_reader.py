from typing import Callable

from attrs import frozen

from appearance.input.clicks_catcher.click import MouseButtons
from appearance.input.moves_inputer.input_actions import CellClickAction, InputAction, CreationButtonPressAction, \
    ConversionButtonPressAction, CaptureButtonPressAction, AttackButtonPressAction, ButtonPressAction
from core.moves.attack import Attack
from core.moves.capture import Capture
from core.moves.conversion import Conversion
from core.moves.relocations import Relocation, Assault
from core.moves.creation import Creation
from core.protocols import ValidMove, GameSession, Move
from statuses import Status, INVALID, MISSING, CAN_BECOME_CORRECT, ABORT_NEEDED
import appearance.protocols as proto


@frozen
class MoveReaders:
    _session: GameSession
    _cell_selector: proto.CellSelector

    @property
    def readers(self) -> list[Callable[[list[InputAction]], ValidMove | Status]]:
        return [
            self._try_read_relocation_move,
            self._try_read_assault_move,
            self._try_read_creation_move,
            self._try_read_conversion_move,
            self._try_read_capture_move,
            self._try_read_attack_move,
        ]

    def _try_read_relocation_move(self, actions: list[InputAction]) -> ValidMove | Status:
        match actions:
            case [CellClickAction(coord=to_coord,
                                  buttons=MouseButtons(is_right=True))]:
                if (coord := self._cell_selector.get_coord()) is MISSING:
                    return INVALID

                return Relocation(coord, to_coord).validate(self._session)

            case _:
                return INVALID

    def _try_read_assault_move(self, actions: list[InputAction]) -> ValidMove | Status:
        match actions:
            case [CellClickAction(coord=to_coord,
                                  buttons=MouseButtons(is_right=True))]:
                if (coord := self._cell_selector.get_coord()) is MISSING:
                    return INVALID

                return Assault(coord, to_coord).validate(self._session)

            case _:
                return INVALID

    def _try_read_creation_move(self, actions: list[InputAction]) -> ValidMove | Status:
        match actions:
            case [CreationButtonPressAction(figure=figure)]:
                if (coord := self._cell_selector.get_coord()) is MISSING:
                    return INVALID

                return Creation(figure, coord).validate(self._session)

            case _:
                return INVALID

    def _try_read_conversion_move(self, actions: list[InputAction]) -> ValidMove | Status:
        match actions:
            case [ConversionButtonPressAction(target=target)]:
                if (coord := self._cell_selector.get_coord()) is MISSING:
                    return INVALID

                return Conversion(coord, target).validate(self._session)

            case _:
                return INVALID

    def _try_read_capture_move(self, actions: list[InputAction]) -> ValidMove | Status:
        return self._try_read_right_click_after(CaptureButtonPressAction, Capture, actions)

    def _try_read_attack_move(self, actions: list[InputAction]) -> ValidMove | Status:
        return self._try_read_right_click_after(AttackButtonPressAction, Attack, actions)

    def _try_read_right_click_after[T: Move](self,
                                             action_type: type[ButtonPressAction],
                                             move_type: type[T],
                                             actions: list[InputAction]) -> ValidMove | Status:
        match actions:
            case [action,
                  CellClickAction(coord=to_coord,
                                  buttons=MouseButtons(is_right=True))]:
                if not isinstance(action, action_type):
                    return INVALID

                if (coord := self._cell_selector.get_coord()) is MISSING:
                    return INVALID

                move = move_type(coord, to_coord).validate(self._session)
                if move is INVALID:
                    return ABORT_NEEDED

                return move

            case [action]:
                if not isinstance(action, action_type):
                    return INVALID

                return CAN_BECOME_CORRECT

            case _:
                return INVALID
