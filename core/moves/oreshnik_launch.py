import random

from attrs import frozen

import core.protocols as proto
from core.cells import Cells
from core.distant_neighbors_getter import DistantNeighborsGetter
from core.moves.valid_move import ValidMove
from mathematics.vector import Vector2Int
from statuses import Status, INVALID, MISSING


@frozen
class OreshnikLaunch(proto.Move):
    from_coord: Vector2Int
    to_coord: Vector2Int

    def get_target_cells(self, session: proto.GameSession) -> Cells:
        board = session.board
        launcher = board[self.from_coord].figure.FLAGS.get(proto.CanLaunchOreshnik)
        random_state = random.getstate()
        random.seed(str(self.to_coord.tuple))

        targets = {board[self.to_coord]}
        for distance in range(1, launcher.spread_radius):
            layer = DistantNeighborsGetter(board[self.to_coord], board).get_as_far_as(distance)
            targets.update(random.sample(list(layer.as_set()), min(len(layer.as_set()), launcher.targets_per_layer)))

        random.setstate(random_state)
        return Cells(targets)

    def validate(self, session: proto.GameSession) -> proto.ValidMove | Status:
        board = session.board
        to_cell = board[self.to_coord]
        from_cell = board[self.from_coord]
        figure = from_cell.figure

        if from_cell.owner is not session.master.current_player:
            return INVALID

        if from_cell.owner is to_cell.owner:
            return INVALID

        if (launcher := figure.FLAGS.get(proto.CanLaunchOreshnik)) is MISSING:
            return INVALID

        if from_cell in (DistantNeighborsGetter(to_cell, board)
                .get_all_not_farther_than(launcher.min_distance, include_cell=False)):
            return INVALID

        if not session.figures_budget.can_spend(figure, figure.get_cost_of(self)):
            return INVALID

        if not session.master.current_player.resources.can_take(launcher.cost):
            return INVALID

        return ValidMove(self)

    def execute(self, session: proto.GameSession) -> None:
        board = session.board
        from_cell = board[self.from_coord]
        figure = from_cell.figure
        launcher = board[self.from_coord].figure.FLAGS.get(proto.CanLaunchOreshnik)

        for target in self.get_target_cells(session):
            if proto.Empty in target.figure.FLAGS:
                continue

            session.figures.remove(target.figure)

        session.figures_budget.add(figure, figure.get_cost_of(self))
        session.master.current_player.resources.take(launcher.cost)
