from attrs import define, field

from appearance.UI.text.text_data_pg import TextDataBuilder
from appearance.layer import LayerBuilder
from color import Color
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2
import appearance.protocols as proto


@define
class TextUi(proto.ElementUi):
    @classmethod
    def make(cls, drawer: proto.UiDrawer, rectangle: Rectangle, data: proto.TextData) -> "TextUi":
        data = (TextDataBuilder.like(data)
                .change_font_size_fitting(rectangle)
                .build())

        self = cls(drawer, data, rectangle)

        layer = (LayerBuilder()
                 .not_catching()
                 .set_draw_function(self._draw)
                 .build())

        self._layer = layer
        return self

    _drawer: proto.UiDrawer
    _data: proto.TextData
    _rectangle: Rectangle
    _layer: proto.Layer = field(init=False)

    @property
    def layer(self) -> proto.Layer:
        return self._layer

    @property
    def rectangle(self) -> Rectangle:
        return self._rectangle

    def set_rectangle(self, rectangle: Rectangle) -> None:
        self._rectangle = rectangle
        self._data = (TextDataBuilder.like(self._data)
                      .change_font_size_fitting(self.rectangle)
                      .build())

    def set_text(self, text: str) -> None:
        self._data = self._data.with_text(text)
        self.set_rectangle(self.rectangle)

    def set_color(self, color: Color) -> None:
        self._data = self._data.with_color(color)

    def _draw(self, _: Vector2) -> None:
        self._drawer.draw_text(self._data, self.rectangle)
