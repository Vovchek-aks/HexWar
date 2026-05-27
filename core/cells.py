from types import UnionType
from typing import Iterator

from attrs import frozen, field

import core.protocols as proto


@frozen(order=False)
class Cells(proto.Cells):
    @classmethod
    def empty(cls) -> proto.Cells:
        return cls(set())

    _cells: set[proto.Cell] = field(factory=set)

    @property
    def any(self) -> proto.Cell:
        return next(iter(self._cells))

    def as_set(self) -> set[proto.Cell]:
        return set(self._cells)

    def as_list(self) -> list[proto.Cell]:
        return list(self._cells)

    def without(self, cell: proto.Cell) -> "Cells":
        return Cells(self._cells - {cell})

    def with_owner(self, target: proto.Player) -> "Cells":
        return Cells({cell for cell in self._cells if cell.owner is target})

    def with_figure(self, target: type[proto.Figure] | UnionType) -> "Cells":
        return Cells({cell for cell in self._cells if isinstance(cell.figure, target)})

    def with_flag(self, target: type[proto.Flag] | UnionType) -> "Cells":
        return Cells({cell for cell in self._cells if target in cell.figure.FLAGS})

    def players(self) -> set[proto.Player]:
        players = set[proto.Player]()
        for cell in self:
            players.add(cell.owner)
        return players

    def is_region_with_same_owner(self, board: proto.Board) -> bool:
        assert self

        return board.get_region_with_same_owner(self.any) >= self

    def at_front(self, board: proto.Board) -> "Cells":
        assert self
        player = self.any.owner
        assert self == self.with_owner(player)

        return Cells({cell for cell in self._cells
                      if (neighbors := board.get_neighbors(cell, include_cell=False).with_flag(proto.OnLand)) !=
                      neighbors.with_owner(player)})

    def at_outer_boundry(self, board: proto.Board) -> "Cells":
        neighbors = set[proto.Cell]()
        for cell in self:
            neighbors |= board.get_neighbors(cell).as_set()
        return Cells(neighbors - self._cells)

    def at_inner_boundry(self, board: proto.Board) -> "Cells":
        boundry = set[proto.Cell]()
        for cell in self:
            if board.get_neighbors(cell) - self:
                boundry.add(cell)
        return Cells(boundry)

    def __add__(self, other_cells: "Cells") -> "Cells":
        return Cells(self._cells | other_cells._cells)

    def __sub__(self, other_cells: "Cells") -> "Cells":
        return Cells(self._cells - other_cells._cells)

    def __gt__(self, other_cells: "Cells") -> bool:
        return self._cells > other_cells._cells

    def __ge__(self, other: "Cells") -> bool:
        return self == other or self > other

    def __and__(self, other_cells: "Cells") -> "Cells":
        return Cells(self._cells & other_cells._cells)

    def __bool__(self) -> bool:
        return bool(self._cells)

    def __iter__(self) -> Iterator[proto.Cell]:
        return iter(self._cells)

    def __len__(self) -> int:
        return len(self._cells)

    def __contains__(self, cell: proto.Cell) -> bool:
        return cell in self._cells
