from attrs import frozen
import pygame as pg

from appearance.game_engine.game_engine_pg.events import Events, UpdatableEvents
from appearance.game_engine.game_engine_pg.timer import Timer
from mathematics.vector import Vector2


@frozen
class UserInput:
    @classmethod
    def read(cls, events: UpdatableEvents, timer: Timer) -> "UserInput":
        return cls(events.get(),
                   pg.key.get_pressed(),
                   timer.dt,
                   Vector2(*pg.mouse.get_pos()))

    events: Events
    keys: pg.key.ScancodeWrapper
    dt: float

    _mouse_position: Vector2

    @property
    def mouse_position(self) -> Vector2:
        return self._mouse_position
