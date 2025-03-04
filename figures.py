from attrs import define

import protocols as proto


@define
class Empty(proto.StaticFigure):
    STRENGTH = 0


@define
class Tree(proto.StaticFigure):
    STRENGTH = 0


@define
class Farm(proto.StaticFigure):
    STRENGTH = 0


@define
class Hub(proto.StaticFigure):
    STRENGTH = 1


@define
class Tower(proto.StaticFigure):
    STRENGTH = 3


@define
class Castle(proto.StaticFigure):
    STRENGTH = 5


@define
class Worker(proto.MovableFigure):
    STRENGTH = 1


@define
class Spearman(proto.MovableFigure):
    STRENGTH = 2


@define
class Squire(proto.MovableFigure):
    STRENGTH = 4


@define
class Knight(proto.MovableFigure):
    STRENGTH = 6


MAX_STRENGTH = Knight.STRENGTH
