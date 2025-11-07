from attrs import frozen
import pygame as pg

from appearance.graphics.layer_drawers.layers_drawer import LayersDrawer
from appearance.layer import Layer
from mathematics.vector import Vector2


@frozen
class FrameDrawer:
    @classmethod
    def make(cls, layers: list[Layer]) -> "FrameDrawer":
        return cls(LayersDrawer(layers[::-1]))

    _layers: LayersDrawer

    def draw_frame(self, mouse_position: Vector2) -> None:
        self._layers.draw(mouse_position)
        pg.display.flip()
