from typing import Callable

from attrs import define, field

import appearance.protocols as proto
from appearance.graphics.layer_drawers.function_layer_drawer import FunctionLayerDrawer
from appearance.graphics.layer_drawers.layers_drawer import LayersDrawer
from appearance.graphics.layer_drawers.no_draw_layer import NoDrawLayer
from appearance.input.clicks_catcher.layers.layers_container_layer import LayersContainerLayer
from appearance.input.clicks_catcher.layers.no_catching_layer import NoCatchingLayer
from appearance.protocols import Click
from mathematics.vector import Vector2
from observer import OnEventSubscriber, Event
from statuses import Status, MISSING


@define
class Layer(proto.Layer, proto.LayerHolder):
    @classmethod
    def empty(cls) -> "Layer":
        return cls.as_multiple([])

    @classmethod
    def as_multiple(cls, layers: list[proto.LayerHolder]) -> "Layer":
        return cls(LayersDrawer(layers[::-1]),
                   LayersContainerLayer.make(layers))

    _drawable_layer: proto.DrawableLayer
    _clicks_catching_layer: proto.ClicksCatchingLayer
    _is_active: bool = True

    _activity_was_changed: Event[bool, None] = field(init=False, factory=Event)

    @property
    def layer(self) -> proto.Layer:
        return self

    @property
    def was_clicked(self) -> OnEventSubscriber[Click, None]:
        return self._clicks_catching_layer.was_clicked

    @property
    def drawable_layer(self) -> proto.DrawableLayer:
        return self._drawable_layer

    @property
    def clicks_catching_layer(self) -> proto.ClicksCatchingLayer:
        return self._clicks_catching_layer

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def activity_was_changed(self) -> OnEventSubscriber[bool, None]:
        return self._activity_was_changed.subscriber

    def set_activity(self, activity: bool) -> None:
        previous = self._is_active
        self._is_active = activity
        if activity != previous:
            self._activity_was_changed.invoke(activity)

    def draw(self, mouse_position: Vector2) -> None:
        self._drawable_layer.draw(mouse_position)

    def can_catch(self, click: proto.Click) -> bool:
        return self._clicks_catching_layer.can_catch(click)

    def catch(self, click: proto.Click) -> None:
        self._clicks_catching_layer.catch(click)


@define
class LayerBuilder:
    @classmethod
    def like(cls, layer: Layer) -> "LayerBuilder":
        return (cls()
                .set_clicks_catcher(layer.clicks_catching_layer)
                .set_drawable(layer.drawable_layer))

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

    def set_clicks_catcher(self, clicks_catching: proto.ClicksCatchingLayer) -> "LayerBuilder":
        self._clicks_catching_layer = clicks_catching
        return self

    def invisible(self) -> "LayerBuilder":
        return self.set_drawable(NoDrawLayer())

    def not_catching(self) -> "LayerBuilder":
        return self.set_clicks_catcher(NoCatchingLayer())

    def set_draw_function(self, draw: Callable[[Vector2], None]) -> "LayerBuilder":
        return self.set_drawable(FunctionLayerDrawer(draw))
