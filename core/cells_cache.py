from collections import defaultdict

from attrs import frozen, field

import core.protocols as proto
from core.cells import Cells


@frozen
class CellsCache(proto.CellsCache):
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

    def with_figure(self, figure: type[proto.Figure]) -> Cells:
        return Cells(self._cells_with[figure])

    def update(self, cell: proto.Cell) -> None:
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

        if cell.owner != old_owner:
            self._cells_of[old_owner].remove(cell)
            self._cells_of[cell.owner].add(cell)

            self._owner_of[cell] = cell.owner

        if figure != old_figure:
            self._cells_with[old_figure].remove(cell)
            self._cells_with[figure].add(cell)

            self._figure_of[cell] = figure

    def _update_front(self, changed_cell: proto.Cell) -> None:
        for cell in self._board.get_neighbors(changed_cell, include_cell=True):
            at_front = any(neighbor.owner is not cell.owner
                           for neighbor in self._board.get_neighbors(cell, include_cell=False))
            if at_front:
                self._front.add(cell)
            else:
                self._front.discard(cell)
