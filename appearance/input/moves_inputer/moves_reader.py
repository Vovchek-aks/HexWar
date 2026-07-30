from typing import Callable

from attrs import frozen

from appearance.input.clicks_catcher.click import MouseButtons
from appearance.input.moves_inputer.input_actions import CellClickAction, InputAction, CreationButtonPressAction, \
    ConversionButtonPressAction, CaptureButtonPressAction, AttackButtonPressAction, ButtonPressAction, \
    PullingInitiationButtonPressAction, PullingTerminationButtonPressAction, OreshnikLaunchButtonPressAction, \
    CombinationButtonPressAction, GradAttackButtonPressAction
from core.moves.attack import Attack
from core.moves.capture import Capture
from core.moves.comnination import Combination
from core.moves.conversion import Conversion
from core.moves.grad_attack import GradAttack
from core.moves.oreshnik_launch import OreshnikLaunch
from core.moves.pulling import PullingInitiation, PullingTermination
from core.moves.relocations import Relocation, Assault
from core.moves.creation import Creation
from core.protocols import ValidMove, GameSession, Move
from mathematics.vector import Vector2Int
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
            self._try_read_grad_attack_move,
            self._try_read_combination_move,
            self._try_read_pulling_initiation_move,
            self._try_read_pulling_termination_move,
            self._try_read_oreshnik_launch_move
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

    def _try_read_pulling_termination_move(self, actions: list[InputAction]) -> ValidMove | Status:
        match actions:
            case [PullingTerminationButtonPressAction()]:
                if (coord := self._cell_selector.get_coord()) is MISSING:
                    return INVALID

                return PullingTermination(coord).validate(self._session)

            case _:
                return INVALID

    def _try_read_capture_move(self, actions: list[InputAction]) -> ValidMove | Status:
        return self._try_read_right_click_after(CaptureButtonPressAction, Capture, actions)

    def _try_read_attack_move(self, actions: list[InputAction]) -> ValidMove | Status:
        return self._try_read_right_click_after(AttackButtonPressAction, Attack, actions)

    def _try_read_grad_attack_move(self, actions: list[InputAction]) -> ValidMove | Status:
        return self._try_read_right_click_after(GradAttackButtonPressAction, GradAttack, actions)

    def _try_read_combination_move(self, actions: list[InputAction]) -> ValidMove | Status:
        if not isinstance(actions[0], CombinationButtonPressAction):
            return INVALID
        return self._try_read_right_click_after(CombinationButtonPressAction,
                                                (lambda coord, to_coord: Combination(coord, to_coord,
                                                                                     actions[0].target)),
                                                actions)

    def _try_read_pulling_initiation_move(self, actions: list[InputAction]) -> ValidMove | Status:
        return self._try_read_right_click_after(PullingInitiationButtonPressAction, PullingInitiation, actions)

    def _try_read_oreshnik_launch_move(self, actions: list[InputAction]) -> ValidMove | Status:
        return self._try_read_right_click_after(OreshnikLaunchButtonPressAction, OreshnikLaunch, actions)

    def _try_read_right_click_after[T: Move](self,
                                             action_type: type[ButtonPressAction],
                                             move_maker: type[T] | Callable[[Vector2Int, Vector2Int], T],
                                             actions: list[InputAction]) -> ValidMove | Status:
        match actions:
            case [action,
                  CellClickAction(coord=to_coord,
                                  buttons=MouseButtons(is_right=True))]:
                if not isinstance(action, action_type):
                    return INVALID

                if (coord := self._cell_selector.get_coord()) is MISSING:
                    return INVALID

                move = move_maker(coord, to_coord).validate(self._session)
                if move is INVALID:
                    return ABORT_NEEDED

                return move

            case [action]:
                if not isinstance(action, action_type):
                    return INVALID

                return CAN_BECOME_CORRECT

            case _:
                return INVALID
