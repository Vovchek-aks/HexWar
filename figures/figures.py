from attrs import frozen

import protocols as proto
from figures_flags import Flags, Static, Movable


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
    FLAGS = Flags.new(Static())


@frozen
class Hub(proto.Figure):
    STRENGTH = 1
    FLAGS = Flags.new(Static())


@frozen
class Tower(proto.Figure):
    STRENGTH = 3
    FLAGS = Flags.new(Static())


@frozen
class Castle(proto.Figure):
    STRENGTH = 5
    FLAGS = Flags.new(Static())


@frozen
class Worker(proto.Figure):
    STRENGTH = 1
    FLAGS = Flags.new(Movable())


@frozen
class Spearman(proto.Figure):
    STRENGTH = 2
    FLAGS = Flags.new(Movable())


@frozen
class Squire(proto.Figure):
    STRENGTH = 4
    FLAGS = Flags.new(Movable())


@frozen
class Knight(proto.Figure):
    STRENGTH = 6
    FLAGS = Flags.new(Movable())


MAX_STRENGTH = Knight.STRENGTH
