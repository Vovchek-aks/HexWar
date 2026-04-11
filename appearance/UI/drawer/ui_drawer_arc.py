from attrs import frozen
import arcade as arc

import appearance.protocols as proto
from appearance.graphics.sprites import Sprite
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2


@frozen
class UiDrawer(proto.UiDrawer):
    def draw_text(self, text_data: proto.TextData, rectangle: Rectangle) -> None:
        text, font, color = text_data.tuple
        position = rectangle.position
        arc.draw_text(text, *position, color, font.size)

    def draw_image(self, sprite: Sprite, position: Vector2) -> None:
        sprite.blit_at(position)
