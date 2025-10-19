from attrs import frozen
import pygame as pg

from appearance.game_engine.game_engine_pg.events import Events
from appearance.input.clicks_catcher.layers.debug import WholeScreenDebugLayer, RightSideDebugLayer
from appearance.protocols import ClicksCatchingLayer as Layer
from mathematics.vector import Vector2
from statuses import MISSING


@frozen
class ClicksCatcher:
    @classmethod
    def debug(cls) -> "ClicksCatcher":
        return cls([RightSideDebugLayer(500), WholeScreenDebugLayer()])

    _layers: list[Layer]

    def update(self, events: Events, mouse_position: Vector2) -> None:
        if events.get(pg.MOUSEBUTTONDOWN) is MISSING:
            return

        for layer in self._layers:
            if not layer.can_catch(mouse_position):
                continue

            layer.catch(mouse_position)
            break
