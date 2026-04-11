from typing import Callable

from attrs import frozen, Factory

import appearance.protocols as proto
from appearance.UI.button import ButtonUi, get_image_rectangle
from appearance.UI.layouts import VerticalLayoutUi
from appearance.UI.text import TextData, TextUi
from appearance.graphics.sprites import SpritesLoader
from appearance.language import Language
from appearance.layer import Layer
from mathematics.rectangle import Rectangle, RectangleBuilder
from mathematics.vector import Vector2Int, Vector2


@frozen
class PauseMenuUiLayerMaker:
    _drawer: proto.UiDrawer
    _screen_shape: Vector2Int

    _language: Language = Factory(Language.from_meta)
    _sprites_loader: SpritesLoader = Factory(SpritesLoader.from_meta)

    def make(self,
             on_continue_was_pressed: Callable[[], None],
             on_to_main_menu_was_pressed: Callable[[], None]) -> Layer:
        layers = [
            self._make_title(),
            self._make_buttons(on_continue_was_pressed, on_to_main_menu_was_pressed),
        ]

        return Layer.as_multiple(layers)

    def _make_buttons(self,
                      on_continue_was_pressed: Callable[[], None],
                      on_to_main_menu_was_pressed: Callable[[], None]) -> Layer:
        buttons = [
            self._make_null_button(self._language.get_continue_message(), on_continue_was_pressed),
            self._make_null_button(self._language.get_to_main_menu_message(), on_to_main_menu_was_pressed),
        ]
        layout = VerticalLayoutUi(self._get_buttons_rectangle(), margin_ratio=0.2)
        layout.extend(buttons)
        return layout.layer

    def _get_buttons_rectangle(self) -> Rectangle:
        center_x = self._screen_shape.x / 2
        width = self._screen_shape.x / 6
        x = center_x - width / 2
        height = self._screen_shape.y / 5
        bottom_margin = self._screen_shape.y / 5

        return (RectangleBuilder(self._screen_shape)
                .from_left_bottom()
                .set_shape(Vector2(width, height))
                .move(Vector2(x, bottom_margin))
                .adjust_for_shape()
                .build())

    def _make_null_button(self, text: str, on_button_pressed: Callable[[], None]) -> ButtonUi:
        button_background = self._sprites_loader.load_button_3_to_2()
        button_text = TextData.for_button(text)
        button = ButtonUi.make(self._drawer,
                               get_image_rectangle(Rectangle(Vector2.zero(), button_background.shape.as_vector2)),
                               button_background,
                               button_text)
        button.was_clicked.subscribe(on_button_pressed)
        return button

    def _make_title(self) -> Layer:
        title = TextUi.make(self._drawer,
                            self._get_title_rectangle(),
                            TextData.debug(self._language.get_pause_message()),
                            is_center=True)
        return title.layer

    def _get_title_rectangle(self) -> Rectangle:
        center_x = self._screen_shape.x / 2
        width = self._screen_shape.x / 4
        x = center_x - width / 2
        height = self._screen_shape.y / 6
        top_margin = self._screen_shape.y / 5

        return (RectangleBuilder(self._screen_shape)
                .from_left_up()
                .set_shape(Vector2(width, height))
                .move(Vector2(x, top_margin))
                .adjust_for_shape()
                .build())
