from abc import ABC, abstractmethod, ABCMeta
from typing import ClassVar, Iterable

import pygame as pg

from statuses import Status
from mathematics.vector import Vector2Int


class Master(ABC):
    @abstractmethod
    def is_turn_of(self, player: "Player") -> bool:
        ...


class Player(ABC):
    @property
    @abstractmethod
    def color(self) -> pg.Color:
        ...


class ValidMove(ABC):
    @property
    @abstractmethod
    def move(self) -> "Move":
        ...


class Move(ABC):
    @abstractmethod
    def validate(self, board: "Board") -> ValidMove | Status:
        ...

    @abstractmethod
    def execute(self, board: "Board") -> None:
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

    @abstractmethod
    def has_cell(self, cell: "Cell") -> bool:
        ...

    @abstractmethod
    def coordinates_of(self, cell: "Cell") -> Vector2Int:
        ...

    @abstractmethod
    def make(self, move: "ValidMove") -> None:
        ...

    @abstractmethod
    def get_neighbors(self, cell: "Cell", *, include_cell: bool) -> list["Cell"]:
        ...

    @abstractmethod
    def get_all_coords(self) -> Iterable[Vector2Int]:
        ...

    @abstractmethod
    def __getitem__(self, coord: Vector2Int) -> "Cell":
        ...

    @abstractmethod
    def __contains__(self, coord: Vector2Int) -> bool:
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
    def strength(self, board: "Board") -> int:
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
    ...


class Creatable(Flag, metaclass=ABCMeta):
    ...


class Figure(ABC):
    STRENGTH: ClassVar[int]
    FLAGS: ClassVar[Flags]


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
