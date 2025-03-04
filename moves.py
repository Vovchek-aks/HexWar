from attrs import frozen

import protocols as proto
import figures as fig
from vector import Vector2Int


@frozen
class ValidMove(proto.ValidMove):
    _move: proto.Move

    @property
    def move(self) -> proto.Move:
        return self._move


@frozen
class Relocation(proto.Move):
    from_coord: Vector2Int
    to_coord: Vector2Int

    def validate(self, master: proto.Master, board: proto.Board) -> proto.ValidMove | None:
        from_cell = board[self.from_coord]
        to_cell = board[self.to_coord]

        if not master.is_turn_of(from_cell.owner):
            return None

        if not isinstance(movable := from_cell.figure, proto.MovableFigure):
            return None

        if movable.STRENGTH == fig.MAX_STRENGTH:
            return ValidMove(self)

        if movable.STRENGTH <= to_cell.strength:
            return None

        return ValidMove(self)

    def execute(self, board: proto.Board) -> None:
        from_cell = board[self.from_coord]
        to_cell = board[self.to_coord]
        from_cell.take_from(to_cell)
