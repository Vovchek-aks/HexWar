from typing import Iterable

from attrs import frozen

import core.protocols as proto


@frozen
class Cells(proto.Cells):
    _cells: list[proto.Cell]

    def all(self) -> list[proto.Cell]:
        return list(self._cells)

    def with_owner(self, target: proto.Player) -> "Cells":
        return Cells([cell for cell in self._cells if cell.owner == target])

    def with_figure(self, target: type[proto.Figure]) -> "Cells":
        return Cells([cell for cell in self._cells if isinstance(cell.figure, target)])

    def __bool__(self) -> bool:
        return bool(self._cells)

    def __iter__(self) -> Iterable[proto.Cell]:
        return iter(self._cells)

    def __contains__(self, cell: proto.Cell) -> bool:
        return cell in self._cells
