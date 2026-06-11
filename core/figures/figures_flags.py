from itertools import product
from typing import Callable

from attrs import field, frozen

from core import protocols as proto
from core.protocols import Board
from core.resources import ResourcesGroup
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
class Empty(proto.Empty):
    EXCLUDES = {proto.Movable,
                proto.Pullable,
                proto.CanPull,
                proto.PreventsCaptures,
                proto.CanAttack,
                proto.Creatable,
                proto.CanCapture}


@frozen
class OnLand(proto.OnLand):
    EXCLUDES = {proto.AtWater}


@frozen
class AtWater(proto.AtWater):
    EXCLUDES = {proto.OnLand}


@frozen
class Static(proto.Static):
    EXCLUDES = {proto.Movable}


@frozen
class DontHaveOwner(proto.DontHaveOwner):
    EXCLUDES = {proto.Movable,
                proto.Pullable,
                proto.CanPull,
                proto.PreventsCaptures,
                proto.PreventsAnnexations,
                proto.Private,
                proto.CanAttack,
                proto.Creatable,
                proto.CanCapture}


@frozen
class Pullable(proto.Pullable):
    EXCLUDES = {proto.Static}


@frozen
class CanPull(proto.CanPull):
    EXCLUDES = {proto.Static, proto.Capturable}


@frozen
class Private(proto.Private):
    EXCLUDES = set[type[Flag]]()


@frozen
class Creatable(proto.Creatable):
    EXCLUDES = set[type[Flag]]()

    @classmethod
    def make(cls, *resources: proto.Resource) -> proto.Creatable:
        return cls(ResourcesGroup.make(*resources))

    cost: proto.ResourcesGroup


@frozen
class CanCapture(proto.CanCapture):
    EXCLUDES = set[type[Flag]]()


@frozen
class Capturable(proto.Capturable):
    EXCLUDES = {proto.PreventsCaptures}


@frozen
class PreventsCaptures(proto.PreventsCaptures):
    EXCLUDES = {proto.Capturable}


@frozen
class CanAttack(proto.CanAttack):
    EXCLUDES = set[type[Flag]]()

    max_distance: int


@frozen
class StartsWithBudgetSpend(proto.StartsWithBudgetSpend):
    EXCLUDES = set[type[Flag]]()

    amount: int


@frozen
class CanLaunchOreshnik(proto.CanLaunchOreshnik):
    EXCLUDES = set[type[Flag]]()

    min_distance: int
    cost: proto.ResourcesGroup
    spread_radius: int
    targets_per_layer: int


@frozen
class PreventsAnnexations(proto.PreventsAnnexations):
    EXCLUDES = set[type[Flag]]()

    distance: int
    can_prevent: Callable[[Vector2Int, proto.GameSession, proto.Cells], int] = lambda *_: True
