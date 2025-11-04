from typing import Callable

from attrs import frozen, define, field

from core import protocols as proto
from core.protocols import Board
from mathematics.vector import Vector2Int
from statuses import Status, MISSING


@frozen
class Movable(proto.Movable):
    EXCLUDES = {proto.Static}

    _get_strength: Callable[[Vector2Int, proto.Board], int]
    _can_relocate: Callable[[Vector2Int, Vector2Int, proto.Board], bool]

    def strength(self, coord: Vector2Int, board: proto.Board) -> int:
        return self._get_strength(coord, board)

    def can_relocate(self, from_coord: Vector2Int, to_coord: Vector2Int, board: Board) -> bool:
        return self._can_relocate(from_coord, to_coord, board)


@define
class MovableBuilder:
    _get_strength: Callable[[Vector2Int, proto.Board], int] | Status = field(init=False, default=MISSING)
    _can_relocate: Callable[[Vector2Int, Vector2Int, proto.Board], bool] | Status = field(init=False, default=MISSING)

    def is_valid(self) -> bool:
        return MISSING not in (self._get_strength, self._can_relocate)

    def build(self) -> Movable:
        assert self.is_valid()
        return Movable(self._get_strength, self._can_relocate)

    def set_strength_getter(self, get_strength: Callable[[Vector2Int, proto.Board], int]) -> "MovableBuilder":
        self._get_strength = get_strength
        return self

    def set_can_relocate(self, can_relocate: Callable[[Vector2Int, Vector2Int, proto.Board], bool]) -> "MovableBuilder":
        self._can_relocate = can_relocate
        return self

    def constant_strength(self, strength: int) -> "MovableBuilder":
        return self.set_strength_getter(lambda coord, board: strength)

    def always_can_move(self) -> "MovableBuilder":
        return self.set_can_relocate(lambda from_coord, to_coord, board: True)

    def can_move_to_neighbor(self) -> "MovableBuilder":
        def can_relocate(from_coord: Vector2Int, to_coord: Vector2Int, board: Board) -> bool:
            from_cell = board[from_coord]
            to_cell = board[to_coord]
            return to_cell in board.get_neighbors(from_cell, include_cell=False)

        return self.set_can_relocate(can_relocate)
