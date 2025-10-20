from attrs import frozen, Factory

from appearance.game_engine.game_engine_pg.events import Events
from appearance.protocols import ClicksCatchingLayer as Layer
from mathematics.vector import Vector2
from statuses import MISSING
from .click import read_click


@frozen
class ClicksCatcher:
    _layers: list[Layer] = Factory(list)

    def update(self, events: Events, mouse_position: Vector2) -> None:
        if (click := read_click(events, mouse_position)) is MISSING:
            return

        for layer in self._layers:
            if not layer.can_catch(click):
                continue

            layer.catch(click)
            break
