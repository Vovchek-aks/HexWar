import random

from attrs import frozen

import core.protocols as proto
from core.cells import Cells
from core.distant_neighbors_getter import DistantNeighborsGetter
from core.moves.valid_move import ValidMove
from mathematics.vector import Vector2Int
from my_random import temporarily_seed
from statuses import Status, INVALID, MISSING


@frozen
class GradAttack(proto.Move):
    from_coord: Vector2Int
    to_coord: Vector2Int

    def get_target_cells(self, session: proto.GameSession) -> Cells:
        board = session.board
        attacker = board[self.from_coord].figure.FLAGS.get(proto.CanGradAttack)
        with temporarily_seed(str(self.to_coord)):
            return Cells(random.sample(board.get_neighbors(board[self.to_coord],
                                                           include_cell=attacker.is_attacking_center).as_list(),
                                       attacker.targets_count)
                         ).filter(lambda cell: proto.CannotBeDestroyed not in cell.figure.FLAGS)

    def validate(self, session: proto.GameSession) -> proto.ValidMove | Status:
        board = session.board
        to_cell = board[self.to_coord]
        from_cell = board[self.from_coord]
        figure = from_cell.figure

        if from_cell.owner is not session.master.current_player:
            return INVALID

        if from_cell.owner is to_cell.owner:
            return INVALID

        if not to_cell.figure.is_on_land():
            return INVALID

        if (attacker := figure.FLAGS.get(proto.CanGradAttack)) is MISSING:
            return INVALID

        if figure.FLAGS.get(proto.WithRestrictedTerrainKinds).contains_in(from_cell, board=board):
            return INVALID

        if from_cell not in (DistantNeighborsGetter(to_cell, board)
                .get_all_not_farther_than(attacker.max_distance, include_cell=False)):
            return INVALID

        if not session.figures_budget.can_spend(figure, figure.get_cost_of(self)):
            return INVALID

        if not session.master.current_player.resources.can_take(attacker.cost):
            return INVALID

        return ValidMove(self)

    def execute(self, session: proto.GameSession) -> None:
        board = session.board
        from_cell = board[self.from_coord]
        figure = from_cell.figure
        attacker = board[self.from_coord].figure.FLAGS.get(proto.CanGradAttack)
        assert attacker is not MISSING

        for target in self.get_target_cells(session):
            if proto.Empty in target.figure.FLAGS:
                continue

            session.figures.remove(target.figure)

        session.figures_budget.add(figure, figure.get_cost_of(self))
        session.master.current_player.resources.take(attacker.cost)
