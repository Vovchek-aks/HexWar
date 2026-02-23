from collections import defaultdict
from types import UnionType
from typing import get_args, Union

from attrs import frozen, field

import core.protocols as proto
from core.cells import Cells


@frozen
class CellsCache(proto.CellsCache):
    @classmethod
    def make(cls, board: proto.Board) -> "CellsCache":
        self = CellsCache(board)
        for cell in board.cells:
            self.update(cell)
        return self

    _board: proto.Board

    _cells_of: dict[proto.Player, set[proto.Cell]] = field(init=False, factory=lambda: defaultdict(set))
    _cells_with: dict[type[proto.Figure], set[proto.Cell]] = field(init=False, factory=lambda: defaultdict(set))
    _owner_of: dict[proto.Cell, proto.Player] = field(init=False, factory=dict)
    _figure_of: dict[proto.Cell, type[proto.Figure]] = field(init=False, factory=dict)
    _front: set[proto.Cell] = field(init=False, factory=set)

    @property
    def at_front(self) -> Cells:
        return Cells(self._front)

    def with_owner(self, player: proto.Player) -> Cells:
        return Cells(self._cells_of[player])

    def with_figure(self, figure: type[proto.Figure] | UnionType) -> Cells:
        if not isinstance(figure, UnionType):
            return Cells(self._cells_with[figure])

        result = set()
        for concrete_figure in get_args(figure):
            result |= self._cells_with[concrete_figure]
        return Cells(result)

    def update(self, cell: proto.Cell) -> None:
        if not cell.figure.is_on_land():
            return

        self._update_front(cell)

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
