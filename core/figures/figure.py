from abc import ABCMeta

from attrs import define, field

from core import protocols as proto
from core.figures.figures_flags import Flags, Static, Creatable, CanCapture, Capturable, CanAttack, Pullable, \
    PreventCaptures, CanPull, OnLand, AtWater, Empty, DontHaveOwner, CanLaunchOreshnik, StartsWithBudgetSpend
from core.figures.movable_flag import MovableBuilder
from core.figures.updatable_on_turn_start_flag import UpdatableOnTurnStartBuilder
from core.moves.attack import Attack
from core.moves.capture import Capture
from core.moves.oreshnik_launch import OreshnikLaunch
from core.moves.pulling import PullingInitiation, PullingTermination
from core.moves.relocations import Relocation, Assault
from core.resources import Dollars
from exceptions import NotSupportedMove
from mathematics.vector import Vector2Int
from core.protocols import Figure


@define(hash=True, eq=True)
class _Figure(Figure, metaclass=ABCMeta):
    _id: int = field(init=False)

    @classmethod
    def is_on_land(cls) -> bool:
        if OnLand in cls.FLAGS:
            return True

        assert AtWater in cls.FLAGS
        return False

    def __attrs_post_init__(self) -> None:
        self._id = id(self)


class Land(_Figure):
    FLAGS = Flags.new(OnLand(),
                      Empty(),
                      Static(),
                      Capturable())
    MOVES_BUDGET = 0

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        return 0

    @classmethod
    def get_cost_of(cls, move: proto.Move) -> int:
        return 0


class Water(_Figure):
    FLAGS = Flags.new(AtWater(),
                      Empty(),
                      DontHaveOwner(),
                      Static())
    MOVES_BUDGET = 0

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        return 0

    @classmethod
    def get_cost_of(cls, move: proto.Move) -> int:
        return 0


class Settlement(_Figure):
    FLAGS = Flags.new(OnLand(),
                      Static())
    MOVES_BUDGET = 0

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        return 0

    @classmethod
    def get_cost_of(cls, move: proto.Move) -> int:
        return 0


class Town(_Figure):
    FLAGS = Flags.new(OnLand(),
                      Static(),
                      Creatable(Dollars(1_000_000)),
                      Capturable(),
                      (UpdatableOnTurnStartBuilder()
                       .add_resources_conditionally(lambda coord, board: Town.get_resources_to_add(coord, board))
                       .build()))
    MOVES_BUDGET = 0
    BASE_RESOURCES_TO_ADD = Dollars(200_000)

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        return 0

    @classmethod
    def get_cost_of(cls, move: proto.Move) -> int:
        return 0

    @classmethod
    def get_resources_to_add(cls, coord: Vector2Int, board: proto.Board) -> proto.Resource:
        cell = board[coord]
        capitals = board.get_neighbors(cell).with_owner(cell.owner).with_figure(Capital)
        return cls.BASE_RESOURCES_TO_ADD * (1 + len(capitals))


class Capital(_Figure):
    FLAGS = Flags.new(OnLand(),
                      Static(),
                      Creatable(Dollars(5_000_000)),
                      (UpdatableOnTurnStartBuilder()
                       .try_take_else_die(Dollars(800_000))
                       .build()))
    MOVES_BUDGET = 0

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        return 0

    @classmethod
    def get_cost_of(cls, move: proto.Move) -> int:
        return 0


class Bunker(_Figure):
    FLAGS = Flags.new(OnLand(),
                      Static(),
                      Creatable(Dollars(150_000)))
    MOVES_BUDGET = 0

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        return 4

    @classmethod
    def get_cost_of(cls, move: proto.Move) -> int:
        return 0


class MissileSilo(_Figure):
    FLAGS = Flags.new(OnLand(),
                      Static(),
                      Creatable(Dollars(3_000_000)),
                      Capturable(),
                      StartsWithBudgetSpend(1),
                      CanLaunchOreshnik(min_distance=10,
                                        cost=Dollars(750_000),
                                        spread_radius=3,
                                        targets_per_layer=3))
    MOVES_BUDGET = 1

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        return 0

    @classmethod
    def get_cost_of(cls, move: proto.Move) -> int:
        match move:
            case OreshnikLaunch():
                return 1
            case _:
                raise NotSupportedMove(move)


class Infantry(_Figure):
    FLAGS = Flags.new(OnLand(),
                      (MovableBuilder()
                       .can_move_to_neighbor()
                       .constant_strength(3)
                       .build()),
                      CanPull(),
                      Creatable(Dollars(100_000)),
                      CanCapture(),
                      PreventCaptures(),
                      (UpdatableOnTurnStartBuilder()
                       .try_take_else_die(Dollars(25_000))
                       .build()))
    MOVES_BUDGET = 6

    SELF_HARDNESS = 2
    _NEAR_BUNKER_HARDNESS = 6

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        cell = board[coord]
        has_bunker = bool(board.get_neighbors(cell, include_cell=False)
                          .with_flag(proto.OnLand)
                          .with_owner(cell.owner)
                          .with_figure(Bunker))
        if has_bunker:
            return cls._NEAR_BUNKER_HARDNESS

        return cls.SELF_HARDNESS

    @classmethod
    def get_cost_of(cls, move: proto.Move) -> int:
        match move:
            case Relocation():
                return 1
            case Assault():
                return 2
            case Capture():
                return 2
            case PullingInitiation():
                return 0
            case PullingTermination():
                return 0
            case _:
                raise NotSupportedMove(move)


class Motorization(_Figure):
    FLAGS = Flags.new(OnLand(),
                      (MovableBuilder()
                       .can_move_to_neighbor()
                       .constant_strength(3)
                       .build()),
                      CanPull(),
                      PreventCaptures(),
                      (UpdatableOnTurnStartBuilder()
                       .try_take_else_die(Dollars(75_000))
                       .build()))
    MOVES_BUDGET = 200

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        return 1

    @classmethod
    def get_cost_of(cls, move: proto.Move) -> int:
        match move:
            case Relocation():
                return 5
            case Assault():
                return 14
            case PullingInitiation():
                return 0
            case PullingTermination():
                return 0
            case _:
                raise NotSupportedMove(move)


class Tank(_Figure):
    FLAGS = Flags.new(OnLand(),
                      (MovableBuilder()
                       .can_move_to_neighbor()
                       .set_strength_getter(lambda coord, board: Tank.SELF_STRENGTH +
                                                                 Tank.get_projected_strength(coord, board))
                       .build()),
                      Creatable(Dollars(500_000)),
                      Capturable(),
                      (UpdatableOnTurnStartBuilder()
                       .try_take_else_die(Dollars(100_000))
                       .build()),
                      CanAttack(1))
    MOVES_BUDGET = 200

    SELF_STRENGTH = 3
    _SELF_HARDNESS = 2
    _PER_INFANTRY_STRENGTH_RATIO = .5
    _PER_INFANTRY_HARDNESS_RATIO = .5

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        return cls._SELF_HARDNESS + cls._get_projected(coord, board, cls._PER_INFANTRY_HARDNESS_RATIO)

    @classmethod
    def get_cost_of(cls, move: proto.Move) -> int:
        match move:
            case Relocation():
                return 15
            case Assault():
                return 25
            case Attack():
                return 20
            case _:
                raise NotSupportedMove(move)

    @classmethod
    def get_projected_strength(cls, coord: Vector2Int, board: proto.Board) -> int:
        return cls._get_projected(coord, board, cls._PER_INFANTRY_STRENGTH_RATIO)

    @classmethod
    def _get_projected(cls, coord: Vector2Int, board: proto.Board, per_infantry_ratio: float) -> int:
        cell = board[coord]

        return int(per_infantry_ratio *
                   sum(map(lambda infantry_cell: infantry_cell.strength(board),
                           board.get_neighbors(cell, include_cell=False)
                           .with_flag(proto.OnLand)
                           .with_owner(cell.owner)
                           .with_figure(Infantry | Motorization)
                           .as_set())))


class Artillery(_Figure):
    FLAGS = Flags.new(OnLand(),
                      MovableBuilder()
                      .constant_strength(1_000_000)
                      .set_can_relocate(lambda from_coord, to_coord, board: False)
                      .build(),
                      Pullable(),
                      Creatable(Dollars(250_000)),
                      Capturable(),
                      (UpdatableOnTurnStartBuilder()
                       .try_take_else_die(Dollars(150_000))
                       .build()),
                      CanAttack(3))
    MOVES_BUDGET = 7

    @classmethod
    def hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        return 0

    @classmethod
    def get_cost_of(cls, move: proto.Move) -> int:
        match move:
            case Relocation():
                return 1
            case Assault():
                return cls.MOVES_BUDGET + 1
            case Attack():
                return 4
            case PullingInitiation():
                return 0
            case PullingTermination():
                return 0
            case _:
                raise NotSupportedMove(move)


def get_figures() -> list[type[_Figure]]:
    return [
        Land,
        Water,
        Settlement,
        Town,
        Capital,
        Bunker,
        MissileSilo,
        Infantry,
        Motorization,
        Tank,
        Artillery
    ]
