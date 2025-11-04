from attrs import frozen

from core import protocols as proto
from core.cells import Cells
from core.figures.figures_flags import Flags, Static, Creatable
from core.figures.movable_flag import MovableBuilder
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
    FLAGS = Flags.new(Static(),
                      Creatable())

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
    FLAGS = Flags.new(MovableBuilder()
                      .always_can_move()
                      .constant_strength(2)
                      .build(),
                      Creatable())

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        return 1


@frozen
class Motorization(proto.Figure):
    FLAGS = Flags.new(MovableBuilder()
                      .always_can_move()
                      .constant_strength(1)
                      .build(),
                      Creatable())

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        return 1


@frozen
class Tank(proto.Figure):
    FLAGS = Flags.new(MovableBuilder()
                      .always_can_move()
                      .set_strength_getter(lambda coord, board: Tank.SELF_STRENGTH +
                                                                Tank.get_projected_strength(coord, board))
                      .build(),
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

        return (cls._PER_INFANTRY_STRENGTH_RATIO *
                sum(map(lambda infantry_cell: infantry_cell.strength(board),
                        board.get_neighbors(cell, include_cell=False)
                        .with_owner(cell.owner)
                        .with_figure(Infantry | Motorization)
                        .all())))


@frozen
class Artillery(proto.Figure):
    FLAGS = Flags.new(MovableBuilder()
                      .constant_strength(4)
                      .set_can_relocate(lambda from_coord, to_coord, board:
                                        Artillery.can_relocate(from_coord, to_coord, board))
                      .build(),
                      Creatable())

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        return 0

    @classmethod
    def can_relocate(cls, from_coord: Vector2Int, to_coord: Vector2Int, board: proto.Board) -> bool:
        cell = board[from_coord]
        infantry_cells = (board.get_neighbors(cell, include_cell=False)
                          .with_owner(cell.owner)
                          .with_figure(Infantry | Motorization)
                          .all())

        cells = Cells()
        for infantry_cell in infantry_cells:
            cells += board.get_neighbors(infantry_cell, include_cell=False)

        target = board[to_coord]
        return target in cells



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
