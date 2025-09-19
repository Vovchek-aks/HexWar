from abc import ABC, abstractmethod

from mathematics.angle import Angle
from mathematics.vector import Vector2, Vector2Int
from mathematics.hex_geometry import Neighbor
from statuses import Status


class Camera(ABC):
    @abstractmethod
    def world_to_screen(self, point: Vector2) -> Vector2:
        ...

    @abstractmethod
    def screen_to_world(self, point: Vector2) -> Vector2:
        ...


class CameraOrientation(ABC):
    @property
    @abstractmethod
    def position(self) -> Vector2:
        ...

    @property
    @abstractmethod
    def rotation(self) -> Angle:
        ...

    @property
    @abstractmethod
    def zoom(self) -> float:
        ...

    @property
    @abstractmethod
    def tuple(self) -> tuple[Vector2, Angle, float]:
        ...

    @abstractmethod
    def move(self, delta: Vector2) -> "CameraOrientation":
        ...

    @abstractmethod
    def rotate(self, angle: Angle) -> "CameraOrientation":
        ...

    @abstractmethod
    def zoom_in(self, ratio: float) -> "CameraOrientation":
        ...


class Draw:
    @abstractmethod
    def board(self) -> None:
        ...

    @abstractmethod
    def background(self) -> None:
        ...

    @abstractmethod
    def highlighted(self, cell_coord: Vector2Int) -> None:
        ...

    @abstractmethod
    def edge(self, cell_coord: Vector2Int, neighbor: Neighbor) -> None:
        ...

    @abstractmethod
    def edges(self, cell_coord: Vector2Int) -> None:
        ...

    @abstractmethod
    def hex_background(self, cell_coord: Vector2Int) -> None:
        ...


class SelectedCellGetter:
    @abstractmethod
    def get_coord(self, mouse_position: Vector2) -> Vector2Int | Status:
        ...
