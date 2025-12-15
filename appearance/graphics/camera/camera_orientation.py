from attrs import define, frozen

from mathematics.angle import Angle
from mathematics.vector import Vector2
from appearance import protocols as proto


@define
class CameraOrientation(proto.CameraOrientation):
    @classmethod
    def starter(cls) -> "CameraOrientation":
        return cls(Vector2(14, -8), Angle(60), 25)

    _position: Vector2
    _rotation: Angle
    _zoom: float

    @property
    def position(self) -> Vector2:
        return self._position

    @property
    def rotation(self) -> Angle:
        return self._rotation

    @property
    def zoom(self) -> float:
        return self._zoom

    @property
    def tuple(self) -> tuple[Vector2, Angle, float]:
        return self._position, self._rotation, self._zoom

    def move(self, delta: Vector2) -> "CameraOrientation":
        self._position += self._rotation.inverse.apply(delta)
        return self

    def rotate(self, angle: Angle) -> "CameraOrientation":
        self._rotation += angle
        return self

    def zoom_in(self, ratio: float) -> "CameraOrientation":
        self._zoom *= ratio
        return self


@frozen
class ReadonlyCameraOrientation(proto.ReadonlyCameraOrientation):
    _orientation: proto.CameraOrientation

    @property
    def position(self) -> Vector2:
        return self._orientation.position

    @property
    def rotation(self) -> Angle:
        return self._orientation.rotation

    @property
    def zoom(self) -> float:
        return self._orientation.zoom

    @property
    def tuple(self) -> tuple[Vector2, Angle, float]:
        return self._orientation.tuple
