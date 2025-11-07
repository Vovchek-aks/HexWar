from attrs import frozen, Factory

from appearance.game_engine.game_engine_pg.events import Events
from appearance.protocols import ClicksCatchingLayer as Layer
from mathematics.vector import Vector2
from statuses import MISSING, Status
from .click import read_click, Click


@frozen
class ClicksCatcher:
    _layers: list[Layer] = Factory(list)

    def update(self, events: Events, mouse_position: Vector2) -> None:
        if (click := read_click(events, mouse_position)) is MISSING:
            return

        self.update_from(click)

    def update_from(self, click: Click) -> None:
        layer = self.get_first_layer_that_cat_catch(click)
        layer.catch(click)

    def get_first_layer_that_cat_catch(self, click: Click) -> Layer | Status:
        for layer in self._layers:
            if layer.can_catch(click):
                return layer
        return MISSING
