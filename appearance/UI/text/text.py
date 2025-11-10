from attrs import define, field

from appearance.layer import LayerBuilder
from color import Color
from mathematics.vector import Vector2
import appearance.protocols as proto


@define
class TextUi(proto.LayerHolder):
    _drawer: proto.UiDrawer
    _data: proto.TextData
    _position: Vector2
    _layer: proto.Layer = field(init=False)

    def __attrs_post_init__(self) -> None:
        self._layer = (LayerBuilder()
                       .not_catching()
                       .set_draw_function(self._draw)
                       .build())

    @property
    def layer(self) -> proto.Layer:
        return self._layer

    def set_text(self, text: str) -> None:
        self._data = self._data.with_text(text)

    def set_color(self, color: Color) -> None:
        self._data = self._data.with_color(color)

    def _draw(self, _: Vector2) -> None:
        self._drawer.draw_text(self._data, self._position)
