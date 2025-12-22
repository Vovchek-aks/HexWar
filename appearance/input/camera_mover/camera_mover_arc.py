from attrs import frozen
import arcade as arc

from mathematics.angle import Angle
from mathematics.vector import Vector2
from appearance import protocols as proto

ROTATION_POSITIVE = arc.key.E
ROTATION_NEGATIVE = arc.key.Q

MOVEMENT_UP = arc.key.W
MOVEMENT_LEFT = arc.key.A
MOVEMENT_DOWN = arc.key.S
MOVEMENT_RIGHT = arc.key.D

ROTATION_SPEED = Angle(60)
MOVEMENT_SPEED = 150
ZOOM_SPEED = 1.15


@frozen
class CameraMover:
    _orientation: proto.CameraOrientation

    def update(self, mouse_wheel_delta: float, keys: set[int], dt: float) -> None:
        self._movement(keys, dt)
        self._rotation(keys, dt)
        self._zoom(mouse_wheel_delta)

    def _movement(self, keys: set[int], dt: float) -> None:
        x = _has_key(keys, MOVEMENT_RIGHT) - _has_key(keys, MOVEMENT_LEFT)
        y = _has_key(keys, MOVEMENT_UP) - _has_key(keys, MOVEMENT_DOWN)
        direction = Vector2(x, y)

        if direction.length() > 1:
            direction = direction.normalize()

        zoom = self._orientation.zoom
        self._orientation.move(_get_movement_speed(zoom) * direction * dt)

    def _rotation(self, keys: set[int], dt: float) -> None:
        direction = _has_key(keys, ROTATION_POSITIVE) - _has_key(keys, ROTATION_NEGATIVE)
        self._orientation.rotate(ROTATION_SPEED * (dt * direction))

    def _zoom(self, delta: float) -> None:
        if delta == 0:
            return

        self._orientation.zoom_in(ZOOM_SPEED ** delta)


def _has_key(keys: set[int], key: int) -> bool:
    return key in keys


def _get_movement_speed(zoom: float) -> float:
    return MOVEMENT_SPEED / zoom ** .5
