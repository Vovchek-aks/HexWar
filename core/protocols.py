from abc import ABC, abstractmethod, ABCMeta
from types import UnionType, TracebackType
from typing import ClassVar, Iterable

from observer import OnEventSubscriber
from statuses import Status
from mathematics.vector import Vector2Int
from color import Color


class Master(ABC):
    @property
    @abstractmethod
    def turn_has_passed(self) -> OnEventSubscriber["Player", None]:
        ...

    @property
    @abstractmethod
    def current_player(self) -> "Player":
        ...

    @abstractmethod
    def pass_turn_to_next_player(self) -> None:
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
    def cell_changed_figure(self) -> OnEventSubscriber[Vector2Int, None]:
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
    def coordinates_of(self, cell: "Cell") -> Vector2Int:
        ...

    @abstractmethod
    def get_neighbors(self, cell: "Cell", *, include_cell: bool) -> "Cells":
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


class CellsCache(ABC):
    @property
    @abstractmethod
    def at_front(self) -> "Cells":
        ...

    @abstractmethod
    def with_owner(self, player: Player) -> "Cells":
        ...

    @abstractmethod
    def with_figure(self, figure: type["Figure"] | UnionType) -> "Cells":
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
    def board(self) -> Board:
        ...

    @property
    @abstractmethod
    def cells(self) -> CellsCache:
        ...

    @abstractmethod
    def make(self, move: "ValidMove") -> None:
        ...


class Cell(ABC):
    @property
    @abstractmethod
    def owner(self) -> "Player":
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
    def change_owner(self, player: Player) -> None:
        ...

    @abstractmethod
    def take_from(self, other: "Cell") -> None:
        ...


class Cells(ABC):
    @abstractmethod
    def all(self) -> set[Cell]:
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
    def at_front(self, board: Board) -> "Cells":
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
    def __bool__(self) -> bool:
        ...

    @abstractmethod
    def __iter__(self) -> Iterable[Cell]:
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


class CanCapture(Flag, metaclass=ABCMeta):
    ...


class Capturable(Flag, metaclass=ABCMeta):
    ...


class CanAttack(Flag, metaclass=ABCMeta):
    @property
    @abstractmethod
    def max_distance(self) -> int:
        ...


class Static(Flag, metaclass=ABCMeta):
    ...


class Movable(Flag, metaclass=ABCMeta):
    @abstractmethod
    def strength(self, coord: Vector2Int, board: Board) -> int:
        ...

    @abstractmethod
    def can_relocate(self, from_coord: Vector2Int, to_coord: Vector2Int, board: Board) -> bool:
        ...


class Creatable(Flag, metaclass=ABCMeta):
    @property
    @abstractmethod
    def cost(self) -> "Resource":
        ...


class UpdatableOnTurnStart(Flag, metaclass=ABCMeta):
    @abstractmethod
    def update(self, coord: Vector2Int, session: GameSession) -> None:
        ...


class Figure(ABC):
    FLAGS: ClassVar[Flags]
    MOVES_BUDGET: ClassVar[int]

    @classmethod
    @abstractmethod
    def hardness(cls, coord: Vector2Int, board: Board) -> int:
        ...

    @classmethod
    @abstractmethod
    def get_cost_of(cls, move: Move) -> int:
        ...


class FiguresRelocationBudget(ABC):
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


class ResourcesStockpile(ABC):
    @property
    @abstractmethod
    def has_changed(self) -> OnEventSubscriber["ResourcesStockpile", None]:
        ...

    @abstractmethod
    def get(self, target: type[Resource]) -> Resource:
        ...

    @abstractmethod
    def can_take(self, taken_resource: Resource) -> bool:
        ...

    @abstractmethod
    def add(self, additional_resource: Resource) -> None:
        ...

    @abstractmethod
    def take(self, taken_resource: Resource) -> None:
        ...
