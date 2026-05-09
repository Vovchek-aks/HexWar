from abc import ABCMeta

from attrs import define, field

from core import protocols as proto
from core.figures.figures_flags import Flags, Static, Creatable, CanCapture, Capturable, CanAttack, Pullable, \
    PreventCaptures, CanPull, OnLand, AtWater, Empty, DontHaveOwner, CanLaunchOreshnik, StartsWithBudgetSpend
from core.figures.movable_flag import MovableBuilder
from core.figures.resources_flow_flags import TriesTakeResourcesElseDies, AddsResourcesIndefinably, \
    BuffsNeighborResourceAdders, TransformsResourcesIndefinably
from core.moves.attack import Attack
from core.moves.capture import Capture
from core.moves.oreshnik_launch import OreshnikLaunch
from core.moves.pulling import PullingInitiation, PullingTermination
from core.moves.relocations import Relocation, Assault
from core.resources import ResourcesGroup, Dollars, LightIndustryProducts, HeavyIndustryProducts
from exceptions import NotSupportedMove
from mathematics.vector import Vector2Int
from core.protocols import Figure, Board


# it's here because of python stupidity
def _get_transformer_of(figure: type[Figure]) -> TransformsResourcesIndefinably:
    return figure.FLAGS.get(TransformsResourcesIndefinably)


@define(hash=True, eq=True)
class _Figure(Figure, metaclass=ABCMeta):
    _id: int = field(init=False)

    @classmethod
    def is_on_land(cls) -> bool:
        if OnLand in cls.FLAGS:
            return True

        assert AtWater in cls.FLAGS
        return False

    @classmethod
    def hardness(cls, coord: Vector2Int, board: Board) -> int:
        return cls.base_hardness() + cls.additional_hardness(coord, board)

    @classmethod
    def additional_hardness(cls, coord: Vector2Int, board: Board) -> int:
        return 0

    def __attrs_post_init__(self) -> None:
        self._id = id(self)


class Land(_Figure):
    FLAGS = Flags.new(OnLand(),
                      Empty(),
                      Static(),
                      Capturable())
    MOVES_BUDGET = 0

    @classmethod
    def base_hardness(cls) -> int:
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
    def base_hardness(cls) -> int:
        return 0

    @classmethod
    def get_cost_of(cls, move: proto.Move) -> int:
        return 0


class Settlement(_Figure):
    FLAGS = Flags.new(OnLand(),
                      Static())
    MOVES_BUDGET = 0

    @classmethod
    def base_hardness(cls) -> int:
        return 0

    @classmethod
    def get_cost_of(cls, move: proto.Move) -> int:
        return 0


class Town(_Figure):
    FLAGS = Flags.new(OnLand(),
                      Static(),
                      Creatable.make(Dollars(700_000), LightIndustryProducts(1_000)),
                      Capturable(),
                      AddsResourcesIndefinably.make(Dollars(250_000)))
    MOVES_BUDGET = 0

    @classmethod
    def base_hardness(cls) -> int:
        return 0

    @classmethod
    def get_cost_of(cls, move: proto.Move) -> int:
        return 0


class LightFactory(_Figure):
    FLAGS = Flags.new(OnLand(),
                      Static(),
                      Creatable.make(Dollars(1_500_000)),
                      Capturable(),
                      TransformsResourcesIndefinably(ResourcesGroup.make(Dollars(100_000)),
                                                     ResourcesGroup.make(LightIndustryProducts(1_000))))
    MOVES_BUDGET = 0

    @classmethod
    def base_hardness(cls) -> int:
        return 0

    @classmethod
    def get_cost_of(cls, move: proto.Move) -> int:
        return 0


class HeavyFactory(_Figure):
    FLAGS = Flags.new(OnLand(),
                      Static(),
                      Creatable.make(Dollars(3_000_000), LightIndustryProducts(15_000)),
                      Capturable(),
                      TransformsResourcesIndefinably(ResourcesGroup.make(Dollars(500_000),
                                                                         LightIndustryProducts(3_000)),
                                                     ResourcesGroup.make(HeavyIndustryProducts(1_000)),
                                                     priority=_get_transformer_of(LightFactory).priority + 1))
    MOVES_BUDGET = 0

    @classmethod
    def base_hardness(cls) -> int:
        return 0

    @classmethod
    def get_cost_of(cls, move: proto.Move) -> int:
        return 0


class Capital(_Figure):
    FLAGS = Flags.new(OnLand(),
                      Static(),
                      Capturable(),
                      Creatable.make(Dollars(2_000_000), LightIndustryProducts(10_000), HeavyIndustryProducts(1_000)),
                      TriesTakeResourcesElseDies.make(Dollars(800_000)),
                      BuffsNeighborResourceAdders(ratio=1))
    MOVES_BUDGET = 0

    @classmethod
    def base_hardness(cls) -> int:
        return 0

    @classmethod
    def get_cost_of(cls, move: proto.Move) -> int:
        return 0


class Bunker(_Figure):
    FLAGS = Flags.new(OnLand(),
                      Static(),
                      Creatable.make(Dollars(150_000), LightIndustryProducts(250)))
    MOVES_BUDGET = 0

    @classmethod
    def base_hardness(cls) -> int:
        return 4

    @classmethod
    def get_cost_of(cls, move: proto.Move) -> int:
        return 0


class MissileSilo(_Figure):
    FLAGS = Flags.new(OnLand(),
                      Static(),
                      Creatable.make(Dollars(2_000_000), LightIndustryProducts(20_000), HeavyIndustryProducts(5_000)),
                      Capturable(),
                      StartsWithBudgetSpend(1),
                      TriesTakeResourcesElseDies.make(Dollars(25_000),
                                                      LightIndustryProducts(1_000),
                                                      HeavyIndustryProducts(500)),
                      CanLaunchOreshnik(min_distance=10,
                                        cost=ResourcesGroup.make(Dollars(250_000),
                                                                 LightIndustryProducts(15_000),
                                                                 HeavyIndustryProducts(7_500)),
                                        spread_radius=3,
                                        targets_per_layer=3))
    MOVES_BUDGET = 1

    @classmethod
    def base_hardness(cls) -> int:
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
                       .set_base_strength(3)
                       .build()),
                      CanPull(),
                      Creatable.make(Dollars(200_000)),
                      CanCapture(),
                      PreventCaptures(),
                      TriesTakeResourcesElseDies.make(Dollars(50_000)))
    MOVES_BUDGET = 6

    _NEAR_BUNKER_HARDNESS_INCREASE = 4

    @classmethod
    def base_hardness(cls) -> int:
        return 2

    @classmethod
    def additional_hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        cell = board[coord]
        has_bunker = bool(board.get_neighbors(cell, include_cell=False)
                          .with_flag(proto.OnLand)
                          .with_owner(cell.owner)
                          .with_figure(Bunker))
        if has_bunker:
            return cls._NEAR_BUNKER_HARDNESS_INCREASE

        return 0

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
                       .set_base_strength(3)
                       .build()),
                      CanPull(),
                      PreventCaptures(),
                      TriesTakeResourcesElseDies.make(Dollars(75_000), LightIndustryProducts(500)))
    MOVES_BUDGET = 200

    @classmethod
    def base_hardness(cls) -> int:
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
                       .set_base_strength(3)
                       .set_additional_strength_getter(lambda coord, board: Tank.get_projected_strength(coord, board))
                       .build()),
                      Creatable.make(Dollars(500_000), LightIndustryProducts(5_000), HeavyIndustryProducts(1_000)),
                      Capturable(),
                      TriesTakeResourcesElseDies.make(Dollars(150_000),
                                                      LightIndustryProducts(1_000),
                                                      HeavyIndustryProducts(250)),
                      CanAttack(max_distance=1))
    MOVES_BUDGET = 200

    _PER_INFANTRY_STRENGTH_RATIO = .5
    _PER_INFANTRY_HARDNESS_RATIO = .5

    @classmethod
    def base_hardness(cls) -> int:
        return 2

    @classmethod
    def additional_hardness(cls, coord: Vector2Int, board: proto.Board) -> int:
        return cls._get_projected(coord, board, cls._PER_INFANTRY_HARDNESS_RATIO)

    @classmethod
    def get_cost_of(cls, move: proto.Move) -> int:
        match move:
            case Relocation():
                return 15
            case Assault():
                return 25
            case Attack():
                return 15
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
                      .set_base_strength(25)
                      .set_can_relocate(lambda from_coord, to_coord, board: False)
                      .build(),
                      Pullable(),
                      Creatable.make(Dollars(200_000), LightIndustryProducts(5_000), HeavyIndustryProducts(1_250)),
                      Capturable(),
                      TriesTakeResourcesElseDies.make(Dollars(100_000),
                                                      LightIndustryProducts(750),
                                                      HeavyIndustryProducts(300)),
                      CanAttack(max_distance=3))
    MOVES_BUDGET = 7

    @classmethod
    def base_hardness(cls) -> int:
        return 1

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
        LightFactory,
        HeavyFactory,
        Capital,
        Bunker,
        MissileSilo,
        Infantry,
        Motorization,
        Tank,
        Artillery
    ]
