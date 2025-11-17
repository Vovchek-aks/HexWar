from attrs import define, field

from appearance.layer import LayerBuilder
from color import Color
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2
import appearance.protocols as proto


@define
class TextUi(proto.UiElement):
    @classmethod
    def make(cls, drawer: proto.UiDrawer, position: Vector2, text_data: proto.TextData) -> "TextUi":
        self = cls(drawer,
                   text_data,
                   Rectangle.with_center_at(position, text_data.shape))

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

    def set_text(self, text: str) -> None:
        center = self.rectangle.center
        self._data = self._data.with_text(text)
        self._rectangle = Rectangle.with_center_at(center, self._data.shape)

    def set_color(self, color: Color) -> None:
        self._data = self._data.with_color(color)

    def _draw(self, _: Vector2) -> None:
        self._drawer.draw_text(self._data, self.rectangle.left_up_corner)
