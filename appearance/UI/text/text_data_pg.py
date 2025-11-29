from attrs import define, frozen, field

from font import Font
from color import Color
import appearance.protocols as proto
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2
from statuses import Status, MISSING

DEBUG_COLOR = Color(255, 255, 255)


@frozen
class TextData(proto.TextData):
    @classmethod
    def debug(cls, text: str) -> "TextData":
        return (TextDataBuilder()
                .set_text(text)
                .debug_font()
                .debug_color()
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

    def debug_color(self) -> "TextDataBuilder":
        return self.set_color(DEBUG_COLOR)

    def change_font_size_fitting(self, rectangle: Rectangle) -> "TextDataBuilder":
        assert MISSING not in (self._text, self._font)

        # FUCK MY LIFE

        rect_width, rect_height = rectangle.shape
        # text_width, text_height = self._font.size(self._text)
        #
        # estimated_size1 = round(rect_height * 1.4)
        # # font = Font(self._font.file_path, estimated_size1)
        #
        # # if (width := font.size(self._text)[0]) < rect_width:
        # #     return self.set_font(font)
        #
        # estimated_size2 = round(rect_width * .25)
        # estimated_size = round((estimated_size1 + estimated_size2) / 2)
        # font = Font(self._font.file_path, estimated_size)
        # # if new_font.size(self._text)[0] < width:
        # #     return self.set_font(new_font)

        font = self._font
        text_surface = font.render(self._text, True, self._color)
        text_rect = text_surface.get_rect()

        if text_rect.width > rect_width or text_rect.height > rect_height:
            scale_x = rect_width / text_rect.width
            scale_y = rect_height / text_rect.height
            scale = min(scale_x, scale_y)
            new_size = max(1, int(font.get_height() * scale))
            font = Font(font.file_path, new_size)

        return self.set_font(font)
