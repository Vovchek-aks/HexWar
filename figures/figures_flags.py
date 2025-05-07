from itertools import product

from attrs import field, frozen

import protocols as proto
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
                    raise ValueError(f"{type(flag)} does not fits other flags")

    @property
    def flag_types(self) -> set[type[Flag]]:
        return set(map(type, self._flags))

    def get[T: Flag](self, flag_type: type[T]) -> T | Status:
        if not (flags := [flag for flag in self._flags if type(flag) == flag_type]):
            return MISSING
        return flags[0]

    def __contains__(self, item: type[Flag]) -> bool:
        return any(issubclass(item, type(flag)) for flag in self._flags)


@frozen
class Static(Flag):
    EXCLUDES = {proto.Movable}


@frozen
class Movable(proto.Movable):
    EXCLUDES = {proto.Static}


@frozen
class Creatable(proto.Creatable):
    EXCLUDES = {}

    @classmethod
    def new(cls, market: type[proto.FiguresMarket], kind: proto.CreatableKind, price: int) -> proto.Creatable:
        flag = cls()
        market.register_creatable(flag, kind, price)
        return flag


@frozen
class Updatable(proto.Updatable):
    EXCLUDES = {}

    @classmethod
    def new(cls, market: type[proto.FiguresMarket], creatable: proto.Creatable) -> "Updatable":
        flag = cls()
        market.register_updatable(flag, creatable)
        return flag
