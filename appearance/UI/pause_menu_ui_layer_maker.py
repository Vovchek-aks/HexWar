from typing import Callable

from attrs import frozen, Factory

import appearance.protocols as proto
from appearance.UI.button import ButtonUi, get_image_rectangle
from appearance.UI.layouts import VerticalLayoutUi
from appearance.UI.main_menu_ui_layer_maker import MainMenuUiLayerMaker
from appearance.UI.text import TextData, TextUi
from appearance.UI.text.test_size_synchroniser import TextSizeSynchroniser
from appearance.graphics.colors import RECTANGLE_BUTTON
from appearance.graphics.sprites import SpritesLoader
from appearance.language import Language
from appearance.layer import Layer
from mathematics.rectangle import Rectangle, RectangleBuilder
from mathematics.vector import Vector2Int, Vector2
from my_types import combine
from observer import Event, OnEventSubscriber


@frozen
class PauseMenuUiLayerMaker:
    _drawer: proto.UiDrawer
    _screen_shape: Vector2Int
    _mouse_movement_observer: proto.MouseMovementObserver

    _language: Language = Factory(Language.from_meta)
    _sprites_loader: SpritesLoader = Factory(SpritesLoader.from_meta)

    def make(self,
             on_continue_was_pressed: Callable[[], None],
             on_to_main_menu_was_pressed: Callable[[], None],
             pause_menu_open_requested: OnEventSubscriber[None],
             reload: Callable[[], None]) -> Layer:
        to_label_was_pressed = Event[None]()
        settings_was_pressed = Event[None]()

        pause_menu_open_requested.subscribe(to_label_was_pressed.invoke)

        tabs = list[Layer]()

        def turn_tabs_off() -> None:
            for tab in tabs:
                tab.set_activity(False)

        tabs.append(self._make_label(turn_tabs_off, to_label_was_pressed.subscriber, on_continue_was_pressed,
                                     on_to_main_menu_was_pressed, settings_was_pressed.invoke))
        tabs.append(MainMenuUiLayerMaker(self._drawer, self._screen_shape, self._mouse_movement_observer)
                    .make_settings_tab(turn_tabs_off, settings_was_pressed.subscriber, to_label_was_pressed, reload,
                                       include_screed_settings=False))

        return Layer.as_multiple(tabs)

    def _make_label(self,
                    turn_tabs_off: Callable[[], None],
                    on_to_label_was_pressed: OnEventSubscriber[None],
                    on_continue_was_pressed: Callable[[], None],
                    on_to_main_menu_was_pressed: Callable[[], None],
                    on_settings_was_pressed: Callable[[], None]) -> Layer:
        layers = [
            self._make_title(),
            self._make_buttons(on_continue_was_pressed, on_to_main_menu_was_pressed,
                               combine(turn_tabs_off, on_settings_was_pressed)),
        ]

        layer = Layer.as_multiple(layers)
        on_to_label_was_pressed.subscribe(combine(turn_tabs_off, lambda: layer.set_activity(True)))
        return layer

    def _make_buttons(self,
                      on_continue_was_pressed: Callable[[], None],
                      on_to_main_menu_was_pressed: Callable[[], None],
                      on_settings_was_pressed: Callable[[], None]) -> Layer:
        buttons = [
            self._make_null_button(self._language.get_continue_message(), on_continue_was_pressed),
            self._make_null_button(self._language.get_settings_message(), on_settings_was_pressed),
            self._make_null_button(self._language.get_to_main_menu_message(), on_to_main_menu_was_pressed),
        ]

        layout = VerticalLayoutUi(self._get_buttons_rectangle(), margin_ratio=0.2)
        layout.extend(buttons)

        synchroniser = TextSizeSynchroniser()
        for button in buttons:
            synchroniser.append(button.text)
        synchroniser.synchronise()

        return layout.layer

    def _get_buttons_rectangle(self) -> Rectangle:
        center_x = self._screen_shape.x / 2
        width = self._screen_shape.x / 5
        x = center_x - width / 2
        height = self._screen_shape.y / 5 * 1.5
        bottom_margin = self._screen_shape.y / 5 / 1.5

        return (RectangleBuilder(self._screen_shape)
                .from_left_bottom()
                .set_shape(Vector2(width, height))
                .move(Vector2(x, bottom_margin))
                .adjust_for_shape()
                .build())

    def _make_null_button(self, text: str, on_button_pressed: Callable[[], None]) -> ButtonUi:
        button_background = self._sprites_loader.load_button_5().colored_in(RECTANGLE_BUTTON)
        button_text = TextData.for_button(text)
        button = ButtonUi.make(self._drawer,
                               get_image_rectangle(Rectangle(Vector2.zero(), button_background.shape.as_vector2)),
                               button_background,
                               self._mouse_movement_observer,
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
