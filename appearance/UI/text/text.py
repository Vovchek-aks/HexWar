import arcade as arc
from attrs import define, field

from appearance.layer import LayerBuilder
from color import Color
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2
import appearance.protocols as proto


@define
class TextUi(proto.ElementUi):
    @classmethod
    def make(cls, drawer: proto.UiDrawer, rectangle: Rectangle, data: proto.TextData) -> "TextUi":
        text = arc.Text(data.text, *rectangle.position, color=data.color, font_size=data.font.font_size)

        self = cls(drawer, text, rectangle)
        self.set_rectangle(rectangle)

        layer = (LayerBuilder()
                 .not_catching()
                 .set_draw_function(self._draw)
                 .build())

        self._layer = layer
        return self

    _drawer: proto.UiDrawer
    _text: arc.Text
    _rectangle: Rectangle
    _layer: proto.Layer = field(init=False)

    @property
    def layer(self) -> proto.Layer:
        return self._layer

    @property
    def rectangle(self) -> Rectangle:
        return self._rectangle

    @property
    def text(self) -> str:
        return self._text.text

    def set_rectangle(self, rectangle: Rectangle) -> None:
        self._rectangle = rectangle
        self._text.position = rectangle.position.tuple
        self._change_font_size_fitting(rectangle)

    def set_text(self, text: str) -> None:
        self._text.text = text

    def set_color(self, color: Color) -> None:
        self._text.color = color

    def _draw(self, _: Vector2) -> None:
        self._text.draw()

    def _change_font_size_fitting(self, rectangle: Rectangle) -> None:
        if rectangle == Rectangle.zero():
            return

        rect_width, rect_height = rectangle.shape
        text_rect = Vector2(*self._text.content_size)

        scale_x = rect_width / text_rect.x
        scale_y = rect_height / text_rect.y
        scale = min(scale_x * .85, scale_y * 1.45)
        new_size = max(1, int(self._text.font_size * scale))
        self._text.font_size = new_size
