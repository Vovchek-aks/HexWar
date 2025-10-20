from abc import ABC, abstractmethod

from mathematics.angle import Angle
from mathematics.vector import Vector2, Vector2Int
from mathematics.hex_geometry import Neighbor
from statuses import Status
from appearance.graphics.sprites import Sprite
import core.protocols as proto


class Camera(ABC):
    @property
    @abstractmethod
    def orientation(self) -> "ReadonlyCameraOrientation":
        ...

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


class ReadonlyCameraOrientation(ABC):
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


class Draw(ABC):
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
    def figures(self) -> None:
        ...


class FiguresDrawer(ABC):
    @abstractmethod
    def draw_figures(self) -> None:
        ...


class FiguresSprites(ABC):
    @abstractmethod
    def get(self, figure: type[proto.Figure]) -> Sprite:
        ...


class BordDrawer(ABC):
    @abstractmethod
    def draw_board(self) -> None:
        ...

    @abstractmethod
    def draw_background(self) -> None:
        ...

    @abstractmethod
    def draw_highlighted(self, cell_coord: Vector2Int) -> None:
        ...

    @abstractmethod
    def draw_edge(self, cell_coord: Vector2Int, neighbor: Neighbor) -> None:
        ...

    @abstractmethod
    def draw_edges(self, cell_coord: Vector2Int) -> None:
        ...

    @abstractmethod
    def draw_hex_background(self, cell_coord: Vector2Int) -> None:
        ...


class SelectedCellGetter(ABC):
    @abstractmethod
    def get_coord(self, mouse_position: Vector2) -> Vector2Int | Status:
        ...


class Click(ABC):
    @property
    @abstractmethod
    def screen_position(self) -> Vector2:
        ...

    @property
    @abstractmethod
    def is_left(self) -> bool:
        ...

    @property
    @abstractmethod
    def is_right(self) -> bool:
        ...

    @property
    @abstractmethod
    def is_middle(self) -> bool:
        ...


class ClicksCatchingLayer(ABC):
    @abstractmethod
    def can_catch(self, click: Click) -> bool:
        ...

    @abstractmethod
    def catch(self, click: Click) -> None:
        ...
