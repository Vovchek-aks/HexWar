from attrs import frozen, field

import core.protocols as proto
from core.moves import Relocation, Capture, Creation
from observer import Event, OnEventSubscriber


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
        match move.move:  # move move
            case Relocation() | Capture() | Creation():
                self._session.board.make(move)
                self._board_move_was_made.invoke(move)
            case _:
                raise NotImplemented(f"{type(move)}")

        self._move_was_made.invoke(move)
