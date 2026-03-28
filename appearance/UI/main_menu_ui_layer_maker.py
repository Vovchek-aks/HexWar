from typing import Callable

from attrs import frozen, Factory

import appearance.protocols as proto
from appearance.UI.box import BoxUi
from appearance.UI.button import ButtonUi, get_image_rectangle
from appearance.UI.layouts import VerticalLayoutUi, HorizontalLayoutUi
from appearance.UI.text import TextData, TextUi
from appearance.graphics.sprites import SpritesLoader
from appearance.language import Language
from appearance.layer import Layer
from files import read_build_info
from game_session_saver import get_saved_maps, get_tutorials
from mathematics.rectangle import Rectangle, RectangleBuilder
from mathematics.vector import Vector2Int, Vector2
from observer import Event


@frozen
class MainMenuUiLayerMaker:
    _drawer: proto.UiDrawer
    _screen_shape: Vector2Int

    _language: Language = Factory(Language.from_meta)
    _sprites_loader: SpritesLoader = Factory(SpritesLoader.from_meta)

    def make(self,
             on_map_was_selected: Callable[[str], None],
             on_exit_was_pressed: Callable[[], None]) -> Layer:
        play_was_pressed = Event[None]()
        tutorial_was_pressed = Event[None]()
        to_main_menu_was_pressed = Event[None]()

        label = self._make_label(play_was_pressed.invoke, tutorial_was_pressed.invoke, on_exit_was_pressed)
        map_selection = self._make_map_selection(get_saved_maps(), on_map_was_selected,
                                                 to_main_menu_was_pressed.invoke)
        tutorial_selection = self._make_map_selection(get_tutorials(), on_map_was_selected,
                                                      to_main_menu_was_pressed.invoke)

        map_selection.set_activity(False)
        tutorial_selection.set_activity(False)
        play_was_pressed.subscribe(lambda: label.set_activity(False))
        play_was_pressed.subscribe(lambda: map_selection.set_activity(True))
        tutorial_was_pressed.subscribe(lambda: label.set_activity(False))
        tutorial_was_pressed.subscribe(lambda: tutorial_selection.set_activity(True))
        to_main_menu_was_pressed.subscribe(lambda: label.set_activity(True))
        to_main_menu_was_pressed.subscribe(lambda: map_selection.set_activity(False))
        to_main_menu_was_pressed.subscribe(lambda: tutorial_selection.set_activity(False))

        return Layer.as_multiple([label, map_selection, tutorial_selection])

    def _make_map_selection(self,
                            map_names: list[str],
                            on_map_was_selected: Callable[[str], None],
                            on_to_main_menu_was_pressed: Callable[[], None]) -> Layer:
        layers = [
            self._make_map_selection_buttons(map_names, on_map_was_selected),
            self._make_back_button(on_to_main_menu_was_pressed),
        ]
        return Layer.as_multiple(layers)

    def _make_map_selection_buttons(self,
                                    map_names: list[str],
                                    on_map_was_selected: Callable[[str], None]) -> VerticalLayoutUi:
        buttons_shape = Vector2Int(5, 5)

        buttons = list[ButtonUi]()
        for map_name in map_names:
            buttons.append(self._make_map_selection_button(map_name, on_map_was_selected))

        assert len(buttons) <= buttons_shape.x * buttons_shape.y

        layout = VerticalLayoutUi(self._get_maps_buttons_rectangle(), margin_ratio=.2)
        for index in range(0, len(buttons), buttons_shape.x):
            row = buttons[index:index + buttons_shape.x]
            horizontal = HorizontalLayoutUi(Rectangle.zero())
            layout.append(horizontal)
            horizontal.extend(row)
            while len(horizontal) < buttons_shape.x:
                horizontal.append(BoxUi(Rectangle.zero()))

        while len(layout) < buttons_shape.y:
            layout.append(BoxUi(Rectangle.zero()))

        return layout

    def _make_map_selection_button(self, map_name: str, on_map_was_selected: Callable[[str], None]) -> ButtonUi:
        return self._make_null_button(map_name, lambda: on_map_was_selected(map_name))

    def _get_maps_buttons_rectangle(self) -> Rectangle:
        margin = 20
        width = self._screen_shape.x - margin * 2
        height = self._screen_shape.y * 5 / 6 - margin * 2

        return (RectangleBuilder(self._screen_shape)
                .from_left_up()
                .set_shape(Vector2(width, height))
                .move(Vector2(margin, margin))
                .adjust_for_shape()
                .build())

    def _make_back_button(self, on_to_main_menu_was_pressed: Callable[[], None]) -> ButtonUi:
        button = self._make_null_button(self._language.get_back_message(), on_to_main_menu_was_pressed)
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

    def _make_label(self,
                    on_play_was_pressed: Callable[[], None],
                    on_tutorial_was_pressed: Callable[[], None],
                    on_exit_was_pressed: Callable[[], None]) -> Layer:
        layers = [
            self._make_title(),
            self._make_buttons(on_play_was_pressed, on_tutorial_was_pressed, on_exit_was_pressed),
            self._make_build_info(),
        ]

        return Layer.as_multiple(layers)

    def _make_buttons(self,
                      on_play_was_pressed: Callable[[], None],
                      on_tutorial_was_pressed: Callable[[], None],
                      on_exit_was_pressed: Callable[[], None]) -> Layer:
        buttons = [
            self._make_null_button(self._language.get_play_message(), on_play_was_pressed),
            self._make_null_button(self._language.get_tutorial_message(), on_tutorial_was_pressed),
            self._make_null_button(self._language.get_exit_message(), on_exit_was_pressed),
        ]
        layout = VerticalLayoutUi(self._get_buttons_rectangle(), margin_ratio=0.1)
        layout.extend(buttons)
        return layout.layer

    def _get_buttons_rectangle(self) -> Rectangle:
        center_x = self._screen_shape.x / 2
        width = self._screen_shape.x / 4
        x = center_x - width / 2
        height = self._screen_shape.y / 3
        bottom_margin = self._screen_shape.y / 10

        return (RectangleBuilder(self._screen_shape)
                .from_left_bottom()
                .set_shape(Vector2(width, height))
                .move(Vector2(x, bottom_margin))
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

    def _make_title(self) -> Layer:
        title = TextUi.make(self._drawer,
                            self._get_title_rectangle(),
                            TextData.debug("HexWar"),
                            is_center=True)
        return title.layer

    def _get_title_rectangle(self) -> Rectangle:
        center_x = self._screen_shape.x / 2
        width = self._screen_shape.x / 2
        x = center_x - width / 2
        height = self._screen_shape.y / 3
        top_margin = self._screen_shape.y / 10

        return (RectangleBuilder(self._screen_shape)
                .from_left_up()
                .set_shape(Vector2(width, height))
                .move(Vector2(x, top_margin))
                .adjust_for_shape()
                .build())

    def _make_build_info(self) -> Layer:
        shape = Vector2(self._screen_shape.x / 2, 15)
        title = TextUi.make(self._drawer,
                            Rectangle(Vector2.zero(), shape),
                            TextData.debug(_get_version_message()))
        title.set_rectangle(RectangleBuilder(self._screen_shape)
                            .from_right_bottom()
                            .move(Vector2(5, 5))
                            .set_shape(title.text_shape)
                            .adjust_for_shape()
                            .build())
        return title.layer


def _get_version_message() -> str:
    version_prefix = "version_prefix"
    version = "version"
    date = "date"
    build_info = read_build_info()
    return f"{build_info[version_prefix]} {build_info[version]} from {build_info[date]}"
