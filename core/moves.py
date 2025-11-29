from abc import ABCMeta

from attrs import frozen

from core.figures.movable_flag import Movable
import core.protocols as proto
import core.figures as fig
from core.protocols import Creatable
from mathematics.vector import Vector2Int
from statuses import Status, INVALID, MISSING


@frozen
class ValidMove(proto.ValidMove):
    _move: proto.Move

    @property
    def move(self) -> proto.Move:
        return self._move


@frozen
class _FiguresRelocation(proto.Move, metaclass=ABCMeta):
    from_coord: Vector2Int
    to_coord: Vector2Int

    def execute(self, session: proto.GameSession) -> None:
        board = session.board
        from_cell = board[self.from_coord]
        to_cell = board[self.to_coord]
        figure = from_cell.figure

        session.figures_budget.add(figure, figure.get_cost_of(self, board))
        to_cell.take_from(from_cell)


@frozen
class Capture(_FiguresRelocation):
    def validate(self, session: proto.GameSession) -> proto.ValidMove | Status:
        board = session.board
        from_cell = board[self.from_coord]
        to_cell = board[self.to_coord]
        figure = from_cell.figure

        if from_cell.owner is not session.master.current_player:
            return INVALID

        if from_cell.owner is to_cell.owner:
            return INVALID

        if not board.get_neighbors(to_cell, include_cell=False).with_owner(from_cell.owner):
            return INVALID

        if (movable := from_cell.figure.FLAGS.get(Movable)) is MISSING:
            return INVALID

        if not movable.can_relocate(self.from_coord, self.to_coord, board):
            return INVALID

        if from_cell.strength(board) <= to_cell.hardness(board):
            return INVALID

        if not session.figures_budget.can_spend(figure, figure.get_cost_of(self, session.board)):
            return INVALID

        return ValidMove(self)


@frozen
class Relocation(_FiguresRelocation):
    def validate(self, session: proto.GameSession) -> proto.ValidMove | Status:
        board = session.board
        from_cell = board[self.from_coord]
        to_cell = board[self.to_coord]
        figure = from_cell.figure

        if from_cell.owner is not session.master.current_player:
            return INVALID

        if from_cell.owner is not to_cell.owner:
            return INVALID

        if not isinstance(to_cell.figure, fig.Empty):
            return INVALID

        if (movable := from_cell.figure.FLAGS.get(Movable)) is MISSING:
            return INVALID

        if not movable.can_relocate(self.from_coord, self.to_coord, board):
            return INVALID

        if not session.figures_budget.can_spend(figure, figure.get_cost_of(self, session.board)):
            return INVALID

        return ValidMove(self)


@frozen
class Creation(proto.Move):
    figure_type: type[proto.Figure]
    to_coord: Vector2Int

    def validate(self, session: proto.GameSession) -> proto.ValidMove | Status:
        board = session.board
        to_cell = board[self.to_coord]

        if to_cell.owner is not session.master.current_player:
            return INVALID

        if not to_cell.is_empty:
            return INVALID

        if (creatable := self.figure_type.FLAGS.get(Creatable)) is MISSING:
            return INVALID

        if not session.master.current_player.resources.can_take(creatable.cost):
            return INVALID

        return ValidMove(self)

    def execute(self, session: proto.GameSession) -> None:
        board = session.board
        figure = self.figure_type()

        board[self.to_coord].insert(figure)

        session.master.current_player.resources.take(figure.FLAGS.get(Creatable).cost)
