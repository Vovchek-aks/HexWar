from attrs import define
import pygame as pg

from angle import Angle
from appearance.graphics import protocols as proto


@define
class CameraOrientation(proto.CameraOrientation):
    @classmethod
    def starter(cls) -> "CameraOrientation":
        return cls(pg.Vector2(0, 0), Angle(0), 50)

    _position: pg.Vector2
    _rotation: Angle
    _zoom: float

    @property
    def position(self) -> pg.Vector2:
        return self._position

    @property
    def rotation(self) -> Angle:
        return self._rotation

    @property
    def zoom(self) -> float:
        return self._zoom

    @property
    def tuple(self) -> tuple[pg.Vector2, Angle, float]:
        return self._position, self._rotation, self._zoom

    def move(self, delta: pg.Vector2) -> "CameraOrientation":
        self._position += self._rotation.inverse.apply(delta)
        return self

    def rotate(self, angle: Angle) -> "CameraOrientation":
        self._rotation += angle
        return self

    def zoom_in(self, ratio: float) -> "CameraOrientation":
        self._zoom *= ratio
        return self
