from attrs import frozen

import core.protocols as proto
from core.figures.figures_flags import PreventsCaptures
from core.moves.valid_move import ValidMove
from mathematics.vector import Vector2Int
from statuses import Status, INVALID


@frozen
class Capture(proto.Move):
    from_coord: Vector2Int
    to_coord: Vector2Int

    def validate(self, session: proto.GameSession) -> proto.ValidMove | Status:
        board = session.board
        to_cell = board[self.to_coord]
        from_cell = board[self.from_coord]
        figure = from_cell.figure

        if from_cell.owner is not session.master.current_player:
            return INVALID

        if from_cell.owner is to_cell.owner:
            return INVALID

        if proto.CanCapture not in figure.FLAGS:
            return INVALID

        if proto.Capturable not in to_cell.figure.FLAGS:
            return INVALID

        if from_cell not in (neighbors := board.get_neighbors(to_cell, include_cell=False).with_flag(proto.OnLand)):
            return INVALID

        if neighbors.with_owner(to_cell.owner).with_flag(PreventsCaptures):
            return INVALID

        if not session.figures_budget.can_spend(figure, figure.get_cost_of(self)):
            return INVALID

        return ValidMove(self)

    def execute(self, session: proto.GameSession) -> None:
        board = session.board
        to_cell = board[self.to_coord]
        from_cell = board[self.from_coord]
        figure = from_cell.figure
        budget = session.figures_budget

        to_cell.change_owner_to(from_cell.owner)
        budget.add(figure, figure.get_cost_of(self))
