from typing import Callable

from attrs import frozen, define

import appearance.protocols as proto
from appearance.graphics.layer_drawers.function_layer_drawer import FunctionLayerDrawer
from appearance.graphics.layer_drawers.no_draw_layer import NoDrawLayer
from appearance.input.clicks_catcher.layers.no_catching_layer import NoCatchingLayer
from mathematics.vector import Vector2
from statuses import Status, MISSING


@frozen
class Layer(proto.Layer):
    _drawable_layer: proto.DrawableLayer
    _clicks_catching_layer: proto.ClicksCatchingLayer

    @property
    def drawable_layer(self) -> proto.DrawableLayer:
        return self._drawable_layer

    @property
    def clicks_catching_layer(self) -> proto.ClicksCatchingLayer:
        return self._clicks_catching_layer

    def draw(self, mouse_position: Vector2) -> None:
        self._drawable_layer.draw(mouse_position)

    def can_catch(self, click: proto.Click) -> bool:
        return self._clicks_catching_layer.can_catch(click)

    def catch(self, click: proto.Click) -> None:
        self._clicks_catching_layer.catch(click)


@define
class LayerBuilder:
    _drawable_layer: proto.DrawableLayer | Status = MISSING
    _clicks_catching_layer: proto.ClicksCatchingLayer | Status = MISSING

    def is_valid(self) -> bool:
        return MISSING not in (self._drawable_layer, self._clicks_catching_layer)

    def build(self) -> Layer:
        assert self.is_valid()
        return Layer(self._drawable_layer, self._clicks_catching_layer)

    def set_drawable(self, drawable_layer: proto.DrawableLayer) -> "LayerBuilder":
        self._drawable_layer = drawable_layer
        return self

    def set_clicks_catching(self, clicks_catching: proto.ClicksCatchingLayer) -> "LayerBuilder":
        self._clicks_catching_layer = clicks_catching
        return self

    def invisible(self) -> "LayerBuilder":
        return self.set_drawable(NoDrawLayer())

    def not_catching(self) -> "LayerBuilder":
        return self.set_clicks_catching(NoCatchingLayer())

    def set_draw_function(self, draw: Callable[[Vector2], None]) -> "LayerBuilder":
        return self.set_drawable(FunctionLayerDrawer(draw))
