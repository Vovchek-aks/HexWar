from attrs import define, field
import arcade.gui as arcgui

import appearance.protocols as proto
from appearance.game_engine.game_engine_arc.window import Window
from appearance.input.clicks_catcher.layers.shape_layer import ShapeLayer
from appearance.layer import LayerBuilder
from appearance.protocols import TextData
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2
from observer import OnEventSubscriber


@define(hash=True)
class LineEditUi(proto.ElementUi):
    @classmethod
    def make(cls,
             window: Window,
             scene_was_switched: OnEventSubscriber[None],
             rectangle: Rectangle,
             text_data: TextData) -> "LineEditUi":
        manager = arcgui.UIManager(window)
        manager.enable()
        scene_was_switched.subscribe(manager.disable)

        input_field = arcgui.UIInputText(
            text=text_data.text,
            text_color=text_data.color,
            font_size=text_data.font.size,
            font_name=text_data.font.name,
        )
        manager.add(input_field)

        self = cls(input_field, manager, rectangle)
        self.set_rectangle(rectangle)

        self._layer = (LayerBuilder()
                       .set_clicks_catcher(ShapeLayer(self._rectangle))
                       .set_draw_function(self._draw)
                       .build())
        self._layer.activity_was_changed.subscribe(lambda is_active: (manager.enable  # todo: fix!!!!
                                                                      if is_active else
                                                                      manager.disable)())
        return self

    _input_field: arcgui.UIInputText = field(hash=False)
    _manager: arcgui.UIManager = field(hash=False)
    _rectangle: Rectangle = field(hash=False)
    _layer: proto.Layer = field(init=False, hash=False)
    _id = field(init=False, hash=True)

    def __attrs_post_init__(self) -> None:
        self._id = id(self)

    @property
    def layer(self) -> proto.Layer:
        return self._layer

    @property
    def rectangle(self) -> Rectangle:
        return self._rectangle

    @property
    def text(self) -> str:
        return self._input_field.text

    def set_rectangle(self, rectangle: Rectangle) -> None:
        self._rectangle = rectangle
        self._input_field.center_x = rectangle.position.x
        self._input_field.center_y = rectangle.position.y
        self._input_field.width = rectangle.shape.x
        self._input_field.height = rectangle.shape.y

    def _draw(self, _: Vector2) -> None:
        self._manager.draw()
