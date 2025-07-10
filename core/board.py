from itertools import product
from typing import Callable, Iterable
from attrs import define, field

import core.protocols as proto
from mathematics import hex_geometry as geo
from mathematics.vector import Vector2Int


@define
class Board(proto.Board):
    @classmethod
    def from_maker(cls, shape: Vector2Int, cell_maker: Callable[[Vector2Int], proto.Cell]) -> proto.Board:
        cells = [cell_maker(Vector2Int(x, y)) for x, y in product(range(shape.x), range(shape.y))]
        return cls(shape, cells)

    _shape: Vector2Int
    _cells: list[proto.Cell] = field()

    @_cells.validator
    def _validate_cells(self, _, cells: list[proto.Cell]) -> None:
        if len(cells) != self.width * self.height:
            raise ValueError(f"Given wrong number of Cells: {len(cells)} != {self.width} * {self.height}")

    @property
    def shape(self) -> Vector2Int:
        return self._shape

    @property
    def width(self) -> int:
        return self._shape.x

    @property
    def height(self) -> int:
        return self._shape.y

    def has_cell(self, cell: proto.Cell) -> bool:
        return cell in self._cells

    def coordinates_of(self, cell: proto.Cell) -> Vector2Int:
        assert self.has_cell(cell)

        idx = self._cells.index(cell)
        y, x = divmod(idx, self.width)
        return Vector2Int(x, y)

    def make(self, move: proto.ValidMove) -> None:
        move.move.execute(self)

    def get_neighbors(self, cell: proto.Cell, *, include_cell: bool = False) -> set[proto.Cell]:
        assert self.has_cell(cell)

        cell_coord = self.coordinates_of(cell)
        neighbors = {cell} if include_cell else set[proto.Cell]()

        for delta in geo.neighbor_square_deltas().values():
            coord = cell_coord + delta
            if coord in self:
                neighbors.add(self[coord])

        return neighbors

    def get_all_coords(self) -> Iterable[Vector2Int]:
        return map(lambda coord: Vector2Int(*coord), product(*map(range, self.shape.tuple)))

    def __getitem__(self, coord: Vector2Int) -> proto.Cell:
        assert coord in self

        return self._cells[coord.x + coord.y * self.width]

    def __contains__(self, coord: Vector2Int) -> bool:
        return (coord.x in range(self.width) and
                coord.y in range(self.height))
