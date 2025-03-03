from attrs import define

import protocols as proto


@define
class Empty(proto.FigureStatic):
    STRENGTH = 0


@define
class Tree(proto.FigureStatic):
    STRENGTH = 0


@define
class Farm(proto.FigureStatic):
    STRENGTH = 0


@define
class Hub(proto.FigureStatic):
    STRENGTH = 1


@define
class Tower(proto.FigureStatic):
    STRENGTH = 3


@define
class Castle(proto.FigureStatic):
    STRENGTH = 5


@define
class Worker(proto.FigureMovable):
    STRENGTH = 1


@define
class Spearman(proto.FigureMovable):
    STRENGTH = 2


@define
class Squire(proto.FigureMovable):
    STRENGTH = 4


@define
class Knight(proto.FigureMovable):
    STRENGTH = 6


MAX_STRENGTH = Knight.STRENGTH
