from itertools import product
from typing import Callable

from attrs import field, frozen

from core import protocols as proto
from mathematics.vector import Vector2Int
from statuses import Status, MISSING

Flag = proto.Flag


@frozen
class Flags(proto.Flags):
    @classmethod
    def new(cls, *flags: Flag) -> proto.Flags:
        return cls(set(flags))

    _flags: set[Flag] = field()

    @_flags.validator
    def _validate_flags(self, _, flags: set[Flag]) -> None:
        if len(self.flag_types) != len(flags):
            raise ValueError("Certain flag type can only once be added")

        for flag in flags:
            for excluded, target in product(flag.EXCLUDES, flags):
                if isinstance(target, excluded):
                    raise ValueError(f"{type(target)} does not fits {type(flag)} excludes: {flag.EXCLUDES}")

    @property
    def flag_types(self) -> set[type[Flag]]:
        return set(map(type[Flag], self._flags))

    def get[T: Flag](self, flag_type: type[T]) -> T | Status:
        if not (flags := [flag for flag in self._flags if isinstance(flag, flag_type)]):
            return MISSING
        return flags[0]

    def __contains__(self, item: type[Flag]) -> bool:
        return self.get(item) is not MISSING


@frozen
class Static(proto.Static):
    EXCLUDES = {proto.Movable}


@frozen
class Movable(proto.Movable):
    EXCLUDES = {proto.Static}

    @classmethod
    def constant_strength(cls, strength: int) -> proto.Movable:
        return cls(lambda coord, board: strength)

    _get_strength: Callable[[Vector2Int, proto.Board], int]

    def strength(self, coord: Vector2Int, board: proto.Board) -> int:
        return self._get_strength(coord, board)


@frozen
class Creatable(proto.Creatable):
    EXCLUDES = set[type[Flag]]()
