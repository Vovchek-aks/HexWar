from attrs import frozen

import core.protocols as proto
from core.moves.valid_move import ValidMove
from mathematics.vector import Vector2Int
from statuses import Status, INVALID


@frozen
class PullingInitiation(proto.Move):
    pullable_coord: Vector2Int
    puller_coord: Vector2Int

    def validate(self, session: proto.GameSession) -> proto.ValidMove | Status:
        board = session.board
        puller_cell = board[self.puller_coord]
        pullable_cell = board[self.pullable_coord]
        puller = puller_cell.figure
        pullable = pullable_cell.figure

        if puller_cell.owner is not pullable_cell.owner:
            return INVALID

        if puller_cell.owner is not session.master.current_player:
            return INVALID

        if proto.CanPull not in puller.FLAGS:
            return INVALID

        if proto.Pullable not in pullable.FLAGS:
            return INVALID

        if puller_cell not in board.get_neighbors(pullable_cell, include_cell=False):
            return INVALID

        if not session.figures_budget.can_spend(puller, puller.get_cost_of(self)):
            return INVALID

        if not session.figures_budget.can_spend(pullable, pullable.get_cost_of(self)):
            return INVALID

        return ValidMove(self)

    def execute(self, session: proto.GameSession) -> None:
        board = session.board
        puller_cell = board[self.puller_coord]
        pullable_cell = board[self.pullable_coord]
        puller = puller_cell.figure
        pullable = pullable_cell.figure
        budget = session.figures_budget

        session.pulling_connections.register(puller, pullable)
        budget.add(puller, puller.get_cost_of(self))
        budget.add(pullable, pullable.get_cost_of(self))


@frozen
class PullingTermination(proto.Move):
    pullable_coord: Vector2Int

    def validate(self, session: proto.GameSession) -> proto.ValidMove | Status:
        board = session.board
        pullable_cell = board[self.pullable_coord]
        pullable = pullable_cell.figure

        if pullable_cell.owner is not session.master.current_player:
            return INVALID

        if proto.Pullable not in pullable.FLAGS:
            return INVALID

        if not session.pulling_connections.is_pullable(pullable):
            return INVALID

        puller = session.pulling_connections.get_puller(pullable)
        puller_coord = session.figures.locate(puller)
        puller_cell = board[puller_coord]

        assert proto.CanPull in puller.FLAGS
        assert puller_cell.owner is pullable_cell.owner

        if not session.figures_budget.can_spend(puller, puller.get_cost_of(self)):
            return INVALID

        if not session.figures_budget.can_spend(pullable, pullable.get_cost_of(self)):
            return INVALID

        return ValidMove(self)

    def execute(self, session: proto.GameSession) -> None:
        board = session.board
        pullable_cell = board[self.pullable_coord]
        pullable = pullable_cell.figure
        puller = session.pulling_connections.get_puller(pullable)
        budget = session.figures_budget

        session.pulling_connections.unregister(puller, pullable)
        budget.add(puller, puller.get_cost_of(self))
        budget.add(pullable, pullable.get_cost_of(self))
