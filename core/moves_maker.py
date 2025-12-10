from attrs import frozen, field

import core.protocols as proto
from core.moves.attack import Attack
from core.moves.capture import Capture
from core.moves.relocations import Relocation, Assault
from core.moves.creation import Creation
from core.moves.conversion import Conversion
from exceptions import NotImplementedMove
from observer import Event, OnEventSubscriber
from statuses import INVALID


@frozen
class MovesMaker(proto.MovesMaker):
    _move_was_made: Event[proto.ValidMove, None] = field(init=False, factory=Event)
    _board_move_was_made: Event[proto.ValidMove, None] = field(init=False, factory=Event)

    _session: proto.GameSession

    @property
    def move_was_made(self) -> OnEventSubscriber[proto.ValidMove, None]:
        return self._move_was_made.subscriber

    @property
    def board_move_was_made(self) -> OnEventSubscriber[proto.ValidMove, None]:
        return self._board_move_was_made.subscriber

    def make(self, move: proto.ValidMove) -> None:
        assert move.move.validate(self._session) is not INVALID

        match move.move:  # move move
            case Relocation() | Assault() | Creation() | Conversion() | Capture() | Attack():
                self._session.make(move)
                self._board_move_was_made.invoke(move)
            case _:
                raise NotImplementedMove(move.move)

        self._move_was_made.invoke(move)
