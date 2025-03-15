from abc import ABC, abstractmethod
from typing import ClassVar

from vector import Vector2Int

INVALID = object()


class Master(ABC):
    @abstractmethod
    def is_turn_of(self, player: "Player") -> bool:
        ...


class Player(ABC):
    ...


class ValidMove(ABC):
    @property
    @abstractmethod
    def move(self) -> "Move":
        ...


class Move(ABC):
    @abstractmethod
    def validate(self, board: "Board") -> ValidMove | INVALID:
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
    def coordinates_of(self, cell: "Cell") -> Vector2Int:
        ...

    @abstractmethod
    def make(self, move: "ValidMove") -> None:
        ...

    @abstractmethod
    def __getitem__(self, item: Vector2Int) -> "Cell":
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

    @property
    @abstractmethod
    def strength(self) -> int:
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


class Figure(ABC):
    STRENGTH: ClassVar[int]


class StaticFigure(Figure, ABC):
    ...


class CreatableFigure(Figure, ABC):
    ...


class MovableFigure(Figure, ABC):
    ...
