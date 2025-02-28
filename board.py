from itertools import product
from typing import Callable
from attrs import define, field

import protocols as proto
from vector import Vector2Int


@define
class Board(proto.Board):
    @classmethod
    def from_maker(cls, shape: Vector2Int, cell_maker: Callable[[Vector2Int], proto.Cell]) -> proto.Board:
        cells = [cell_maker(Vector2Int(x, y)) for x, y in product(range(shape.x), range(shape.y))]
        return cls(shape, cells)

    _shape: Vector2Int
    _cells: list[proto.Cell] = field()

    @_cells.validator
    def validate_cells(self, _, cells: list[proto.Cell]) -> None:
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

    def coordinates_of(self, cell: proto.Cell) -> Vector2Int:
        idx = self._cells.index(cell)
        y, x = divmod(idx, self.width)
        return Vector2Int(x, y)

    def __getitem__(self, item: tuple[int, int]) -> proto.Cell:
        return self._cells[item[0] + item[1] * self.width]
