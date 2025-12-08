from attrs import define, frozen, field

from font import Font
from color import Color
import appearance.protocols as proto
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2
from statuses import Status, MISSING

WHITE_COLOR = Color(255, 255, 255)
BLACK_COLOR = Color(53, 53, 49)


@frozen
class TextData(proto.TextData):
    @classmethod
    def debug(cls, text: str) -> "TextData":
        return (TextDataBuilder()
                .set_text(text)
                .debug_font()
                .white_colored()
                .build())

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


@define
class TextDataBuilder:
    @classmethod
    def like(cls, data: TextData) -> "TextDataBuilder":
        return (cls()
                .set_text(data.text)
                .set_font(data.font)
                .set_color(data.color))

    _text: str | Status = field(init=False, default=MISSING)
    _font: Font | Status = field(init=False, default=MISSING)
    _color: Color | Status = field(init=False, default=MISSING)

    def is_valid(self) -> bool:
        return MISSING not in (self._text, self._font, self._color)

    def build(self) -> TextData:
        assert self.is_valid()
        return TextData(self._text, self._font, self._color)

    def set_text(self, text: str) -> "TextDataBuilder":
        self._text = text
        return self

    def set_font(self, font: Font) -> "TextDataBuilder":
        self._font = font
        return self

    def set_color(self, color: Color) -> "TextDataBuilder":
        self._color = color
        return self

    def debug_font(self, size: int = 30) -> "TextDataBuilder":
        return self.set_font(Font(None, size))

    def white_colored(self) -> "TextDataBuilder":
        return self.set_color(WHITE_COLOR)

    def black_colored(self) -> "TextDataBuilder":
        return self.set_color(BLACK_COLOR)

    def change_font_size_fitting(self, rectangle: Rectangle) -> "TextDataBuilder":
        assert MISSING not in (self._text, self._font)

        if not self._text:
            return self

        font = self._font
        for _ in range(2):
            rect_width, rect_height = rectangle.shape
            text_surface = font.render(self._text, True, self._color)
            text_rect = text_surface.get_rect()

            scale_x = rect_width / text_rect.width
            scale_y = rect_height / text_rect.height
            scale = min(scale_x, scale_y) * 1.45
            new_size = max(1, int(font.get_height() * scale))
            font = Font(font.file_path, new_size)

        return self.set_font(font)
