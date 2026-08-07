from attrs import frozen

import core.protocols as proto
from core.distant_neighbors_getter import DistantNeighborsGetter
from core.moves.valid_move import ValidMove
from mathematics.vector import Vector2Int
from statuses import Status, INVALID, MISSING


@frozen
class Attack(proto.Move):
    from_coord: Vector2Int
    to_coord: Vector2Int

    def validate(self, session: proto.GameSession) -> proto.ValidMove | Status:
        board = session.board
        to_cell = board[self.to_coord]
        from_cell = board[self.from_coord]
        figure = from_cell.figure

        if from_cell.owner is not session.master.current_player:
            return INVALID

        if to_cell.is_empty:
            return INVALID

        if proto.CannotBeDestroyed in to_cell.figure.FLAGS:
            return INVALID

        if (can_attack := figure.FLAGS.get(proto.CanAttack)) is MISSING:
            return INVALID

        if figure.FLAGS.get(proto.WithRestrictedTerrainKinds).contains_in(from_cell, board=board):
            return INVALID

        if from_cell not in (DistantNeighborsGetter(to_cell, board)
                .get_all_not_farther_than(can_attack.max_distance, include_cell=False)):
            return INVALID

        if from_cell.strength(board) < to_cell.hardness(board):
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

        session.figures.remove(to_cell.figure)
        budget.add(figure, figure.get_cost_of(self))
