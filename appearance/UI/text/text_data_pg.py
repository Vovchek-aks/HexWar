from attrs import frozen
import pygame as pg

from font import Font
from color import Color
import appearance.protocols as proto


@frozen
class TextData(proto.TextData):
    @classmethod
    def with_debug_font(cls, text: str, size: int, color: Color) -> "TextData":
        font = pg.font.Font(None, size)
        return cls(text, font, color)

    text: str
    font: Font
    color: Color

    @property
    def tuple(self) -> tuple[str, Font, Color]:
        return self.text, self.font, self.color

    def with_text(self, text: str) -> "TextData":
        return TextData(text, self.font, self.color)

    def with_color(self, color: Color) -> "TextData":
        return TextData(self.text, self.font, color)
