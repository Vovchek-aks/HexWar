from attrs import define

import protocols as proto
from figures_flags import Flags, Static, Movable, Creatable, Updatable
from market import FiguresMarket, BUILDING, UNIT


@define
class Empty(proto.Figure):
    STRENGTH = 0
    FLAGS = Flags.new(Static())


@define
class Tree(proto.Figure):
    STRENGTH = 0
    FLAGS = Flags.new(Static())


@define
class Farm(proto.Figure):
    STRENGTH = 0
    FLAGS = Flags.new(Static(),
                      Creatable.new(FiguresMarket, BUILDING, 20))


@define
class Hub(proto.Figure):
    STRENGTH = 1
    FLAGS = Flags.new(Static())


@define
class Tower(proto.Figure):
    STRENGTH = 3
    FLAGS = Flags.new(Static(),
                      creatable := Creatable.new(FiguresMarket, BUILDING, 50),
                      Updatable.new(FiguresMarket, creatable))


@define
class Castle(proto.Figure):
    STRENGTH = 5
    FLAGS = Flags.new(Static(),
                      Creatable.new(FiguresMarket, BUILDING, 100))


@define
class Worker(proto.Figure):
    STRENGTH = 1
    FLAGS = Flags.new(Movable(),
                      creatable := Creatable.new(FiguresMarket, UNIT, 10),
                      Updatable.new(FiguresMarket, creatable))


@define
class Spearman(proto.Figure):
    STRENGTH = 2
    FLAGS = Flags.new(Movable(),
                      creatable := Creatable.new(FiguresMarket, UNIT, 20),
                      Updatable.new(FiguresMarket, creatable))


@define
class Squire(proto.Figure):
    STRENGTH = 4
    FLAGS = Flags.new(Movable(),
                      creatable := Creatable.new(FiguresMarket, UNIT, 30),
                      Updatable.new(FiguresMarket, creatable))


@define
class Knight(proto.Figure):
    STRENGTH = 6
    FLAGS = Flags.new(Movable(),
                      creatable := Creatable.new(FiguresMarket, UNIT, 50),
                      Updatable.new(FiguresMarket, creatable))


MAX_STRENGTH = Knight.STRENGTH
