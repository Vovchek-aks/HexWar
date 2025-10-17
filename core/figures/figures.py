from attrs import frozen

from core import protocols as proto
from core.figures.figures_flags import Flags, Static, Movable, Creatable


@frozen
class Empty(proto.Figure):
    STRENGTH = 0
    FLAGS = Flags.new(Static())


@frozen
class Tree(proto.Figure):
    STRENGTH = 0
    FLAGS = Flags.new(Static())


@frozen
class Farm(proto.Figure):
    STRENGTH = 0
    FLAGS = Flags.new(Static(),
                      Creatable())


@frozen
class Hub(proto.Figure):
    STRENGTH = 1
    FLAGS = Flags.new(Static())


@frozen
class Tower(proto.Figure):
    STRENGTH = 3
    FLAGS = Flags.new(Static(),
                      Creatable())


@frozen
class Castle(proto.Figure):
    STRENGTH = 5
    FLAGS = Flags.new(Static(),
                      Creatable())


@frozen
class Worker(proto.Figure):
    STRENGTH = 1
    FLAGS = Flags.new(Movable(),
                      Creatable())


@frozen
class Spearman(proto.Figure):
    STRENGTH = 2
    FLAGS = Flags.new(Movable(),
                      Creatable())


@frozen
class Squire(proto.Figure):
    STRENGTH = 4
    FLAGS = Flags.new(Movable(),
                      Creatable())


@frozen
class Knight(proto.Figure):
    STRENGTH = 6
    FLAGS = Flags.new(Movable(),
                      Creatable())


def get_figures() -> list[type[proto.Figure]]:
    return [
        Empty,
        Tree,
        Farm,
        Hub,
        Tower,
        Castle,
        Worker,
        Spearman,
        Squire,
        Knight,
    ]
