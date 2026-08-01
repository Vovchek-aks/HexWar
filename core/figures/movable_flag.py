from typing import Callable

from attrs import frozen, define, field

from core import protocols as proto
from core.protocols import Board
from mathematics.vector import Vector2Int
from statuses import Status, MISSING


@frozen
class Movable(proto.Movable):
    EXCLUDES = {proto.Static}

    _base_strength: int
    _get_additional_strength: Callable[[Vector2Int, proto.Board], int]
    _can_relocate: Callable[[Vector2Int, Vector2Int, proto.Board], bool]

    @property
    def base_strength(self) -> int:
        return self._base_strength

    def strength(self, coord: Vector2Int, board: proto.Board) -> int:
        return self._base_strength + self._get_additional_strength(coord, board)

    def can_relocate(self, from_coord: Vector2Int, to_coord: Vector2Int, board: Board) -> bool:
        return self._can_relocate(from_coord, to_coord, board)


@define
class MovableBuilder:
    _base_strength: int = field(init=False, default=0)
    _get_additional_strength: Callable[[Vector2Int, proto.Board], int] = field(init=False, default=lambda _, __: 0)
    _can_relocate: Callable[[Vector2Int, Vector2Int, proto.Board], bool] | Status = field(init=False, default=MISSING)

    def is_valid(self) -> bool:
        return MISSING not in (self._get_additional_strength, self._can_relocate)

    def build(self) -> Movable:
        assert self.is_valid()
        return Movable(self._base_strength, self._get_additional_strength, self._can_relocate)

    def set_base_strength(self, strength: int) -> "MovableBuilder":
        self._base_strength = strength
        return self

    def set_additional_strength_getter(self,
                                       get_additional_strength: Callable[[Vector2Int, proto.Board], int]
                                       ) -> "MovableBuilder":
        self._get_additional_strength = get_additional_strength
        return self

    def set_can_relocate(self, can_relocate: Callable[[Vector2Int, Vector2Int, proto.Board], bool]) -> "MovableBuilder":
        assert self._can_relocate is MISSING

        return self._set_can_relocate(can_relocate)

    def always_can_move(self) -> "MovableBuilder":
        assert self._can_relocate is MISSING

        return self._set_can_relocate(lambda from_coord, to_coord, board: True)

    def can_move_to_neighbor(self) -> "MovableBuilder":
        assert self._can_relocate is MISSING

        def can_relocate(from_coord: Vector2Int, to_coord: Vector2Int, board: Board) -> bool:
            from_cell = board[from_coord]
            to_cell = board[to_coord]
            return to_cell in board.get_neighbors(from_cell, include_cell=False).with_flag(proto.OnLand)

        return self._set_can_relocate(can_relocate)

    def restrict_terrains(self, *territories: type[proto.TerrainKind]) -> "MovableBuilder":
        assert self._can_relocate is not MISSING

        territories_set = set(territories)
        assert len(territories) == len(territories_set)

        current_can_relocate = self._can_relocate

        def can_relocate(from_coord: Vector2Int, to_coord: Vector2Int, board: Board) -> bool:
            if board[to_coord].terrain_kinds(board) & territories_set:
                return False
            return current_can_relocate(from_coord, to_coord, board)

        return self._set_can_relocate(can_relocate)

    def _set_can_relocate(self,
                          can_relocate: Callable[[Vector2Int, Vector2Int, proto.Board], bool]) -> "MovableBuilder":
        self._can_relocate = can_relocate
        return self
