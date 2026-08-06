from attrs import frozen

import core.protocols as proto
from core.moves.valid_move import ValidMove
from core.protocols import Creatable
from mathematics.vector import Vector2Int
from statuses import Status, INVALID, MISSING


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

        if to_cell.figure.is_on_land() != self.figure_type.is_on_land():
            return INVALID

        if (creatable := self.figure_type.FLAGS.get(Creatable)) is MISSING:
            return INVALID

        if creatable.necessary_neighbor is not MISSING:
            creators = board.get_neighbors(to_cell).with_figure(creatable.necessary_neighbor)
            if not creators.filter(lambda creator:
                                   session.figures_budget.can_spend(creator.figure, creator.figure.get_cost_of(self))):
                return INVALID

        if self.figure_type.FLAGS.get(proto.WithRestrictedTerrainKinds).contains_in(to_cell, board=board):
            return INVALID

        if not session.master.current_player.resources.can_take(creatable.cost):
            return INVALID

        return ValidMove(self)

    def execute(self, session: proto.GameSession) -> None:
        board = session.board
        to_cell = board[self.to_coord]

        session.figures.add(self.figure_type, self.to_coord)
        figure = to_cell.figure
        if (spend_budget := figure.FLAGS.get(proto.StartsWithBudgetSpend)) is not MISSING:
            session.figures_budget.add(figure, spend_budget.amount)

        session.master.current_player.resources.take(figure.FLAGS.get(Creatable).cost)

        creatable = self.figure_type.FLAGS.get(proto.Creatable)
        if creatable.necessary_neighbor is MISSING:
            return

        creator = (board
                   .get_neighbors(to_cell)
                   .with_figure(creatable.necessary_neighbor)
                   .filter(lambda cell: session.figures_budget.can_spend(cell.figure, cell.figure.get_cost_of(self)))
                   .any.figure)
        session.figures_budget.add(creator, creator.get_cost_of(self))
