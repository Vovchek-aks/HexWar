from math import ceil
from typing import ClassVar

from attrs import frozen

import core.protocols as proto
import core.figures.figures as fig
from core.moves.valid_move import ValidMove
from core.resources import Dollars, Resource
from mathematics.vector import Vector2Int
from statuses import Status, INVALID


@frozen
class Conversion(proto.Move):
    _CONVERSIONS: ClassVar[dict[tuple[type[fig.Figure], type[fig.Figure]], tuple[Resource, int]]] = {
        (fig.Infantry, fig.Motorization): (Dollars(100_000), 1),
        (fig.Motorization, fig.Infantry): (Dollars(0), 10),
    }

    coord: Vector2Int
    target: type[fig.Figure]

    def validate(self, session: proto.GameSession) -> proto.ValidMove | Status:
        cell = session.board[self.coord]
        player = session.master.current_player

        if cell.owner is not player:
            return INVALID

        if (conversion := (type(cell.figure), self.target)) not in self._CONVERSIONS:
            return INVALID

        resources_cost, figure_budget_cost = self._CONVERSIONS[conversion]
        if not player.resources.can_take(resources_cost):
            return INVALID

        figure = cell.figure
        if not session.figures_budget.can_spend(figure, figure_budget_cost):
            return INVALID

        return ValidMove(self)

    def execute(self, session: proto.GameSession) -> None:
        cell = session.board[self.coord]
        figure = self.target()
        budget = session.figures_budget

        old_figure = cell.pop()
        resources_cost, figure_budget_cost = self._CONVERSIONS[type(old_figure), self.target]
        session.figures_budget.add(old_figure, figure_budget_cost)
        old_bill = budget.pop(old_figure)

        bill = ceil(figure.MOVES_BUDGET * (old_bill / old_figure.MOVES_BUDGET))
        if not budget.can_spend(figure, bill):
            bill = figure.MOVES_BUDGET

        cell.insert(figure)
        budget.add(figure, bill)

        session.master.current_player.resources.take(resources_cost)
