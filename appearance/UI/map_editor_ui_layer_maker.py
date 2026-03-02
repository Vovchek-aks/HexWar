from typing import Callable

from attrs import frozen, Factory

import appearance.protocols as proto
from appearance.UI.button import ButtonUi, get_image_rectangle, SwitchButtonUI
from appearance.UI.text import TextData
from appearance.graphics.sprites import SpritesLoader
from appearance.language import Language
from appearance.layer import Layer
from map_editor import MapEditor
from mathematics.rectangle import Rectangle, RectangleBuilder
from mathematics.vector import Vector2Int, Vector2


@frozen
class MapEditorUiLayerMaker:
    _drawer: proto.UiDrawer
    _screen_shape: Vector2Int
    _map_editor: MapEditor

    _language: Language = Factory(Language.from_meta)
    _sprites_loader: SpritesLoader = Factory(SpritesLoader.from_meta)

    def make(self, on_exit_was_pressed: Callable[[], None]) -> Layer:

        layers = [
            self._make_back_button(on_exit_was_pressed),
            self._make_switch_transform_button()
        ]

        return Layer.as_multiple(layers)

    def _make_back_button(self, on_exit_was_pressed: Callable[[], None]) -> ButtonUi:
        button = self._make_null_button(self._language.get_back_message(), on_exit_was_pressed)
        button.set_rectangle(self._get_back_button_rectangle())
        return button

    def _get_back_button_rectangle(self) -> Rectangle:
        width = self._screen_shape.x / 15
        height = self._screen_shape.y / 20

        return (RectangleBuilder(self._screen_shape)
                .from_left_bottom()
                .set_shape(Vector2(width, height))
                .move(Vector2(20, 20))
                .adjust_for_shape()
                .build())

    def _make_switch_transform_button(self) -> SwitchButtonUI:
        transforms = self._map_editor.transforms
        buttons = list[ButtonUi]()
        for name, transform in zip(transforms, transforms[1:] + [transforms[0]]):
            buttons.append(self._make_transform_button(name, transform))

        switch_button = SwitchButtonUI.make(self._get_switch_transform_button_rectangle(), *buttons)

        for button in buttons:
            button.was_clicked.subscribe(switch_button.next)

        return switch_button

    def _make_transform_button(self, name: str, transform: str) -> ButtonUi:
        return self._make_null_button(name, lambda: self._map_editor.set(transform))

    def _get_switch_transform_button_rectangle(self) -> Rectangle:
        width = self._screen_shape.x / 10
        height = self._screen_shape.y / 15

        return (RectangleBuilder(self._screen_shape)
                .from_right_bottom()
                .set_shape(Vector2(width, height))
                .move(Vector2(30, 30))
                .adjust_for_shape()
                .build())

    def _make_null_button(self, text: str, on_button_pressed: Callable[[], None]) -> ButtonUi:
        button_background = self._sprites_loader.load_button_3_to_2()
        button_text = TextData.debug(text)
        button = ButtonUi.make(self._drawer,
                               get_image_rectangle(Rectangle(Vector2.zero(), button_background.shape.as_vector2)),
                               button_background,
                               button_text)
        button.was_clicked.subscribe(on_button_pressed)
        return button
