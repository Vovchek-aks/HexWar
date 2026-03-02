from attrs import frozen, field

from appearance.input.moves_inputer.actions_reader import InputActionsReader
from appearance.input.moves_inputer.moves_reader import MoveReaders
from appearance.input.moves_inputer.input_actions import InputAction
from core.protocols import ValidMove, GameSession
import appearance.protocols as proto
from observer import Event, OnEventSubscriber
from statuses import CAN_BECOME_CORRECT, ABORT_NEEDED, Status, MISSING


@frozen
class MovesInputer(proto.MovesInputer):
    @classmethod
    def make(cls,
             reader: InputActionsReader,
             multiple_relocations_reader: proto.MultipleRelocationsReader,
             session: GameSession,
             cell_selector: proto.CellSelector) -> "MovesInputer":
        inputer = cls(reader, multiple_relocations_reader, MoveReaders(session, cell_selector))
        reader.action_was_read.subscribe(inputer._on_action_was_read)
        return inputer

    _actions_reader: InputActionsReader
    multiple_relocations_reader: proto.MultipleRelocationsReader
    _move_reader: MoveReaders

    _move_was_raed: Event[ValidMove, None] = field(init=False, factory=Event)

    @property
    def move_was_raed(self) -> OnEventSubscriber[ValidMove, None]:
        return self._move_was_raed.subscriber

    def _on_action_was_read(self, *_: InputAction | bool) -> None:
        last_action: InputAction | Status = MISSING

        while actions := self._actions_reader.actions:
            results = list(map(lambda reader: reader(actions),
                               self._move_reader.readers))

            if ABORT_NEEDED in results:
                self._actions_reader.clear()
                return

            moves = [result for result in results if isinstance(result, ValidMove)]
            assert len(moves) < 2

            if moves:
                move = moves[0]
                self._move_was_raed.invoke(move)
                self._actions_reader.clear()
                return

            if CAN_BECOME_CORRECT in results:
                return

            last_action = self._actions_reader.pop()

        if last_action is MISSING:
            return

        for move in self.multiple_relocations_reader.process(last_action):
            self._move_was_raed.invoke(move)
