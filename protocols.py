from abc import ABC, abstractmethod
from typing import ClassVar

from vector import Vector2Int


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
    def validate(self, master: Master, board: "Board") -> ValidMove | None:
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
    def strength(self) -> int:
        ...

    @abstractmethod
    def pop_figure(self) -> "Figure":
        ...

    @abstractmethod
    def take_from(self, other: "Cell") -> None:
        ...


class Figure(ABC):
    STRENGTH: ClassVar[int]


class StaticFigure(ABC, Figure):
    ...


class MovableFigure(ABC, Figure):
    ...
