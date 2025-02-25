from abc import ABC, abstractmethod


class Agent(ABC):
    ...


class Board(ABC):
    @property
    @abstractmethod
    def width(self) -> int:
        ...

    @property
    @abstractmethod
    def height(self) -> int:
        ...

    @abstractmethod
    def __getitem__(self, item: tuple[int, int]) -> "Cell":
        ...


class Cell(ABC):
    ...


class Figure(ABC):
    ...
