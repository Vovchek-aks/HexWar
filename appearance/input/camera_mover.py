from attrs import frozen
import pygame as pg

from angle import Angle
from events import Events
from appearance.graphics import protocols as proto
from statuses import MISSING

ROTATION_POSITIVE = pg.K_e
ROTATION_NEGATIVE = pg.K_q

MOVEMENT_UP = pg.K_w
MOVEMENT_LEFT = pg.K_a
MOVEMENT_DOWN = pg.K_s
MOVEMENT_RIGHT = pg.K_d

ROTATION_SPEED = Angle(60)
MOVEMENT_SPEED = 150
ZOOM_SPEED = 1.15


@frozen
class CameraMover:
    _orientation: proto.CameraOrientation

    def update(self, events: Events, keys: pg.key.ScancodeWrapper, dt: float) -> None:
        self._movement(keys, dt)
        self._rotation(keys, dt)
        self._zoom(events)

    def _movement(self, keys: pg.key.ScancodeWrapper, dt: float) -> None:
        x = keys[MOVEMENT_RIGHT] - keys[MOVEMENT_LEFT]
        y = keys[MOVEMENT_DOWN] - keys[MOVEMENT_UP]
        direction = pg.Vector2(x, y)

        if direction.length() > 1:
            direction = direction.normalize()

        zoom = self._orientation.zoom
        self._orientation.move(_get_movement_speed(zoom) * direction * dt)

    def _rotation(self, keys: pg.key.ScancodeWrapper, dt: float) -> None:
        direction = keys[ROTATION_POSITIVE] - keys[ROTATION_NEGATIVE]
        self._orientation.rotate(ROTATION_SPEED * (dt * direction))

    def _zoom(self, events: Events) -> None:
        if (event := events.get(pg.MOUSEWHEEL)) is MISSING:
            return

        delta = event.y
        self._orientation.zoom_in(ZOOM_SPEED ** delta)


def _get_movement_speed(zoom: float) -> float:
    return MOVEMENT_SPEED / zoom ** .5
