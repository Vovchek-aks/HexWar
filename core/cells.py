from types import UnionType
from typing import Iterable

from attrs import frozen, field

import core.protocols as proto


@frozen
class Cells(proto.Cells):
    @classmethod
    def empty(cls) -> proto.Cells:
        return cls(set())

    _cells: set[proto.Cell] = field(factory=set)

    def all(self) -> set[proto.Cell]:
        return set(self._cells)

    def with_owner(self, target: proto.Player) -> "Cells":
        return Cells({cell for cell in self._cells if cell.owner is target})

    def with_figure(self, target: type[proto.Figure] | UnionType) -> "Cells":
        return Cells({cell for cell in self._cells if isinstance(cell.figure, target)})

    def with_flag(self, target: type[proto.Flag] | UnionType) -> "Cells":
        return Cells({cell for cell in self._cells if target in cell.figure.FLAGS})

    def at_front(self, board: proto.Board) -> "Cells":
        assert self
        player = next(iter(self._cells)).owner
        assert self == self.with_owner(player)

        return Cells({cell for cell in self._cells
                      if (neighbors := board.get_neighbors(cell, include_cell=False).with_flag(proto.OnLand)) !=
                      neighbors.with_owner(player)})

    def __add__(self, other_cells: "Cells") -> "Cells":
        return Cells(self._cells | other_cells._cells)

    def __sub__(self, other_cells: "Cells") -> "Cells":
        return Cells(self._cells - other_cells._cells)

    def __and__(self, other_cells: "Cells") -> "Cells":
        return Cells(self._cells & other_cells._cells)

    def __bool__(self) -> bool:
        return bool(self._cells)

    def __iter__(self) -> Iterable[proto.Cell]:
        return iter(self._cells)

    def __contains__(self, cell: proto.Cell) -> bool:
        return cell in self._cells
