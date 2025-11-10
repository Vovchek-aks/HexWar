from attrs import define, field

import appearance.protocols as proto
from appearance.graphics.sprites import Sprite
from appearance.input.clicks_catcher.layers.shape_layer import ShapeLayer
from appearance.layer import LayerBuilder
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2


@define
class ImageUi(proto.Layer):
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
    def drawable_layer(self) -> proto.DrawableLayer:
        return self._layer.drawable_layer

    @property
    def clicks_catching_layer(self) -> proto.ClicksCatchingLayer:
        return self._layer.clicks_catching_layer

    def draw(self, mouse_position: Vector2) -> None:
        self._layer.drawable_layer.draw(mouse_position)

    def can_catch(self, click: proto.Click) -> bool:
        return self._layer.clicks_catching_layer.can_catch(click)

    def catch(self, click: proto.Click) -> None:
        self._layer.clicks_catching_layer.catch(click)

    def _draw(self, _: Vector2) -> None:
        self._drawer.draw_image(self._sprite, self._position)
