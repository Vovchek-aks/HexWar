from attrs import define, field

import appearance.protocols as proto
from appearance.graphics.sprites import Sprite
from appearance.input.clicks_catcher.layers.shape_layer import ShapeLayer
from appearance.layer import LayerBuilder
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2, Vector2Int


@define
class ImageUi(proto.UiElement):
    _drawer: proto.UiDrawer
    _sprite: Sprite
    _position: Vector2
    _rectangle: Rectangle = field(init=False)
    _layer: proto.Layer = field(init=False)

    def __attrs_post_init__(self) -> None:
        self._sprite = self._sprite.with_pivot(Vector2Int.zero())
        self._rectangle = Rectangle.with_center_at(self._position, self._sprite.shape.as_vector2)
        self._layer = (LayerBuilder()
                       .set_clicks_catching(ShapeLayer(self._rectangle))
                       .set_draw_function(self._draw)
                       .build())

    @property
    def layer(self) -> proto.Layer:
        return self._layer

    @property
    def rectangle(self) -> Rectangle:
        return self._rectangle

    def _draw(self, _: Vector2) -> None:
        self._drawer.draw_image(self._sprite, self.rectangle.left_up_corner)
