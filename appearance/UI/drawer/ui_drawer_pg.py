from attrs import frozen
import pygame as pg

import appearance.protocols as proto
from appearance.graphics.sprites import Sprite
from mathematics.vector import Vector2


@frozen
class UiDrawer(proto.UiDrawer):
    _screen: pg.Surface

    def draw_text(self, text_data: proto.TextData) -> None:
        text, font, color, position = text_data.tuple
        rendered = font.render(text, True, color)
        self._screen.blit(rendered, position)

    def draw_image(self, sprite: Sprite, position: Vector2) -> None:
        sprite.blit_on(self._screen, position)
