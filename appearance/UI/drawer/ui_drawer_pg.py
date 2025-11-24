from attrs import frozen
import pygame as pg

import appearance.protocols as proto
from appearance.graphics.sprites import Sprite
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2


@frozen
class UiDrawer(proto.UiDrawer):
    _screen: pg.Surface

    def draw_text(self, text_data: proto.TextData, rectangle: Rectangle) -> None:
        text, font, color = text_data.tuple
        rendered = font.render(text, True, color)
        position = rectangle.center
        position -= Vector2(rendered.get_width(), rendered.get_height()) / 2
        self._screen.blit(rendered, position)

    def draw_image(self, sprite: Sprite, position: Vector2) -> None:
        sprite.blit_on(self._screen, position)
