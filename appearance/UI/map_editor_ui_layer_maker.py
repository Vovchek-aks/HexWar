from typing import Callable

from attrs import frozen, Factory

import appearance.protocols as proto
from appearance.UI.button import ButtonUi, get_image_rectangle, SwitchButtonUi
from appearance.UI.layouts import HorizontalLayoutUi, VerticalLayoutUi
from appearance.UI.layouts.layout import LayoutUi
from appearance.UI.text import TextData, TextUi
from appearance.UI.text.test_size_synchroniser import TextSizeSynchroniser
from appearance.UI.two_buttons_value_changer import TwoButtonsValueChanger, ListChanger, ValueChanger
from appearance.UI.two_buttons_value_changer.int_changer import IntChanger
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
            self._make_transform_switcher(),
            self._make_player_adding_menu(),
        ]

        return Layer.as_multiple(layers)

    def _make_player_adding_menu(self) -> Layer:
        layout = VerticalLayoutUi(RectangleBuilder(self._screen_shape)
                                  .from_left_up()
                                  .move(Vector2(20, 20))
                                  .set_shape(Vector2(self._screen_shape.x / 5,
                                                     self._screen_shape.y * .4))
                                  .adjust_for_shape()
                                  .build(),
                                  reserved=5,
                                  margin_ratio=.2)
        synchroniser = TextSizeSynchroniser()
        layout.append(self._make_null_button("aboba", lambda: None))
        self._add_changer(synchroniser, layout, "R", IntChanger(128, 0, 255), changers_count=5, name_size_ratio=.2)
        self._add_changer(synchroniser, layout, "G", IntChanger(128, 0, 255), changers_count=5, name_size_ratio=.2)
        self._add_changer(synchroniser, layout, "B", IntChanger(128, 0, 255), changers_count=5, name_size_ratio=.2)
        layout.append(add_player := self._make_null_button("aboba", lambda: None))
        synchroniser.append(add_player.text)
        synchroniser.synchronise()
        return layout.layer

    def _add_changer[T](self,
                        synchroniser: TextSizeSynchroniser,
                        layout: LayoutUi,
                        text: str,
                        changer: ValueChanger[T],
                        *,
                        changers_count: int,
                        name_size_ratio: float = .5) -> None:
        text = f"{text}:"
        margin_ratio = .13
        rectangle = Rectangle(Vector2.zero(),
                              Vector2(changers_count * layout.rectangle.shape.x / layout.rectangle.shape.y,
                                      1 - layout.margin_ratio) * 100)
        horizontal = HorizontalLayoutUi(rectangle, margin_ratio=margin_ratio, reserved=2)
        layout.append(horizontal)

        # w / (w + 1) = r
        # w = rw + r
        # w(1 - r) = r
        # w = r / (1 - r)
        text_weight = name_size_ratio / (1 - name_size_ratio)

        horizontal.append(text_ui := TextUi.make_with_anchors(self._drawer, Rectangle.zero(), TextData.debug(text),
                                                              anchor_x=TextUi.RIGHT, anchor_y=TextUi.CENTER),
                          weight=text_weight)
        horizontal.append(TwoButtonsValueChanger.make_horizontal(
            Rectangle(Vector2.zero(), rectangle.shape.with_x(rectangle.shape.x *
                                                             (1 - margin_ratio) / (text_weight + 1))),
            changer, self._sprites_loader, self._drawer))
        synchroniser.append(text_ui)

    def _make_back_button(self, on_exit_was_pressed: Callable[[], None]) -> ButtonUi:
        button = self._make_null_button(self._language.get_to_main_menu_message(), on_exit_was_pressed)
        button.set_rectangle(self._get_back_button_rectangle())
        return button

    def _get_back_button_rectangle(self) -> Rectangle:
        width = self._screen_shape.x / 8
        height = self._screen_shape.y / 20

        return (RectangleBuilder(self._screen_shape)
                .from_left_bottom()
                .set_shape(Vector2(width, height))
                .move(Vector2(20, 20))
                .adjust_for_shape()
                .build())

    def _make_transform_switcher(self) -> TwoButtonsValueChanger[str]:
        transforms = self._map_editor.transforms

        transform_switcher = TwoButtonsValueChanger.make_horizontal(self._get_transform_switcher_rectangle(),
                                                                    ListChanger(transforms),
                                                                    self._sprites_loader,
                                                                    self._drawer)
        transform_switcher.value_had_changed.subscribe(lambda transform: self._map_editor.set(transform))

        return transform_switcher

    def _get_transform_switcher_rectangle(self) -> Rectangle:
        width = self._screen_shape.x / 4
        height = self._screen_shape.y / 20

        return (RectangleBuilder(self._screen_shape)
                .from_right_bottom()
                .set_shape(Vector2(width, height))
                .move(Vector2(20, 20))
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
