from attrs import define

import protocols as proto
from figures_flags import Flag


@define
class Empty(proto.Figure):
    STRENGTH = 0
    FLAGS = {Flag.STATIC}


@define
class Tree(proto.Figure):
    STRENGTH = 0
    FLAGS = {Flag.STATIC}


@define
class Farm(proto.Figure):
    STRENGTH = 0
    FLAGS = {Flag.STATIC,
             Flag.CREATABLE}


@define
class Hub(proto.Figure):
    STRENGTH = 1
    FLAGS = {Flag.STATIC}


@define
class Tower(proto.Figure):
    STRENGTH = 3
    FLAGS = {Flag.STATIC,
             Flag.CREATABLE,
             Flag.UPGRADABLE}


@define
class Castle(proto.Figure):
    STRENGTH = 5
    FLAGS = {Flag.STATIC,
             Flag.CREATABLE,
             Flag.UPGRADABLE}


@define
class Worker(proto.Figure):
    STRENGTH = 1
    FLAGS = {Flag.MOVABLE,
             Flag.CREATABLE,
             Flag.UPGRADABLE}


@define
class Spearman(proto.Figure):
    STRENGTH = 2
    FLAGS = {Flag.MOVABLE,
             Flag.CREATABLE,
             Flag.UPGRADABLE}


@define
class Squire(proto.Figure):
    STRENGTH = 4
    FLAGS = {Flag.MOVABLE,
             Flag.CREATABLE,
             Flag.UPGRADABLE}


@define
class Knight(proto.Figure):
    STRENGTH = 6
    FLAGS = {Flag.MOVABLE,
             Flag.CREATABLE,
             Flag.UPGRADABLE}


MAX_STRENGTH = Knight.STRENGTH
