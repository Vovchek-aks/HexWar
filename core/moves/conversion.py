from math import ceil
from typing import ClassVar

from attrs import frozen

import core.protocols as proto
import core.figures.figure as fig
from core.moves.valid_move import ValidMove
from core.resources import Dollars, Resource
from mathematics.vector import Vector2Int
from statuses import Status, INVALID

CONVERSIONS = dict[tuple[type[fig.Figure], type[fig.Figure]], tuple[Resource, int]]


@frozen
class Conversion(proto.Move):
    _conversions: ClassVar[CONVERSIONS] = {
        (fig.Infantry, fig.Motorization): (Dollars(100_000), round(fig.Infantry.MOVES_BUDGET / 3)),
        (fig.Motorization, fig.Infantry): (Dollars(0), round(fig.Motorization.MOVES_BUDGET / 3)),
    }

    @classmethod
    def conversions(cls) -> CONVERSIONS:
        return dict(cls._conversions)

    coord: Vector2Int
    target: type[fig.Figure]

    def validate(self, session: proto.GameSession) -> proto.ValidMove | Status:
        cell = session.board[self.coord]
        player = session.master.current_player

        if cell.owner is not player:
            return INVALID

        if (conversion := (type(cell.figure), self.target)) not in self._conversions:
            return INVALID

        resources_cost, figure_budget_cost = self._conversions[conversion]
        if not player.resources.can_take(resources_cost):
            return INVALID

        figure = cell.figure
        if not session.figures_budget.can_spend(figure, figure_budget_cost):
            return INVALID

        return ValidMove(self)

    def execute(self, session: proto.GameSession) -> None:
        cell = session.board[self.coord]

        old_figure = cell.figure
        session.figures.convert(old_figure, self.target)
        figure = cell.figure

        self._take_resources_and_figures_budget(figure, old_figure, session)

    def _take_resources_and_figures_budget(self,
                                           figure: fig.Figure,
                                           old_figure: fig.Figure,
                                           session: proto.GameSession) -> None:
        budget = session.figures_budget
        resources_cost, figure_budget_cost = self._conversions[type(old_figure), self.target]
        session.figures_budget.add(old_figure, figure_budget_cost)
        old_bill = budget.pop(old_figure)
        bill = ceil(figure.MOVES_BUDGET * (old_bill / old_figure.MOVES_BUDGET))
        if not budget.can_spend(figure, bill):
            bill = figure.MOVES_BUDGET
        budget.add(figure, bill)
        session.master.current_player.resources.take(resources_cost)
