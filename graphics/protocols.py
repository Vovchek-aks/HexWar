from abc import ABC, abstractmethod

import pygame as pg

from angle import Angle


class Camera(ABC):
    @abstractmethod
    def world_to_screen(self, point: pg.Vector2) -> pg.Vector2:
        ...


class CameraOrientation(ABC):
    @property
    @abstractmethod
    def position(self) -> pg.Vector2:
        ...

    @property
    @abstractmethod
    def rotation(self) -> Angle:
        ...

    @property
    @abstractmethod
    def zoom(self) -> float:
        ...

    @abstractmethod
    def move(self, delta: pg.Vector2) -> "CameraOrientation":
        ...

    @abstractmethod
    def rotate(self, angle: Angle) -> "CameraOrientation":
        ...

    @abstractmethod
    def zoom_in(self, ratio: float) -> "CameraOrientation":
        ...


class CameraMover(ABC):
    ...
