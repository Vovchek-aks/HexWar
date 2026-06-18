from abc import ABC, abstractmethod, ABCMeta
from types import UnionType, TracebackType
from typing import ClassVar, Iterable, Iterator, Callable, Hashable

from observer import OnEventSubscriber
from statuses import Status
from mathematics.vector import Vector2Int
from color import Color


class Master(ABC):
    @property
    @abstractmethod
    def current_turn(self) -> int:
        ...

    @property
    @abstractmethod
    def players(self) -> list["Player"]:
        ...

    @property
    @abstractmethod
    def current_player(self) -> "Player":
        ...

    @property
    @abstractmethod
    def next_player(self) -> "Player":
        ...

    @property
    @abstractmethod
    def turn_had_started(self) -> OnEventSubscriber["Player", None]:
        ...

    @property
    @abstractmethod
    def turn_has_passed(self) -> OnEventSubscriber["Player", None]:
        ...

    @abstractmethod
    def pass_turn_to_next_player(self, session: "GameSession") -> None:
        ...


class ValidMove(ABC):
    @property
    @abstractmethod
    def move(self) -> "Move":
        ...


class PlayerData(ABC):
    @property
    @abstractmethod
    def color(self) -> Color:
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...


class PlayerInputer(ABC):
    @abstractmethod
    def get_move(self, session: "GameSession") -> ValidMove | Status:
        ...

    @abstractmethod
    def wants_to_end_turn(self) -> bool:
        ...

    @abstractmethod
    def __enter__(self) -> "PlayerInputer":
        ...

    @abstractmethod
    def __exit__(self,
                 exc_type: type[BaseException],
                 exc_val: BaseException,
                 exc_tb: TracebackType) -> bool | None:
        ...


class Player(ABC):
    @property
    @abstractmethod
    def data(self) -> PlayerData:
        ...

    @property
    @abstractmethod
    def inputer(self) -> PlayerInputer:
        ...

    @property
    @abstractmethod
    def need_ui(self) -> bool:
        ...

    @property
    @abstractmethod
    def resources(self) -> "ResourcesStockpile":
        ...

    @abstractmethod
    def change_inputer(self, inputer: PlayerInputer) -> None:
        ...


class Bot:
    @abstractmethod
    def get_move(self, session: "GameSession") -> ValidMove | Status:
        ...


class Move(ABC):
    @abstractmethod
    def validate(self, session: "GameSession") -> ValidMove | Status:
        ...

    @abstractmethod
    def execute(self, session: "GameSession") -> None:
        ...


class MovesMaker(ABC):
    @property
    @abstractmethod
    def move_was_made(self) -> OnEventSubscriber[ValidMove, None]:
        ...

    @property
    @abstractmethod
    def board_move_was_made(self) -> OnEventSubscriber[ValidMove, None]:
        ...

    @property
    @abstractmethod
    def cell_changed_owner(self) -> OnEventSubscriber[Vector2Int, None]:
        ...

    @property
    @abstractmethod
    def resources_flow_could_have_changed(self) -> OnEventSubscriber[None]:
        ...

    @property
    @abstractmethod
    def cells_to_annex_could_have_changed(self) -> OnEventSubscriber[None]:
        ...

    @abstractmethod
    def make(self, move: ValidMove) -> None:
        ...


class CellsChangesObserver(ABC):
    @property
    @abstractmethod
    def cell_changed_owner(self) -> OnEventSubscriber[Vector2Int, None]:
        ...

    @property
    @abstractmethod
    def cell_changed_figure(self) -> OnEventSubscriber[Vector2Int, None]:
        ...


class Board(ABC):
    @property
    @abstractmethod
    def shape(self) -> Vector2Int:
        ...

    @property
    @abstractmethod
    def width(self) -> int:
        ...

    @property
    @abstractmethod
    def height(self) -> int:
        ...

    @property
    @abstractmethod
    def cells(self) -> "Cells":
        ...

    @property
    @abstractmethod
    def cell_coords(self) -> Iterable[Vector2Int]:
        ...

    @abstractmethod
    def has(self, cell: "Cell") -> bool:
        ...

    @abstractmethod
    def is_on_boundry(self, cell: "Cell") -> bool:
        ...

    @abstractmethod
    def coordinates_of(self, cell: "Cell") -> Vector2Int:
        ...

    @abstractmethod
    def get_neighbors(self, cell: "Cell", *, include_cell: bool = False) -> "Cells":
        ...

    @abstractmethod
    def get_region_with_same_owner(self, cell: "Cell") -> "Cells":
        ...

    @abstractmethod
    def at(self, coord: Vector2Int) -> "Cell":
        ...

    @abstractmethod
    def __getitem__(self, coord: Vector2Int) -> "Cell":
        ...

    @abstractmethod
    def __iter__(self) -> Iterable[Vector2Int]:
        ...

    @abstractmethod
    def __contains__(self, coord: Vector2Int) -> bool:
        ...


class AnnexationMap(ABC):
    @abstractmethod
    def get_cells_to_annex_of(self, player: Player) -> "Cells":
        ...

    @abstractmethod
    def update_for(self, player: Player, *, initial_frame_skips: int = 0) -> Iterator[None]:
        ...

    @abstractmethod
    def __contains__(self, cell: "Cell") -> bool:
        ...


class AnnexationMapUpdater(ABC):
    @property
    @abstractmethod
    def is_active(self) -> bool:
        ...

    @property
    @abstractmethod
    def map(self) -> AnnexationMap:
        ...

    @property
    @abstractmethod
    def update_for_player_was_requested(self) -> OnEventSubscriber[Player, None]:
        ...

    @property
    @abstractmethod
    def update_for_player_was_started(self) -> OnEventSubscriber[Player, None]:
        ...

    @property
    @abstractmethod
    def update_for_player_was_finished(self) -> OnEventSubscriber[Player, None]:
        ...

    @abstractmethod
    def is_about_to_be_updated(self, player: Player) -> bool:
        ...

    @abstractmethod
    def update(self) -> None:
        ...

    @abstractmethod
    def append(self, player: Player) -> None:
        ...

    @abstractmethod
    def push(self, player: Player) -> None:
        ...


class CellsCache(ABC):
    @property
    @abstractmethod
    def at_front(self) -> "Cells":
        ...

    @abstractmethod
    def with_flag(self, flag: "type[Flag] | UnionType") -> "Cells":
        ...

    @abstractmethod
    def get_static_control_zone_of(self, cell: "Cell") -> "Cells":
        ...

    @abstractmethod
    def not_empty(self) -> "Cells":
        ...

    @abstractmethod
    def with_owner(self, player: Player) -> "Cells":
        ...

    @abstractmethod
    def with_figure(self, figure: type["Figure"] | UnionType) -> "Cells":
        ...

    @abstractmethod
    def get_all_players(self) -> "Cells":
        ...

    @abstractmethod
    def get_territories_and_production_ratios_of(self, player: Player) -> tuple[float, float]:
        ...

    @abstractmethod
    def update_fully(self) -> None:
        ...

    @abstractmethod
    def update(self, cell: "Cell") -> None:
        ...


class GameSession(ABC):
    @property
    @abstractmethod
    def master(self) -> Master:
        ...

    @property
    @abstractmethod
    def figures_budget(self) -> "FiguresRelocationBudget":
        ...

    @property
    @abstractmethod
    def pulling_connections(self) -> "PullingConnections":
        ...

    @property
    @abstractmethod
    def board(self) -> Board:
        ...

    @property
    @abstractmethod
    def cells(self) -> CellsCache:
        ...

    @property
    @abstractmethod
    def figures(self) -> "Figures":
        ...

    @abstractmethod
    def make(self, move: "ValidMove") -> None:
        ...


class ByGameRulesSessionChanger(ABC):
    @abstractmethod
    def on_turn_start(self) -> None:
        ...

    @abstractmethod
    def on_turn_end(self) -> None:
        ...

    @abstractmethod
    def annex(self, region: "Cells") -> None:
        ...


class Cell(ABC):
    @property
    @abstractmethod
    def owner(self) -> "Player | Status":
        ...

    @property
    @abstractmethod
    def figure(self) -> "Figure":
        ...

    @property
    @abstractmethod
    def is_empty(self) -> bool:
        ...

    @abstractmethod
    def hardness(self, board: Board) -> int:
        ...

    @abstractmethod
    def strength(self, board: Board, *, strict: bool = True) -> int:
        ...

    @abstractmethod
    def pop(self) -> "Figure":
        ...

    @abstractmethod
    def insert(self, figure: "Figure") -> None:
        ...

    @abstractmethod
    def change_owner_to(self, player: Player) -> None:
        ...

    @abstractmethod
    def take_from(self, other: "Cell") -> None:
        ...

    @abstractmethod
    def turn_into_water(self) -> None:
        ...

    @abstractmethod
    def turn_into_land(self, owner: Player) -> None:
        ...


class Cells(ABC):
    @property
    @abstractmethod
    def any(self) -> Cell:
        ...

    @abstractmethod
    def as_set(self) -> set[Cell]:
        ...

    @abstractmethod
    def as_list(self) -> list[Cell]:
        ...

    @abstractmethod
    def without(self, cell: Cell) -> "Cells":
        ...

    @abstractmethod
    def with_owner(self, target: Player) -> "Cells":
        ...

    @abstractmethod
    def with_figure(self, target: type["Figure"] | UnionType) -> "Cells":
        ...

    @abstractmethod
    def with_flag(self, target: type["Flag"] | UnionType) -> "Cells":
        ...

    @abstractmethod
    def filter(self, function: Callable[[Cell], bool]) -> "Cells":
        ...

    @abstractmethod
    def group_by[T: Hashable](self, function: Callable[[Cell], T]) -> "dict[T, Cells]":
        ...

    @abstractmethod
    def players(self) -> set[Player]:
        ...

    @abstractmethod
    def is_region_with_same_owner(self, board: Board) -> bool:
        ...

    @abstractmethod
    def get_neighbor_regions(self, board: Board) -> "list[Cells]":
        ...

    @abstractmethod
    def split(self, board: Board) -> "list[Cells]":
        ...

    @abstractmethod
    def get_connected_to(self, cell: Cell, board: Board) -> "Cells":
        ...

    @abstractmethod
    def at_front(self, board: Board) -> "Cells":
        ...

    @abstractmethod
    def at_outer_boundry(self, board: Board) -> "Cells":
        ...

    @abstractmethod
    def at_inner_boundry(self, board: Board) -> "Cells":
        ...

    @abstractmethod
    def __add__(self, other_cells: "Cells") -> "Cells":
        ...

    @abstractmethod
    def __sub__(self, other_cells: "Cells") -> "Cells":
        ...

    @abstractmethod
    def __and__(self, other_cells: "Cells") -> "Cells":
        ...

    @abstractmethod
    def __gt__(self, other_cells: "Cells") -> bool:
        ...

    @abstractmethod
    def __ge__(self, other: "Cells") -> bool:
        ...

    @abstractmethod
    def __bool__(self) -> bool:
        ...

    @abstractmethod
    def __iter__(self) -> Iterator[Cell]:
        ...

    @abstractmethod
    def __len__(self) -> int:
        ...

    @abstractmethod
    def __contains__(self, cell: Cell) -> bool:
        ...


class Flag(ABC):
    EXCLUDES: set[type["Flag"]]


class Flags(ABC):
    @classmethod
    @abstractmethod
    def new(cls, *flags: Flag) -> "Flags":
        ...

    @property
    @abstractmethod
    def flag_types(self) -> set[type[Flag]]:
        ...

    @abstractmethod
    def get[T: Flag](self, flag_type: type[T]) -> T | Status:
        ...

    @abstractmethod
    def __contains__(self, item: type[Flag]) -> bool:
        ...


class Empty(Flag, metaclass=ABCMeta):
    ...


class OnLand(Flag, metaclass=ABCMeta):
    ...


class AtWater(Flag, metaclass=ABCMeta):
    ...


class CanCapture(Flag, metaclass=ABCMeta):
    ...


class Capturable(Flag, metaclass=ABCMeta):
    ...


class PreventsCaptures(Flag, metaclass=ABCMeta):
    ...


class CanAttack(Flag, metaclass=ABCMeta):
    @property
    @abstractmethod
    def max_distance(self) -> int:
        ...


class StartsWithBudgetSpend(Flag, metaclass=ABCMeta):
    @property
    @abstractmethod
    def amount(self) -> int:
        ...


class CanLaunchOreshnik(Flag, metaclass=ABCMeta):
    @property
    @abstractmethod
    def min_distance(self) -> int:
        ...

    @property
    @abstractmethod
    def cost(self) -> "ResourcesGroup":
        ...

    @property
    @abstractmethod
    def spread_radius(self) -> int:
        ...

    @property
    @abstractmethod
    def targets_per_layer(self) -> int:
        ...


class Static(Flag, metaclass=ABCMeta):
    ...


class DontHaveOwner(Flag, metaclass=ABCMeta):
    ...


class Movable(Flag, metaclass=ABCMeta):
    @property
    @abstractmethod
    def base_strength(self) -> int:
        ...

    @abstractmethod
    def strength(self, coord: Vector2Int, board: Board) -> int:
        ...

    @abstractmethod
    def can_relocate(self, from_coord: Vector2Int, to_coord: Vector2Int, board: Board) -> bool:
        ...


class Pullable(Flag, metaclass=ABCMeta):
    ...


class CanPull(Flag, metaclass=ABCMeta):
    ...


class Private(Flag, metaclass=ABCMeta):
    ...


class Creatable(Flag, metaclass=ABCMeta):
    @property
    @abstractmethod
    def cost(self) -> "ResourcesGroup":
        ...


class PreventsAnnexations(Flag, metaclass=ABCMeta):
    @property
    @abstractmethod
    def distance(self) -> int:
        ...

    @abstractmethod
    def can_prevent(self, coord: Vector2Int, session: GameSession, region: Cells) -> bool:
        ...


class TurnsOthersIntoItself(Flag, metaclass=ABCMeta):
    @abstractmethod
    def get_targets(self, coord: Vector2Int, session: GameSession) -> Cells:
        ...


class UpdatableOnTurnStart(Flag, metaclass=ABCMeta):
    @property
    @abstractmethod
    def priority(self) -> int:
        ...

    @abstractmethod
    def update(self, coord: Vector2Int, session: GameSession) -> None:
        ...


class ResourcesChanger(UpdatableOnTurnStart, metaclass=ABCMeta):
    @property
    @abstractmethod
    def changeable_resources(self) -> "set[type[Resource]]":
        ...


class ResourcesTaker(ResourcesChanger, metaclass=ABCMeta):
    @property
    @abstractmethod
    def resources_to_take(self) -> "ResourcesGroup":
        ...


class TriesTakeResourcesElseDies(ResourcesTaker, metaclass=ABCMeta):
    ...


class ResourcesAdder(ResourcesChanger, metaclass=ABCMeta):
    @property
    @abstractmethod
    def base_resources(self) -> "ResourcesGroup":
        ...

    @abstractmethod
    def get_resources_with_buffs(self, coord: Vector2Int, session: GameSession) -> "ResourcesGroup":
        ...


class AddsResourcesIndefinably(ResourcesAdder, metaclass=ABCMeta):
    ...


class TransformsResourcesIndefinably(ResourcesAdder, metaclass=ABCMeta):
    @property
    @abstractmethod
    def input_resources(self) -> "ResourcesGroup":
        ...


class BuffsResourceAdders(Flag, metaclass=ABCMeta):
    @abstractmethod
    def get_buff(self,
                 resources_adder_coord: Vector2Int,
                 coord: Vector2Int,
                 session: GameSession) -> float:
        ...


class BuffsNearbyResourceAdders(BuffsResourceAdders, metaclass=ABCMeta):
    @property
    @abstractmethod
    def additional_ratio(self) -> float:
        ...

    @property
    @abstractmethod
    def distance(self) -> int:
        ...


class Figure(ABC):
    FLAGS: ClassVar[Flags]
    MOVES_BUDGET: ClassVar[int]

    @classmethod
    @abstractmethod
    def is_on_land(cls) -> bool:
        ...

    @classmethod
    @abstractmethod
    def base_hardness(cls) -> int:
        ...

    @classmethod
    @abstractmethod
    def additional_hardness(cls, coord: Vector2Int, board: Board) -> int:
        ...

    @classmethod
    @abstractmethod
    def hardness(cls, coord: Vector2Int, board: Board) -> int:
        ...

    @classmethod
    @abstractmethod
    def get_cost_of(cls, move: Move) -> int:
        ...


class Figures(ABC):
    @property
    @abstractmethod
    def figure_was_added_at(self) -> OnEventSubscriber[Figure, Vector2Int, None]:
        ...

    @property
    @abstractmethod
    def figure_was_removed(self) -> OnEventSubscriber[Figure, Vector2Int, None]:
        ...

    @property
    @abstractmethod
    def figure_was_moved(self) -> OnEventSubscriber[Figure, Vector2Int, Vector2Int, None]:
        ...

    @property
    @abstractmethod
    def figure_was_converted(self) -> OnEventSubscriber[Figure, Figure, Vector2Int, None]:
        ...

    @abstractmethod
    def locate(self, figure: Figure) -> Vector2Int:
        ...

    @abstractmethod
    def add(self, figure_type: type[Figure], coord: Vector2Int) -> None:
        ...

    @abstractmethod
    def remove_at(self, coord: Vector2Int) -> None:
        ...

    @abstractmethod
    def remove(self, figure: Figure) -> None:
        ...

    @abstractmethod
    def move(self, figure: Figure, target: Vector2Int) -> None:
        ...

    @abstractmethod
    def convert(self, figure: Figure, target_type: type[Figure]) -> None:
        ...


class FiguresRelocationBudget(ABC):
    @property
    @abstractmethod
    def figures_bills(self) -> dict[Figure, int]:
        ...

    @abstractmethod
    def clear(self) -> None:
        ...

    @abstractmethod
    def pop(self, figure: Figure) -> int:
        ...

    @abstractmethod
    def of(self, figure: Figure) -> int:
        ...

    @abstractmethod
    def can_spend(self, figure: Figure, pay_count: int) -> bool:
        ...

    @abstractmethod
    def add(self, figure: Figure, pay_count: int) -> None:
        ...


class PullingConnections(ABC):
    @property
    @abstractmethod
    def pullable_of(self) -> dict[Figure, Figure]:
        ...

    @property
    @abstractmethod
    def pair_added(self) -> OnEventSubscriber[Figure, Figure, None]:
        ...

    @property
    @abstractmethod
    def pair_removed(self) -> OnEventSubscriber[Figure, Figure, None]:
        ...

    @abstractmethod
    def register(self, puller: Figure, pullable: Figure) -> None:
        ...

    @abstractmethod
    def unregister(self, puller: Figure, pullable: Figure) -> None:
        ...

    @abstractmethod
    def get_connected(self, figure: Figure) -> Figure | Status:
        ...

    @abstractmethod
    def is_puller(self, figure: Figure) -> bool:
        ...

    @abstractmethod
    def is_pullable(self, figure: Figure) -> bool:
        ...

    @abstractmethod
    def get_pullable(self, puller: Figure) -> Figure:
        ...

    @abstractmethod
    def get_puller(self, pullable: Figure) -> Figure:
        ...

    @abstractmethod
    def __contains__(self, item: tuple[Figure, Figure]) -> bool:
        ...


class Resource(ABC):
    @property
    @abstractmethod
    def amount(self) -> int:
        ...

    @abstractmethod
    def __add__(self, other: "Resource") -> "Resource":
        ...

    @abstractmethod
    def __sub__(self, other: "Resource") -> "Resource":
        ...

    @abstractmethod
    def __mul__(self, multiplier: float) -> "Resource":
        ...

    @abstractmethod
    def __neg__(self) -> "Resource":
        ...

    @abstractmethod
    def __bool__(self) -> bool:
        ...


class ResourcesGroup(ABC):
    @property
    @abstractmethod
    def not_zero(self) -> list[Resource]:
        ...

    @abstractmethod
    def get(self, target: type[Resource]) -> Resource:
        ...

    @abstractmethod
    def __add__(self, other: "ResourcesGroup") -> "ResourcesGroup":
        ...

    @abstractmethod
    def __sub__(self, other: "ResourcesGroup") -> "ResourcesGroup":
        ...

    @abstractmethod
    def __mul__(self, multiplier: float) -> "ResourcesGroup":
        ...

    @abstractmethod
    def __ge__(self, other: "ResourcesGroup") -> bool:
        ...

    @abstractmethod
    def __bool__(self) -> bool:
        ...

    @abstractmethod
    def __iter__(self) -> Iterator[Resource]:
        ...


class ResourcesStockpile(ABC):
    @property
    @abstractmethod
    def has_changed(self) -> OnEventSubscriber["ResourcesStockpile", None]:
        ...

    @property
    @abstractmethod
    def as_group(self) -> ResourcesGroup:
        ...

    @abstractmethod
    def get(self, target: type[Resource]) -> Resource:
        ...

    @abstractmethod
    def can_take(self, resources_to_take: ResourcesGroup) -> bool:
        ...

    @abstractmethod
    def add(self, additional_resources: ResourcesGroup) -> None:
        ...

    @abstractmethod
    def take(self, resources_to_take: ResourcesGroup) -> None:
        ...
