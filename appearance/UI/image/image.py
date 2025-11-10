from attrs import define, field

import appearance.protocols as proto
from appearance.graphics.sprites import Sprite
from appearance.input.clicks_catcher.layers.shape_layer import ShapeLayer
from appearance.layer import LayerBuilder
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2


@define
class ImageUi(proto.LayerHolder):
    _drawer: proto.UiDrawer
    _sprite: Sprite
    _position: Vector2
    _layer: proto.Layer = field(init=False)

    def __attrs_post_init__(self) -> None:
        shape = Rectangle(self._position, self._sprite.shape.as_vector2)
        self._layer = (LayerBuilder()
                       .set_clicks_catching(ShapeLayer(shape))
                       .set_draw_function(self._draw)
                       .build())

    @property
    def layer(self) -> proto.Layer:
        return self._layer

    def _draw(self, _: Vector2) -> None:
        self._drawer.draw_image(self._sprite, self._position)
