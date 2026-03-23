from attrs import define, frozen, field

from mathematics.angle import Angle
from mathematics.vector import Vector2
from appearance import protocols as proto
from observer import Event, OnEventSubscriber


@define
class CameraOrientation(proto.CameraOrientation):
    @classmethod
    def starter(cls) -> "CameraOrientation":
        return cls(Vector2(57, -34), Angle(-60), 6.5)
        # return cls(Vector2(715, 400), Angle(60), 4.6)
        # return cls(Vector2(715, 400), Angle(60), 4.6)

    _has_changed: Event[None] = field(init=False, factory=Event)

    _position: Vector2
    _rotation: Angle
    _zoom: float
    _had_changed: bool = field(init=False, default=False)

    @property
    def has_changed(self) -> OnEventSubscriber[None]:
        return self._has_changed.subscriber

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

    def set_starter(self) -> None:
        starter = CameraOrientation.starter()
        self._position = starter.position
        self._rotation = starter.rotation
        self._zoom = starter.zoom

    def update(self) -> None:
        if not self._had_changed:
            return

        self._has_changed.invoke()
        self._had_changed = False

    def move(self, delta: Vector2) -> "CameraOrientation":
        if delta == Vector2.zero():
            return self

        self._position += self._rotation.inverse.apply(delta)
        self._had_changed = True
        return self

    def rotate(self, angle: Angle) -> "CameraOrientation":
        if angle.degrees == 0:
            return self

        self._rotation += angle
        self._had_changed = True
        return self

    def zoom_in(self, ratio: float) -> "CameraOrientation":
        if ratio == 0:
            return self

        self._zoom *= ratio
        self._had_changed = True
        return self


@frozen
class ReadonlyCameraOrientation(proto.ReadonlyCameraOrientation):
    _orientation: proto.CameraOrientation

    @property
    def has_changed(self) -> OnEventSubscriber[None]:
        return self._orientation.has_changed

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

    def mutable_copy(self) -> proto.CameraOrientation:
        return CameraOrientation(*self.tuple)
