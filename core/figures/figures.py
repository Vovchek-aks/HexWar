from attrs import frozen

from core import protocols as proto
from core.figures.figures_flags import Flags, Static, Movable, Creatable
from mathematics.vector import Vector2Int


@frozen
class Empty(proto.Figure):
    FLAGS = Flags.new(Static())

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        return 0


@frozen
class Settlement(proto.Figure):
    FLAGS = Flags.new(Static(),
                      Creatable())

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        return 0


@frozen
class Town(proto.Figure):
    FLAGS = Flags.new(Static())

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        return 0


@frozen
class Capital(proto.Figure):
    FLAGS = Flags.new(Static())

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        return 0


@frozen
class Bunker(proto.Figure):
    FLAGS = Flags.new(Static(),
                      Creatable())

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        return 3


@frozen
class Infantry(proto.Figure):
    FLAGS = Flags.new(Movable.constant_strength(2),
                      Creatable())

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        return 1


@frozen
class Motorization(proto.Figure):
    FLAGS = Flags.new(Movable.constant_strength(1),
                      Creatable())

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        return 1


@frozen
class Tank(proto.Figure):
    FLAGS = Flags.new(Movable(get_strength=lambda coord, board: Tank.SELF_STRENGTH +
                                                                Tank.get_projected_strength(coord, board)),
                      Creatable())

    SELF_STRENGTH = 1
    _SELF_HARDNESS = 1
    _PER_INFANTRY_STRENGTH_RATIO = 1

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        return cls._SELF_HARDNESS + cls.get_projected_strength(coord, board)

    @classmethod
    def get_projected_strength(cls, coord: Vector2Int, board: proto.Board) -> int:
        cell = board[coord]

        return sum(map(lambda infantry_cell: cls._PER_INFANTRY_STRENGTH_RATIO * infantry_cell.strength(board),
                       board.get_neighbors(cell, include_cell=False)
                       .with_owner(cell.owner)
                       .with_figure(Infantry)
                       .all()))


@frozen
class Artillery(proto.Figure):
    FLAGS = Flags.new(Movable.constant_strength(4),
                      Creatable())

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        return 0


def get_figures() -> list[type[proto.Figure]]:
    return [
        Empty,
        Settlement,
        Town,
        Capital,
        Bunker,
        Infantry,
        Motorization,
        Tank,
        Artillery
    ]
