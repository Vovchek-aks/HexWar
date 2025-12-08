from abc import ABCMeta

from attrs import define, field

from core import protocols as proto
from core.cells import Cells
from core.figures.figures_flags import Flags, Static, Creatable, CanCapture, Capturable, CanAttack
from core.figures.movable_flag import MovableBuilder
from core.figures.updatable_on_turn_start_flag import UpdatableOnTurnStartBuilder
from core.moves.attack import Attack
from core.moves.capture import Capture
from core.moves.relocations import Relocation, Assault
from core.resources import Dollars
from exceptions import NotSupportedMove
from mathematics.vector import Vector2Int
from core.protocols import Figure


@define(hash=True, eq=True)
class _Figure(Figure, metaclass=ABCMeta):
    _id: int = field(init=False)

    def __attrs_post_init__(self) -> None:
        self._id = id(self)


class Empty(_Figure):
    FLAGS = Flags.new(Static(),
                      Capturable())
    MOVES_BUDGET = 0

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        return 0

    @classmethod
    def get_cost_of(cls, move: proto.Move, board: proto.Board) -> int:
        return 0


class Settlement(_Figure):
    FLAGS = Flags.new(Static())
    MOVES_BUDGET = 0

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        return 0

    @classmethod
    def get_cost_of(cls, move: proto.Move, board: proto.Board) -> int:
        return 0


class Town(_Figure):
    FLAGS = Flags.new(Static(),
                      Creatable(Dollars(1_000_000)),
                      (UpdatableOnTurnStartBuilder()
                       .add_resources(Dollars(150_000))
                       .build()))
    MOVES_BUDGET = 0

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        return 0

    @classmethod
    def get_cost_of(cls, move: proto.Move, board: proto.Board) -> int:
        return 0


class Capital(_Figure):
    FLAGS = Flags.new(Static())
    MOVES_BUDGET = 0

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        return 0

    @classmethod
    def get_cost_of(cls, move: proto.Move, board: proto.Board) -> int:
        return 0


class Bunker(_Figure):
    FLAGS = Flags.new(Static(),
                      Creatable(Dollars(1_000_000)))
    MOVES_BUDGET = 0

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        return 4

    @classmethod
    def get_cost_of(cls, move: proto.Move, board: proto.Board) -> int:
        return 0


class Infantry(_Figure):
    FLAGS = Flags.new((MovableBuilder()
                       .can_move_to_neighbor()
                       .constant_strength(3)
                       .build()),
                      Creatable(Dollars(100_000)),
                      CanCapture(),
                      (UpdatableOnTurnStartBuilder()
                       .try_take_else_die(Dollars(5_000))
                       .build()))
    MOVES_BUDGET = 3

    SELF_HARDNESS = 2
    _NEAR_BUNKER_HARDNESS = 4

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        cell = board[coord]
        has_bunker = bool(board.get_neighbors(cell, include_cell=False)
                          .with_owner(cell.owner)
                          .with_figure(Bunker))
        if has_bunker:
            return cls._NEAR_BUNKER_HARDNESS

        return cls.SELF_HARDNESS

    @classmethod
    def get_cost_of(cls, move: proto.Move, board: proto.Board) -> int:
        match move:
            case Relocation():
                return 1
            case Assault():
                return 3
            case Capture():
                return 2
            case _:
                raise NotSupportedMove(move)


class Motorization(_Figure):
    FLAGS = Flags.new((MovableBuilder()
                       .can_move_to_neighbor()
                       .constant_strength(3)
                       .build()),
                      (UpdatableOnTurnStartBuilder()
                       .try_take_else_die(Dollars(10_000))
                       .build()))
    MOVES_BUDGET = 60

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        return 1

    @classmethod
    def get_cost_of(cls, move: proto.Move, board: proto.Board) -> int:
        match move:
            case Relocation():
                return 10
            case Assault():
                return 15
            case _:
                raise NotSupportedMove(move)


class Tank(_Figure):
    FLAGS = Flags.new((MovableBuilder()
                       .can_move_to_neighbor()
                       .set_strength_getter(lambda coord, board: Tank.SELF_STRENGTH +
                                                                 Tank.get_projected_strength(coord, board))
                       .build()),
                      Creatable(Dollars(1_000_000)),
                      Capturable(),
                      (UpdatableOnTurnStartBuilder()
                       .try_take_else_die(Dollars(20_000))
                       .build()),
                      CanAttack(1))
    MOVES_BUDGET = 60

    SELF_STRENGTH = 1
    _SELF_HARDNESS = 2
    _PER_INFANTRY_STRENGTH_RATIO = .5

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        return cls._SELF_HARDNESS + cls.get_projected_strength(coord, board)

    @classmethod
    def get_cost_of(cls, move: proto.Move, board: proto.Board) -> int:
        match move:
            case Relocation():
                return 15
            case Assault():
                return 20
            case Attack():
                return 20
            case _:
                raise NotSupportedMove(move)

    @classmethod
    def get_projected_strength(cls, coord: Vector2Int, board: proto.Board) -> int:
        cell = board[coord]

        return int(cls._PER_INFANTRY_STRENGTH_RATIO *
                   sum(map(lambda infantry_cell: infantry_cell.strength(board),
                           board.get_neighbors(cell, include_cell=False)
                           .with_owner(cell.owner)
                           .with_figure(Infantry | Motorization)
                           .all())))


class Artillery(_Figure):
    FLAGS = Flags.new(MovableBuilder()
                      .constant_strength(6)
                      .set_can_relocate(lambda from_coord, to_coord, board:
                                        Artillery.can_relocate(from_coord, to_coord, board))
                      .build(),
                      Creatable(Dollars(150_000)),
                      Capturable(),
                      (UpdatableOnTurnStartBuilder()
                       .try_take_else_die(Dollars(20_000))
                       .build()),
                      CanAttack(1))
    MOVES_BUDGET = 2

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        return 0

    @classmethod
    def get_cost_of(cls, move: proto.Move, board: proto.Board) -> int:
        return 1

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


def get_figures() -> list[type[_Figure]]:
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
