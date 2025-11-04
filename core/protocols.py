from abc import ABC, abstractmethod, ABCMeta
from types import UnionType
from typing import ClassVar, Iterable

from observer import OnEventSubscriber
from statuses import Status
from mathematics.vector import Vector2Int
from color import Color


class Master(ABC):
    @abstractmethod
    def is_turn_of(self, player: "Player") -> bool:
        ...


class Player(ABC):
    @property
    @abstractmethod
    def color(self) -> Color:
        ...


class ValidMove(ABC):
    @property
    @abstractmethod
    def move(self) -> "Move":
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

    @abstractmethod
    def make(self, move: ValidMove) -> None:
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


class GameSession(ABC):
    @property
    @abstractmethod
    def master(self) -> Master:
        ...

    @property
    @abstractmethod
    def figures_budget(self) -> "FiguresBudget":
        ...

    @property
    @abstractmethod
    def board(self) -> Board:
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
    def take_from(self, other: "Cell") -> None:
        ...


class Cells(ABC):
    @abstractmethod
    def all(self) -> list[Cell]:
        ...

    @abstractmethod
    def with_owner(self, target: Player) -> "Cells":
        ...

    @abstractmethod
    def with_figure(self, target: type["Figure"] | UnionType) -> "Cells":
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
    def get_cost_of(cls, move: Move, board: Board) -> int:
        ...


class FiguresBudget(ABC):
    @abstractmethod
    def clear(self) -> None:
        ...

    @abstractmethod
    def of(self, figure: Figure) -> int:
        ...

    @abstractmethod
    def can_add(self, figure: Figure, pay_count: int) -> bool:
        ...

    @abstractmethod
    def add(self, figure: Figure, pay_count: int) -> None:
        ...


class FiguresGroup(ABC):
    ...


class FiguresMarket(ABC):
    ...


class FiguresMarketBuilder(ABC):
    @abstractmethod
    def register(self, figure: type[Figure], kind: FiguresGroup, price: int) -> None:
        ...

    @abstractmethod
    def build(self) -> FiguresMarket:
        ...
