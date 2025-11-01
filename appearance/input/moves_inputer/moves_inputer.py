from attrs import frozen, field

from appearance.input.clicks_catcher.layers.board_layer import BoardLayer
from appearance.input.moves_inputer.actions_reader import InputActionsReader
from appearance.input.moves_inputer.moves_reader import MoveReaders
from appearance.input.moves_inputer.input_actions import InputAction
from core.protocols import Board, ValidMove
from observer import Event
from observer import ToEventSubscriber
from statuses import CAN_BECOME_CORRECT


@frozen
class MovesInputer:
    @classmethod
    def make(cls, board_layer: BoardLayer, board: Board) -> "MovesInputer":
        reader = InputActionsReader.make(board_layer)
        inputer = cls(reader, MoveReaders(board))
        reader.move_was_raed.subscribe(inputer._on_action_was_read)
        return inputer

    _move_was_raed: Event[ValidMove, None] = field(init=False, factory=Event)

    _actions_reader: "InputActionsReader"
    _move_reader: "MoveReaders"

    @property
    def move_was_raed(self) -> "ToEventSubscriber[ValidMove, None]":
        return self._move_was_raed.subscriber

    def _on_action_was_read(self, _: InputAction) -> None:
        while actions := self._actions_reader.actions:
            results = list(map(lambda reader: reader(actions),
                               self._move_reader.readers))

            moves = [result for result in results if isinstance(result, ValidMove)]
            assert len(moves) < 2

            if moves:
                move = moves[0]
                self._move_was_raed.invoke(move)
                self._actions_reader.clear()
                return

            if CAN_BECOME_CORRECT in results:
                break

            self._actions_reader.pop()
