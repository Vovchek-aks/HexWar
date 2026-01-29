from attrs import frozen, field

import core.protocols as proto
from core.moves.attack import Attack
from core.moves.capture import Capture
from core.moves.pulling import PullingTermination, PullingInitiation
from core.moves.relocations import Relocation, Assault, FiguresRelocation
from core.moves.creation import Creation
from core.moves.conversion import Conversion
from exceptions import NotSupportedMove
from mathematics.vector import Vector2Int
from observer import Event, OnEventSubscriber
from statuses import INVALID


@frozen
class MovesMaker(proto.MovesMaker):
    _session: proto.GameSession

    _move_was_made: Event[proto.ValidMove, None] = field(init=False, factory=Event)
    _board_move_was_made: Event[proto.ValidMove, None] = field(init=False, factory=Event)
    _cell_changed_owner: Event[Vector2Int, None] = field(init=False, factory=Event)

    @property
    def move_was_made(self) -> OnEventSubscriber[proto.ValidMove, None]:
        return self._move_was_made.subscriber

    @property
    def board_move_was_made(self) -> OnEventSubscriber[proto.ValidMove, None]:
        return self._board_move_was_made.subscriber

    @property
    def cell_changed_owner(self) -> OnEventSubscriber[Vector2Int, None]:
        return self._cell_changed_owner.subscriber

    def make(self, move: proto.ValidMove) -> None:
        assert move.move.validate(self._session) is not INVALID

        match move.move:  # move move
            case Assault(to_coord=to_coord, from_coord=from_coord):
                relocation: FiguresRelocation = move.move
                pullable_cell = relocation.pullable_cell(self._session)

                self._session.make(move)
                self._move_was_made.invoke(move)

                self._cell_changed_owner.invoke(to_coord)

                self._board_move_was_made.invoke(move)
                # print(move.move, self._session.board[from_coord], self._session.board[to_coord])
            case Relocation(to_coord=to_coord, from_coord=from_coord):
                relocation: FiguresRelocation = move.move
                pullable_cell = relocation.pullable_cell(self._session)

                self._session.make(move)
                self._move_was_made.invoke(move)
                    
                self._board_move_was_made.invoke(move)
                # print(move.move, self._session.board[from_coord], self._session.board[to_coord])
            case Capture(to_coord=to_coord):
                self._session.make(move)
                self._move_was_made.invoke(move)

                self._cell_changed_owner.invoke(to_coord)
                self._board_move_was_made.invoke(move)
                # print(move.move, self._session.board[move.move.from_coord], self._session.board[to_coord])
            case Creation(to_coord=coord) | Conversion(coord=coord) | Attack(to_coord=coord):
                self._session.make(move)
                self._move_was_made.invoke(move)

                self._board_move_was_made.invoke(move)
                # print(move.move, self._session.board[coord])
            case PullingInitiation() | PullingTermination():
                self._session.make(move)
                self._move_was_made.invoke(move)

                self._board_move_was_made.invoke(move)
            case move:
                raise NotSupportedMove(move)
