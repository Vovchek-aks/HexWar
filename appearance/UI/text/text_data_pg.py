from attrs import frozen
import pygame as pg

from font import Font
from color import Color
import appearance.protocols as proto
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2


@frozen
class TextData(proto.TextData):
    @classmethod
    def with_debug_font(cls, text: str, size: int, color: Color) -> "TextData":
        font = pg.font.Font(None, size)
        return cls(text, font, color)

    @classmethod
    def debug(cls, text: str) -> "TextData":
        return cls.with_debug_font(text, 30, Color(255, 255, 255))

    text: str
    font: Font
    color: Color

    @property
    def tuple(self) -> tuple[str, Font, Color]:
        return self.text, self.font, self.color

    @property
    def shape(self) -> Vector2:
        image = self.font.render(self.text, True, self.color)
        return Vector2(image.get_width(), image.get_height())

    def with_text(self, text: str) -> "TextData":
        return TextData(text, self.font, self.color)

    def with_color(self, color: Color) -> "TextData":
        return TextData(self.text, self.font, color)
