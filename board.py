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
        assert cell in self._cells

        idx = self._cells.index(cell)
        y, x = divmod(idx, self.width)
        return Vector2Int(x, y)

    def make(self, move: proto.ValidMove) -> None:
        move.move.execute(self)

    def get_neighbors(self, cell: proto.Cell, *, include_cell: bool = True) -> set[proto.Cell]:
        assert cell in self._cells

        cell_coord = self.coordinates_of(cell)
        neighbors = {cell} if include_cell else set[proto.Cell]()

        neighbors_coords = [  # https://vk.com/cyberdilf?w=wall-226630281_64
            Vector2Int(-1, -1),
            Vector2Int(-1, 0),
            Vector2Int(0, -1),
            Vector2Int(1, 1),
            Vector2Int(1, 0),
            Vector2Int(0, 1)
        ]
        for delta in neighbors_coords:
            coord = cell_coord + delta
            if self._is_valid_coord(coord):
                neighbors.add(self[coord])

        return neighbors

    def __getitem__(self, coord: Vector2Int) -> proto.Cell:
        assert self._is_valid_coord(coord)

        return self._cells[coord.x + coord.y * self.width]

    def _is_valid_coord(self, coord: Vector2Int) -> bool:
        return (coord.x in range(self.width) and
                coord.y in range(self.height))
