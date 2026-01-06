from attrs import frozen, field

import core.protocols as proto
from core.moves.attack import Attack
from core.moves.capture import Capture
from core.moves.relocations import Relocation, Assault
from core.moves.creation import Creation
from core.moves.conversion import Conversion
from mathematics.vector import Vector2Int
from observer import Event, OnEventSubscriber
from statuses import INVALID


@frozen
class MovesMaker(proto.MovesMaker):
    _move_was_made: Event[proto.ValidMove, None] = field(init=False, factory=Event)
    _board_move_was_made: Event[proto.ValidMove, None] = field(init=False, factory=Event)
    _cell_changed_owner: Event[Vector2Int, None] = field(init=False, factory=Event)
    _cell_changed_figure: Event[Vector2Int, None] = field(init=False, factory=Event)

    _session: proto.GameSession

    @property
    def move_was_made(self) -> OnEventSubscriber[proto.ValidMove, None]:
        return self._move_was_made.subscriber

    @property
    def board_move_was_made(self) -> OnEventSubscriber[proto.ValidMove, None]:
        return self._board_move_was_made.subscriber

    @property
    def cell_changed_owner(self) -> OnEventSubscriber[Vector2Int, None]:
        return self._cell_changed_owner.subscriber

    @property
    def cell_changed_figure(self) -> OnEventSubscriber[Vector2Int, None]:
        return self._cell_changed_figure.subscriber

    def make(self, move: proto.ValidMove) -> None:
        assert move.move.validate(self._session) is not INVALID

        self._session.make(move)
        self._move_was_made.invoke(move)

        match move.move:  # move move
            case Assault(to_coord=to_coord, from_coord=from_coord):
                self._cell_changed_owner.invoke(to_coord)
                self._cell_changed_figure.invoke(to_coord)
                self._cell_changed_figure.invoke(from_coord)
                self._board_move_was_made.invoke(move)
            case Capture(to_coord=to_coord):
                self._cell_changed_owner.invoke(to_coord)
                self._board_move_was_made.invoke(move)
            case Creation(to_coord=coord) | Conversion(coord=coord) | Attack(to_coord=coord):
                self._cell_changed_figure.invoke(coord)
                self._board_move_was_made.invoke(move)
            case Relocation(to_coord=to_coord, from_coord=from_coord):
                self._cell_changed_figure.invoke(to_coord)
                self._cell_changed_figure.invoke(from_coord)
                self._board_move_was_made.invoke(move)
