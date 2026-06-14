from collections import defaultdict
from functools import reduce
from types import UnionType
from typing import get_args

from attrs import frozen, field

import core.protocols as proto
from core.cells import Cells
from core.distant_neighbors_getter import DistantNeighborsGetter
from my_types import union
from statuses import MISSING
import core.figures.figure as fig

@frozen
class CellsCache(proto.CellsCache):
    @classmethod
    def make(cls, board: proto.Board) -> "CellsCache":
        self = CellsCache(board)
        self.update_fully()
        return self

    _board: proto.Board

    _cells_of: dict[proto.Player, set[proto.Cell]] = field(init=False, factory=lambda: defaultdict(set))
    _cells_with: dict[type[proto.Figure], set[proto.Cell]] = field(init=False, factory=lambda: defaultdict(set))
    _owner_of: dict[proto.Cell, proto.Player] = field(init=False, factory=dict)
    _figure_of: dict[proto.Cell, type[proto.Figure]] = field(init=False, factory=dict)
    _front: set[proto.Cell] = field(init=False, factory=set)
    _control_zone_of: dict[proto.Cell, Cells] = field(init=False, factory=dict)

    @property
    def at_front(self) -> Cells:
        return Cells(self._front)

    def get_static_control_zone_of(self, cell: proto.Cell) -> Cells:
        flag = cell.figure.FLAGS.get(proto.PreventsAnnexations)
        assert flag is not MISSING
        return self._control_zone_of[cell]

    def not_empty(self) -> Cells:
        result = set()
        for figure, cells in self._cells_with.items():
            if figure.FLAGS.get(proto.Empty) is MISSING:
                result |= cells
        return Cells(result)

    def with_owner(self, player: proto.Player) -> Cells:
        return Cells(self._cells_of[player])

    def with_figure(self, figure: type[proto.Figure] | UnionType) -> Cells:
        if not isinstance(figure, UnionType):
            return Cells(self._cells_with[figure])

        result = set()
        for concrete_figure in get_args(figure):
            result |= self._cells_with[concrete_figure]
        return Cells(result)

    def get_all_players(self) -> Cells:
        return reduce(lambda a, b: a + b, (self.with_owner(player) for player in self._cells_of))

    def get_territories_and_production_ratios_of(self, player: proto.Player) -> tuple[float, float]:
        production = self.with_figure(union(*fig.get_producers()))
        player_cells = self.with_owner(player)
        player_production = player_cells & production
        return (len(player_cells) / sum(len(self.with_owner(other))
                                        for other in self._cells_of),
                0 if not production else len(player_production) / len(production))

    def update_fully(self) -> None:
        for cell in self._board.cells:
            self.update(cell)

    def update(self, cell: proto.Cell) -> None:
        if not cell.figure.is_on_land():
            return

        self._update_front(cell)
        self._update_control_zones(cell)

        figure = type(cell.figure)
        if cell not in self._owner_of:
            self._cells_of[cell.owner].add(cell)
            self._owner_of[cell] = cell.owner

            self._cells_with[figure].add(cell)
            self._figure_of[cell] = figure
            return

        old_owner = self._owner_of[cell]
        old_figure = self._figure_of[cell]

        if cell.owner is not old_owner:
            self._cells_of[old_owner].remove(cell)
            self._cells_of[cell.owner].add(cell)

            self._owner_of[cell] = cell.owner

        if figure is not old_figure:
            self._cells_with[old_figure].remove(cell)
            self._cells_with[figure].add(cell)

            self._figure_of[cell] = figure

    def _update_control_zones(self, cell: proto.Cell) -> None:
        if proto.Static not in cell.figure.FLAGS:
            return

        flag = cell.figure.FLAGS.get(proto.PreventsAnnexations)
        if flag is MISSING and cell in self._control_zone_of:
            self._control_zone_of.pop(cell)
            return

        if flag is not MISSING:
            assert flag.can_prevent(..., ..., ...)
            self._control_zone_of[cell] = (DistantNeighborsGetter(cell, self._board)
                                           .get_all_not_farther_than(flag.distance, include_cell=True))

    def _update_front(self, changed_cell: proto.Cell) -> None:
        for cell in self._board.get_neighbors(changed_cell, include_cell=True).with_flag(proto.OnLand):
            at_front = any(neighbor.owner is not cell.owner
                           for neighbor in self._board
                           .get_neighbors(cell, include_cell=False)
                           .with_flag(proto.OnLand))
            if at_front:
                self._front.add(cell)
            else:
                self._front.discard(cell)
