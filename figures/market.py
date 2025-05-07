from attrs import frozen

import protocols as proto
from protocols import Updatable, Figure, Creatable


@frozen
class FiguresMarket(proto.FiguresMarket):
    @classmethod
    def register_creatable(cls, flag: Creatable, kind: proto.CreatableKind, price: int) -> None:
        pass

    @classmethod
    def register_updatable(cls, flag: Updatable, to: type[Figure]) -> None:
        pass


@frozen
class CreatableKind(proto.CreatableKind):
    ...


BUILDING = CreatableKind()
UNIT = CreatableKind()
