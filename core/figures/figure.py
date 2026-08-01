import random
from abc import ABCMeta
from typing import Callable

from attrs import define, field

from core import protocols as proto
from core.distant_neighbors_getter import DistantNeighborsGetter
from core.figures.figures_flags import Flags, Static, Creatable, CanCapture, Capturable, CanAttack, Pullable, \
    PreventsCaptures, CanPull, OnLand, AtWater, Empty, DontHaveOwner, CanLaunchOreshnik, StartsWithBudgetSpend, \
    PreventsAnnexations, Private, Transforms, CanGradAttack, CannotBeAttacked, TerrainMountain, TerrainForest, \
    TerrainSwamp, TerrainDesert
from core.figures.movable_flag import MovableBuilder
from core.figures.resources_flow_flags import TriesTakeResourcesElseDies, AddsResourcesIndefinably, \
    BuffsNearbyResourceAdders, TransformsResourcesIndefinably
from core.moves.attack import Attack
from core.moves.capture import Capture
from core.moves.grad_attack import GradAttack
from core.moves.oreshnik_launch import OreshnikLaunch
from core.moves.pulling import PullingInitiation, PullingTermination
from core.moves.relocations import Relocation, Assault
from core.resources import ResourcesGroup, Dollars, LightIndustryProducts, HeavyIndustryProducts
from exceptions import NotSupportedMove
from mathematics.vector import Vector2Int
from core.protocols import Figure, Board
from my_random import temporarily_seed


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


class Mountain(_Figure):
    FLAGS = Flags.new(OnLand(),
                      Static(),
                      Capturable(),
                      TerrainMountain(),
                      CannotBeAttacked())
    MOVES_BUDGET = 0

    @classmethod
    def base_hardness(cls) -> int:
        return 0

    @classmethod
    def get_cost_of(cls, move: proto.Move) -> int:
        return 0


class Forest(_Figure):
    FLAGS = Flags.new(OnLand(),
                      Static(),
                      Capturable(),
                      TerrainForest(),
                      CannotBeAttacked())
    MOVES_BUDGET = 0

    @classmethod
    def base_hardness(cls) -> int:
        return 0

    @classmethod
    def get_cost_of(cls, move: proto.Move) -> int:
        return 0


class Swamp(_Figure):
    FLAGS = Flags.new(OnLand(),
                      Static(),
                      Capturable(),
                      TerrainSwamp(),
                      CannotBeAttacked())
    MOVES_BUDGET = 0

    @classmethod
    def base_hardness(cls) -> int:
        return 0

    @classmethod
    def get_cost_of(cls, move: proto.Move) -> int:
        return 0


class Desert(_Figure):
    FLAGS = Flags.new(OnLand(),
                      Static(),
                      Capturable(),
                      TerrainDesert(),
                      CannotBeAttacked())
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


class Town(_Figure):
    FLAGS = Flags.new(OnLand(),
                      Static(),
                      Creatable.make(Dollars(700_000), LightIndustryProducts(1_000)),
                      Capturable(),
                      AddsResourcesIndefinably.make(Dollars(250_000)))
    MOVES_BUDGET = 198

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


class Settlement(_Figure):
    FLAGS = Flags.new(OnLand(),
                      Static(),
                      Private(),
                      Capturable(),
                      AddsResourcesIndefinably.make(Dollars(100_000)))
    MOVES_BUDGET = 1

    @classmethod
    def base_hardness(cls) -> int:
        return 0

    @classmethod
    def get_cost_of(cls, move: proto.Move) -> int:
        return 0


class PrivateLightFactory(_Figure):
    FLAGS = Flags.new(OnLand(),
                      Static(),
                      Private(),
                      Capturable(),
                      TransformsResourcesIndefinably(ResourcesGroup.make(Dollars(50_000)),
                                                     ResourcesGroup.make(LightIndustryProducts(350)),
                                                     priority=_get_transformer_of(LightFactory).priority + 1,
                                                     on_no_resources=lambda coord, session:
                                                     PrivateLightFactory.on_no_resources_getter(Abandonment)
                                                     (coord, session)))
    MOVES_BUDGET = 1

    _TURN_PROBABILITY = .5

    @classmethod
    def base_hardness(cls) -> int:
        return 0

    @classmethod
    def get_cost_of(cls, move: proto.Move) -> int:
        return 0

    @classmethod
    def on_no_resources_getter(cls,
                               figure_to_turn_into: type[Figure]
                               ) -> Callable[[Vector2Int, proto.GameSession], None]:
        def on_no_resources(coord: Vector2Int, session: proto.GameSession) -> None:
            cell = session.board[coord]

            with temporarily_seed((coord, session.master.current_turn)):
                if random.random() > cls._TURN_PROBABILITY:
                    return

            session.figures.remove(cell.figure)
            session.figures.add(figure_to_turn_into, coord)

        return on_no_resources


class PrivateHeavyFactory(_Figure):
    FLAGS = Flags.new(OnLand(),
                      Static(),
                      Private(),
                      Capturable(),
                      TransformsResourcesIndefinably(ResourcesGroup.make(Dollars(250_000),
                                                                         LightIndustryProducts(1_500)),
                                                     ResourcesGroup.make(HeavyIndustryProducts(350)),
                                                     priority=_get_transformer_of(PrivateLightFactory).priority + 1,
                                                     on_no_resources=lambda coord, session:
                                                     PrivateLightFactory.on_no_resources_getter(Abandonment)
                                                     (coord, session)))
    MOVES_BUDGET = 1

    @classmethod
    def base_hardness(cls) -> int:
        return 0

    @classmethod
    def get_cost_of(cls, move: proto.Move) -> int:
        return 0


class TierOneCapital(_Figure):
    FLAGS = Flags.new(OnLand(),
                      Static(),
                      Capturable(),
                      PreventsAnnexations(distance=10,
                                          can_prevent=lambda coord, session, region:
                                          TierOneCapital.can_prevent(coord, session, region)),
                      Creatable.make(Dollars(2_000_000), LightIndustryProducts(7_500)),
                      TriesTakeResourcesElseDies.make(Dollars(800_000)),
                      BuffsNearbyResourceAdders(additional_ratio=1))
    MOVES_BUDGET = 1

    @classmethod
    def base_hardness(cls) -> int:
        return 0

    @classmethod
    def get_cost_of(cls, move: proto.Move) -> int:
        return 1

    @classmethod
    def can_prevent(cls, _: Vector2Int, __: proto.GameSession, region: proto.Cells) -> bool:
        return len(region) > 1


class TallCapital(_Figure):
    FLAGS = Flags.new(OnLand(),
                      Static(),
                      Capturable(),
                      PreventsAnnexations(distance=15,
                                          can_prevent=lambda coord, session, region:
                                          TierOneCapital.can_prevent(coord, session, region)),
                      TriesTakeResourcesElseDies.make(Dollars(1_000_000),
                                                      LightIndustryProducts(1_000),
                                                      HeavyIndustryProducts(200)),
                      BuffsNearbyResourceAdders(additional_ratio=2))
    MOVES_BUDGET = 0

    @classmethod
    def base_hardness(cls) -> int:
        return 0

    @classmethod
    def get_cost_of(cls, move: proto.Move) -> int:
        return 0


class WideCapital(_Figure):
    FLAGS = Flags.new(OnLand(),
                      Static(),
                      Capturable(),
                      PreventsAnnexations(distance=20,
                                          can_prevent=lambda coord, session, region:
                                          TierOneCapital.can_prevent(coord, session, region)),
                      TriesTakeResourcesElseDies.make(Dollars(1_000_000),
                                                      LightIndustryProducts(1_000),
                                                      HeavyIndustryProducts(200)),
                      BuffsNearbyResourceAdders(additional_ratio=1, distance=2))
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
                      PreventsCaptures(),
                      Transforms(lambda coord, session: Bunker.get_target(coord, session)),
                      Creatable.make(Dollars(150_000), LightIndustryProducts(250)))
    MOVES_BUDGET = 0

    _FROM_FRONT_MAX_DISTANCE = 3
    _TURN_PROBABILITY = .3

    @classmethod
    def base_hardness(cls) -> int:
        return 5

    @classmethod
    def get_cost_of(cls, move: proto.Move) -> int:
        return 0

    @classmethod
    def get_target(cls, coord: Vector2Int, session: proto.GameSession) -> type[proto.Figure]:
        board = session.board
        cell = board[coord]

        neighbors = (DistantNeighborsGetter(cell, board)
                     .get_all_not_farther_than(cls._FROM_FRONT_MAX_DISTANCE, include_cell=True))
        if neighbors & session.cells.at_front:
            return Bunker

        with temporarily_seed((coord, session.master.current_turn)):
            if random.random() > cls._TURN_PROBABILITY:
                return Bunker

        return Abandonment


class MissileSilo(_Figure):
    FLAGS = Flags.new(OnLand(),
                      Static(),
                      Creatable.make(Dollars(1_500_000), LightIndustryProducts(10_000), HeavyIndustryProducts(5_000)),
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


class Abandonment(_Figure):
    FLAGS = Flags.new(OnLand(),
                      Static(),
                      Capturable(),
                      AddsResourcesIndefinably.make(Dollars(-25_000)))
    MOVES_BUDGET = 0

    @classmethod
    def base_hardness(cls) -> int:
        return 0

    @classmethod
    def get_cost_of(cls, move: proto.Move) -> int:
        return 0


class Infantry(_Figure):
    FLAGS = Flags.new(OnLand(),
                      (MovableBuilder()
                       .can_move_to_neighbor()
                       .set_base_strength(3)
                       .build()),
                      CanPull(),
                      PreventsAnnexations(distance=3,
                                          can_prevent=lambda coord, session, region:
                                          Infantry.can_prevent(coord, session, region)),
                      Creatable.make(Dollars(200_000)),
                      CanCapture(),
                      PreventsCaptures(),
                      TriesTakeResourcesElseDies.make(Dollars(50_000)))
    MOVES_BUDGET = 198

    _NEAR_BUNKER_HARDNESS_INCREASE = 5

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
    def can_prevent(cls, coord: Vector2Int, session: proto.GameSession, region: proto.Cells) -> bool:
        board = session.board
        cell = board[coord]
        if region & session.cells.with_figure(Capital):
            return True

        distance = cls.FLAGS.get(PreventsAnnexations).distance
        cells = (DistantNeighborsGetter(cell, board)
                 .get_all_not_farther_than(distance - 1, include_cell=True)
                 & region)
        return bool(cells
                    .at_outer_boundry(board)
                    .with_flag(AtWater))

    @classmethod
    def get_cost_of(cls, move: proto.Move) -> int:
        match move:
            case Relocation():
                return 33
            case Assault():
                return 66
            case Capture():
                return 66
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
                      PreventsAnnexations(distance=Infantry.FLAGS.get(PreventsAnnexations).distance,
                                          can_prevent=lambda coord, session, region:
                                          Infantry.can_prevent(coord, session, region)),
                      PreventsCaptures(),
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
                       .set_base_strength(4)
                       .set_additional_strength_getter(lambda coord, board: Tank.get_projected_strength(coord, board))
                       .build()),
                      Creatable.make(Dollars(750_000), LightIndustryProducts(5_000), HeavyIndustryProducts(1_500)),
                      Capturable(),
                      TriesTakeResourcesElseDies.make(Dollars(250_000),
                                                      LightIndustryProducts(1_000),
                                                      HeavyIndustryProducts(500)),
                      CanAttack(max_distance=1))
    MOVES_BUDGET = 200

    _PER_INFANTRY_STRENGTH_RATIO = .5
    _PER_INFANTRY_HARDNESS_RATIO = .5

    @classmethod
    def base_hardness(cls) -> int:
        return 3

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
                      Creatable.make(Dollars(200_000), LightIndustryProducts(3_000)),
                      Capturable(),
                      TriesTakeResourcesElseDies.make(Dollars(100_000),
                                                      LightIndustryProducts(750)),
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


class Howitzer(_Figure):
    FLAGS = Flags.new(OnLand(),
                      MovableBuilder()
                      .set_base_strength(Artillery.FLAGS.get(proto.Movable).base_strength)
                      .can_move_to_neighbor()
                      .build(),
                      Capturable(),
                      TriesTakeResourcesElseDies.make(Dollars(300_000),
                                                      LightIndustryProducts(1_000),
                                                      HeavyIndustryProducts(750)),
                      CanAttack(max_distance=3))
    MOVES_BUDGET = 200

    @classmethod
    def base_hardness(cls) -> int:
        return 1

    @classmethod
    def get_cost_of(cls, move: proto.Move) -> int:
        match move:
            case Relocation():
                return 15
            case Assault():
                return cls.MOVES_BUDGET + 1
            case Attack():
                return 50
            case _:
                raise NotSupportedMove(move)


class Grad(_Figure):
    FLAGS = Flags.new(OnLand(),
                      MovableBuilder()
                      .set_base_strength(Artillery.FLAGS.get(proto.Movable).base_strength)
                      .can_move_to_neighbor()
                      .build(),
                      Capturable(),
                      TriesTakeResourcesElseDies.make(Dollars(200_000),
                                                      LightIndustryProducts(500)),
                      CanGradAttack(max_distance=5,
                                    targets_count=3,
                                    is_attacking_center=False,
                                    cost=ResourcesGroup.make(LightIndustryProducts(500))))
    MOVES_BUDGET = 20

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
            case GradAttack():
                return 15
            case _:
                raise NotSupportedMove(move)


Capital = TierOneCapital | TallCapital | WideCapital


def get_figures() -> list[type[_Figure]]:
    return [
        Land,
        Mountain,
        Forest,
        Swamp,
        Desert,
        Water,
        Town,
        LightFactory,
        HeavyFactory,
        Settlement,
        PrivateLightFactory,
        PrivateHeavyFactory,
        TierOneCapital,
        TallCapital,
        WideCapital,
        Bunker,
        MissileSilo,
        Abandonment,
        Infantry,
        Motorization,
        Tank,
        Artillery,
        Howitzer,
        Grad,
    ]


def get_producers() -> list[type[_Figure]]:
    return [figure for figure in get_figures()
            if proto.ResourcesAdder in figure.FLAGS]
