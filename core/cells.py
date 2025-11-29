from types import UnionType
from typing import Iterable

from attrs import frozen, field

import core.protocols as proto


@frozen
class Cells(proto.Cells):
    _cells: list[proto.Cell] = field(factory=list)

    def all(self) -> list[proto.Cell]:
        return list(self._cells)

    def with_owner(self, target: proto.Player) -> "Cells":
        return Cells([cell for cell in self._cells if cell.owner == target])

    def with_figure(self, target: type[proto.Figure] | UnionType) -> "Cells":
        return Cells([cell for cell in self._cells if isinstance(cell.figure, target)])

    def with_flag(self, target: type[proto.Flag] | UnionType) -> "Cells":
        return Cells([cell for cell in self._cells if target in cell.figure.FLAGS])

    def __add__(self, other_cells: "Cells") -> "Cells":
        our = [cell for cell in self if cell not in other_cells]
        other = [cell for cell in other_cells if cell not in self]
        common = [cell for cell in other_cells if cell in self]

        return Cells(our + other + common)

    def __bool__(self) -> bool:
        return bool(self._cells)

    def __iter__(self) -> Iterable[proto.Cell]:
        return iter(self._cells)

    def __contains__(self, cell: proto.Cell) -> bool:
        return cell in self._cells
