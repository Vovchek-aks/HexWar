from attrs import frozen
import pygame as pg

from appearance.graphics.draw import Draw
from appearance.layer import Layer
from mathematics.vector import Vector2


@frozen
class FrameDrawer:
    @classmethod
    def make(cls, draw: Draw, layers: list[Layer]) -> "FrameDrawer":
        return cls(draw,
                   layers[::-1])

    _draw: Draw
    _layers: list[Layer]

    def draw_frame(self, mouse_position: Vector2) -> None:
        for layer in self._layers:
            layer.draw(mouse_position)

        pg.display.flip()
