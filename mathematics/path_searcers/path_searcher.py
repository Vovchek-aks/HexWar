from abc import ABC, abstractmethod
from typing import Iterator

from mathematics.vector import Vector2Int
import core.protocols as proto

Path = list[Vector2Int]


class PathSearcher(ABC):
    @abstractmethod
    def search_from(self, start_cell: proto.Cell) -> Path:
        ...

    @abstractmethod
    def search_process_from(self, start_cell: proto.Cell) -> Iterator[None | Path]:
        ...
