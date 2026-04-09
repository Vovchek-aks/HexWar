from abc import ABCMeta

from attrs import frozen

from core.figures.figures_flags import CanPull
from core.figures.movable_flag import Movable
import core.protocols as proto
from core.moves.valid_move import ValidMove
from mathematics.vector import Vector2Int
from statuses import Status, INVALID, MISSING


@frozen
class FiguresRelocation(proto.Move, metaclass=ABCMeta):
    @classmethod
    def make(cls, from_coord: Vector2Int, to_coord: Vector2Int) -> "FiguresRelocation":
        return cls(from_coord, to_coord)

    from_coord: Vector2Int
    to_coord: Vector2Int

    def pullable_cell(self, session: proto.GameSession) -> proto.Cell | Status:
        figure = session.board[self.from_coord].figure
        if CanPull in figure.FLAGS and session.pulling_connections.is_puller(figure):
            pullable = session.pulling_connections.get_pullable(figure)
            pullable_cell = session.board[session.figures.locate(pullable)]
            assert pullable_cell is not MISSING
            return pullable_cell
        return MISSING

    def execute(self, session: proto.GameSession) -> None:
        board = session.board
        from_cell = board[self.from_coord]
        to_cell = board[self.to_coord]
        pullable_cell = self.pullable_cell(session)
        figure = from_cell.figure

        session.figures_budget.add(figure, figure.get_cost_of(self))
        if not to_cell.is_empty:
            session.figures.remove(to_cell.figure)
        session.figures.move(figure, self.to_coord)

        if pullable_cell is not MISSING:
            pullable = pullable_cell.figure
            session.figures_budget.add(pullable, pullable.get_cost_of(Relocation(self.from_coord, self.to_coord)))
            session.figures.move(pullable, self.from_coord)


@frozen
class Assault(FiguresRelocation):
    def validate(self, session: proto.GameSession) -> proto.ValidMove | Status:
        board = session.board
        from_cell = board[self.from_coord]
        to_cell = board[self.to_coord]
        figure = from_cell.figure

        if from_cell.owner is not session.master.current_player:
            return INVALID

        if from_cell.owner is to_cell.owner:
            return INVALID

        if to_cell.figure.is_on_land() != from_cell.figure.is_on_land():
            return INVALID

        if not board.get_neighbors(to_cell, include_cell=False).with_owner(from_cell.owner):
            return INVALID

        if (movable := from_cell.figure.FLAGS.get(Movable)) is MISSING:
            return INVALID

        if not movable.can_relocate(self.from_coord, self.to_coord, board):
            return INVALID

        if from_cell.strength(board) <= to_cell.hardness(board):
            return INVALID

        if not session.figures_budget.can_spend(figure, figure.get_cost_of(self)):
            return INVALID

        if CanPull in figure.FLAGS and session.pulling_connections.is_puller(figure):
            pullable = session.pulling_connections.get_pullable(figure)
            if not session.figures_budget.can_spend(pullable,
                                                    pullable.get_cost_of(Relocation(self.from_coord, self.to_coord))):
                return INVALID

        return ValidMove(self)


@frozen
class Relocation(FiguresRelocation):
    def validate(self, session: proto.GameSession) -> proto.ValidMove | Status:
        board = session.board
        from_cell = board[self.from_coord]
        to_cell = board[self.to_coord]
        figure = from_cell.figure

        if from_cell.owner is not session.master.current_player:
            return INVALID

        if from_cell.owner is not to_cell.owner:
            return INVALID

        if not to_cell.is_empty:
            return INVALID

        if to_cell.figure.is_on_land() != from_cell.figure.is_on_land():
            return INVALID

        if not board.get_neighbors(to_cell, include_cell=False).with_owner(from_cell.owner):
            return INVALID

        if (movable := from_cell.figure.FLAGS.get(Movable)) is MISSING:
            return INVALID

        if not movable.can_relocate(self.from_coord, self.to_coord, board):
            return INVALID

        if not session.figures_budget.can_spend(figure, figure.get_cost_of(self)):
            return INVALID

        if CanPull in figure.FLAGS and session.pulling_connections.is_puller(figure):
            pullable = session.pulling_connections.get_pullable(figure)
            if not session.figures_budget.can_spend(pullable,
                                                    pullable.get_cost_of(Relocation(self.from_coord, self.to_coord))):
                return INVALID

        return ValidMove(self)
