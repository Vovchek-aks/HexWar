from itertools import product
from typing import Callable, Iterable
from attrs import frozen, field

import core.protocols as proto
from core.cells import Cells
from mathematics import hex_geometry as geo
from mathematics.vector import Vector2Int

CELL_MAKER = Callable[[Vector2Int], proto.Cell]


@frozen
class Board(proto.Board):
    @classmethod
    def from_maker(cls, shape: Vector2Int, cell_maker: CELL_MAKER) -> proto.Board:
        cells = [cell_maker(coord) for coord in cls.get_cell_coords(shape)]
        index_of = {cell: index for index, cell in enumerate(cells)}
        return cls(shape, cells, set(cells), index_of)

    @staticmethod
    def get_cell_coords(shape: Vector2Int) -> Iterable[Vector2Int]:
        return map(lambda coord: Vector2Int(coord[1], coord[0]), product(*map(range, shape.tuple[::-1])))

    shape: Vector2Int
    _cells: list[proto.Cell] = field()
    _cells_set: set[proto.Cell]
    _index_of: dict[proto.Cell, int]

    @_cells.validator
    def _validate_cells(self, _, cells: list[proto.Cell]) -> None:
        if len(cells) != self.width * self.height:
            raise ValueError(f"Given wrong number of Cells: {len(cells)} != {self.width} * {self.height}")

    @property
    def width(self) -> int:
        return self.shape.x

    @property
    def height(self) -> int:
        return self.shape.y

    @property
    def cells(self) -> Cells:
        return Cells(set(self._cells))

    @property
    def cell_coords(self) -> Iterable[Vector2Int]:
        return self.get_cell_coords(self.shape)

    def has(self, cell: proto.Cell) -> bool:
        return cell in self._cells_set

    def is_on_boundry(self, cell: proto.Cell) -> bool:
        coord = self.coordinates_of(cell)
        return any((
            coord.x == 0,
            coord.x == self.shape.x - 1,
            coord.y == 0,
            coord.y == self.shape.y - 1
        ))

    def coordinates_of(self, cell: proto.Cell) -> Vector2Int:
        assert self.has(cell)

        idx = self._index_of[cell]
        y, x = divmod(idx, self.width)
        return Vector2Int(x, y)

    def get_neighbors(self, cell: proto.Cell, *, include_cell: bool = False) -> proto.Cells:
        assert self.has(cell)

        cell_coord = self.coordinates_of(cell)
        neighbors = {cell} if include_cell else set[proto.Cell]()

        for delta in geo.neighbor_square_deltas().values():
            coord = cell_coord + delta
            if coord in self:
                neighbors.add(self[coord])

        return Cells(neighbors)

    def get_region_with_same_owner(self, cell: proto.Cell) -> Cells:
        owner = cell.owner

        def _get_region_with_same_owner(cell: proto.Cell, seen: "set[proto.Cell]") -> Cells:
            if cell.owner is not owner or cell in seen:
                return Cells.empty()

            seen.add(cell)

            for neighbor in self.get_neighbors(cell) - Cells(seen):
                _get_region_with_same_owner(neighbor, seen)

            return Cells(seen)

        return _get_region_with_same_owner(cell, set())

    def at(self, coord: Vector2Int) -> proto.Cell:
        return self[coord]

    def __getitem__(self, coord: Vector2Int) -> proto.Cell:
        assert coord in self

        return self._cells[coord.x + coord.y * self.width]

    def __iter__(self) -> Iterable[Vector2Int]:
        return self.cell_coords

    def __contains__(self, coord: Vector2Int) -> bool:
        return (0 <= coord.x < self.width and
                0 <= coord.y < self.height)
