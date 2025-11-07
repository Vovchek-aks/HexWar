from attrs import frozen
import pygame as pg

from font import Font
from mathematics.vector import Vector2
from color import Color
import appearance.protocols as proto


@frozen
class TextData(proto.TextData):
    @classmethod
    def with_debug_font(cls, text: str, size: int, color: Color, position: Vector2) -> "TextData":
        font = pg.font.Font(None, size)
        return cls(text, font, color, position)

    text: str
    font: Font
    color: Color
    _position: Vector2

    @property
    def position(self) -> Vector2:
        return self._position

    @property
    def tuple(self) -> tuple[str, Font, Color, Vector2]:
        return self.text, self.font, self.color, self.position
