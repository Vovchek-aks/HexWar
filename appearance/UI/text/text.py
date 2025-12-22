import arcade as arc

from attrs import define, field

from appearance.UI.text.text_data_arc import TextDataBuilder
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

        layer = (LayerBuilder()
                 .not_catching()
                 .set_draw_function(self._draw)
                 .build())

        self._layer = layer
        return self

    _drawer: proto.UiDrawer
    _text: arc.Text
    # _data: proto.TextData
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
        self._text.position = rectangle.position
        self._change_font_size_fitting(rectangle)
        # self._data = (TextDataBuilder.like(self._data)
        #               .change_font_size_fitting(self.rectangle)
        #               .build())

    def set_text(self, text: str) -> None:
        self._text.text = text
        # self._data = self._data.with_text(text)
        # self.set_rectangle(self.rectangle)

    def set_color(self, color: Color) -> None:
        self._text.color = color
        # self._data = self._data.with_color(color)

    def _draw(self, _: Vector2) -> None:
        # self._drawer.draw_text(self._data, self.rectangle)
        self._text.draw()

    def _change_font_size_fitting(self, rectangle: Rectangle) -> None:
        if rectangle == Rectangle.zero():
            return

        for _ in range(2):
            rect_width, rect_height = rectangle.shape
            text_rect = Vector2(*self._text.content_size)

            scale_x = rect_width / text_rect.x
            scale_y = rect_height / text_rect.y
            scale = min(scale_x, scale_y) * 1.45
            new_size = max(1, int(self._text.font_size * scale))
            self._text.font_size = new_size
