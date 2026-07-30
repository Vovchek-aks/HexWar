from math import ceil
from typing import ClassVar

from attrs import frozen

import core.protocols as proto
import core.figures.figure as fig
from core.moves.valid_move import ValidMove
from core.resources import ResourcesGroup, HeavyIndustryProducts, LightIndustryProducts
from mathematics.vector import Vector2Int
from statuses import Status, INVALID

COMBINATIONS = dict[tuple[type[fig.Figure], type[fig.Figure], type[fig.Figure]], tuple[ResourcesGroup, int]]


@frozen
class Combination(proto.Move):
    _combinations: ClassVar[COMBINATIONS] = {
        (fig.Tank, fig.Artillery, fig.Howitzer): (ResourcesGroup.make(HeavyIndustryProducts(500)),
                                                  round(fig.Tank.MOVES_BUDGET / 2)),
        (fig.Motorization, fig.Artillery, fig.Grad): (ResourcesGroup.make(LightIndustryProducts(500)),
                                                      round(fig.Motorization.MOVES_BUDGET / 2)),
    }

    @classmethod
    def combinations(cls) -> COMBINATIONS:
        return dict(cls._combinations)

    first_coord: Vector2Int
    second_coord: Vector2Int
    target: type[fig.Figure]

    def validate(self, session: proto.GameSession) -> proto.ValidMove | Status:
        board = session.board
        first_cell = board[self.first_coord]
        second_cell = board[self.second_coord]
        player = session.master.current_player

        if first_cell.owner is not player:
            return INVALID

        if second_cell.owner is not player:
            return INVALID

        if second_cell not in board.get_neighbors(first_cell, include_cell=False):
            return INVALID

        if (combination := (type(first_cell.figure), type(second_cell.figure), self.target)) not in self._combinations:
            return INVALID

        resources_cost, figure_budget_cost = self._combinations[combination]
        if not player.resources.can_take(resources_cost):
            return INVALID

        figure = first_cell.figure
        if not session.figures_budget.can_spend(figure, figure_budget_cost):
            return INVALID

        return ValidMove(self)

    def execute(self, session: proto.GameSession) -> None:
        first_cell = session.board[self.first_coord]
        second_cell = session.board[self.second_coord]

        old_figure = first_cell.figure
        session.figures.convert(old_figure, self.target)
        figure = first_cell.figure

        self._take_resources_and_figures_budget(figure, old_figure, second_cell.figure, session)
        session.figures.remove(second_cell.figure)

    def _take_resources_and_figures_budget(self,
                                           figure: fig.Figure,
                                           old_figure: fig.Figure,
                                           second_figure: fig.Figure,
                                           session: proto.GameSession) -> None:
        budget = session.figures_budget
        resources_cost, figure_budget_cost = self._combinations[type(old_figure), type(second_figure), self.target]
        session.figures_budget.add(old_figure, figure_budget_cost)
        old_bill = budget.pop(old_figure)
        bill = ceil(figure.MOVES_BUDGET * (old_bill / old_figure.MOVES_BUDGET))
        if not budget.can_spend(figure, bill):
            bill = figure.MOVES_BUDGET
        budget.add(figure, bill)
        session.master.current_player.resources.take(resources_cost)
