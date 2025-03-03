from abc import ABC, abstractmethod
from typing import ClassVar

from vector import Vector2Int


class Agent(ABC):
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
    def __getitem__(self, item: Vector2Int) -> "Cell":
        ...


class Cell(ABC):
    @property
    @abstractmethod
    def controlling(self) -> "Agent":
        ...

    @property
    @abstractmethod
    def figure(self) -> "Figure":
        ...


class Figure(ABC):
    STRENGTH: ClassVar[int]


class FigureStatic(Figure):
    ...


class FigureMovable(Figure):
    ...
