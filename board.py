from itertools import product
from typing import Callable
from attrs import define, field

import protocols as proto


@define
class Board(proto.Board):
    @classmethod
    def from_maker(cls, shape: tuple[int, int], cell_maker: Callable[[int, int], proto.Cell]) -> proto.Board:
        cells = [cell_maker(x, y) for x, y in product(range(shape[0]), range(shape[1]))]
        return Board(shape, cells)

    _shape: tuple[int, int]
    _cells: list[proto.Cell] = field()

    @_cells.validator
    def validate_cells(self, _, cells: list[[proto.Cell]]):
        if len(cells) != self.width * self.height:
            raise ValueError("Cells not fits under given shape")

    @property
    def shape(self):
        return self._shape

    @property
    def width(self) -> int:
        return self._shape[0]

    @property
    def height(self) -> int:
        return self._shape[1]

    def __getitem__(self, item: tuple[int, int]) -> proto.Cell:
        return self._cells[item[0] + item[1] * self.width]
