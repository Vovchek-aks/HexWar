from typing import Callable

from attrs import frozen, Factory

import appearance.protocols as proto
from appearance.UI.button import ButtonUi, get_image_rectangle
from appearance.UI.image import ImageUi
from appearance.UI.layouts import HorizontalLayoutUi, VerticalLayoutUi
from appearance.UI.layouts.layout import LayoutUi
from appearance.UI.line_edit.line_edit import LineEditUi
from appearance.UI.number_shortener import NumberShortener
from appearance.UI.text import TextData, TextUi, TextDataBuilder
from appearance.UI.text.test_size_synchroniser import TextSizeSynchroniser
from appearance.UI.two_buttons_value_changer import TwoButtonsValueChanger, ListChanger, ValueChanger
from appearance.UI.two_buttons_value_changer.int_changer import IntChanger
from appearance.game_engine.game_engine_arc.window import Window
from appearance.graphics.colors import RECTANGLE_BUTTON
from appearance.graphics.sprites import SpritesLoader, Sprite
from appearance.language import Language
from appearance.layer import Layer
from color import Color
from core.player import Player, PlayerData
from core.player.inputers.bot_player_inputer import BotPlayerInputer
from core.player.inputers.bots import BotIgor
from core.resources import ResourcesStockpile, Dollars, LightIndustryProducts, HeavyIndustryProducts
from map_editor import MapEditor
from mathematics.rectangle import Rectangle, RectangleBuilder
from mathematics.vector import Vector2Int, Vector2
from observer import Event, OnEventSubscriber


@frozen
class MapEditorUiLayerMaker:
    _window: Window
    _drawer: proto.UiDrawer
    _screen_shape: Vector2Int
    _map_editor: MapEditor
    _mouse_movement_observer: proto.MouseMovementObserver

    _language: Language = Factory(Language.from_meta)
    _sprites_loader: SpritesLoader = Factory(SpritesLoader.from_meta)

    def make(self, on_exit_was_pressed: Callable[[], None]) -> Layer:
        exit_was_pressed = Event[None]()
        exit_was_pressed.subscribe(on_exit_was_pressed)
        layers = [
            self._make_back_button(exit_was_pressed.invoke),
            changer := self._make_transform_switcher(),
            self._make_player_adding_menu(changer.changer, exit_was_pressed.subscriber),
            self._make_player_edit_menu(changer),
        ]

        return Layer.as_multiple(layers)

    def _make_player_edit_menu(self, transforms_switcher: TwoButtonsValueChanger[str]) -> Layer:
        layout = VerticalLayoutUi(RectangleBuilder(self._screen_shape)
                                  .from_right_up()
                                  .move(Vector2(20, 20))
                                  .set_shape(Vector2(self._screen_shape.x / 4.5,
                                                     self._screen_shape.y * .24))
                                  .adjust_for_shape()
                                  .build(),
                                  reserved=3,
                                  margin_ratio=.2)

        def get_player() -> Player | None:
            players = [player for player in self._map_editor.session.master.players
                       if player.data.name == transforms_switcher.value]
            assert len(players) < 2
            if not players:
                return None
            return players[0]

        def on_transform_value_had_changed(_: str) -> None:
            player = get_player()
            layout.layer.set_activity(bool(player))
            if not player:
                return

            dollars.set(player.resources.get(Dollars).amount)
            light_industry_products.set(player.resources.get(LightIndustryProducts).amount)
            heavy_industry_products.set(player.resources.get(HeavyIndustryProducts).amount)

        ((dollars := self._append_square_image_and_value_changer_to(layout,
                                                                    self._sprites_loader.load_resource_sprite(Dollars),
                                                                    IntChanger(0, 0, 1_000_000_000, 250_000)))
        .value_had_changed.subscribe(
            lambda value:
            get_player().resources.set(Dollars(value))
            if get_player() else None)
        )
        ((light_industry_products := self._append_square_image_and_value_changer_to(
            layout,
            self._sprites_loader.load_resource_sprite(LightIndustryProducts),
            IntChanger(0, 0, 1_000_000_000, 1_000)
        )).value_had_changed.subscribe(
            lambda value:
            get_player().resources.set(LightIndustryProducts(value))
            if get_player() else None)
        )
        ((heavy_industry_products := self._append_square_image_and_value_changer_to(
            layout,
            self._sprites_loader.load_resource_sprite(
                HeavyIndustryProducts),
            IntChanger(0, 0, 1_000_000_000,
                       1_000)
        )).value_had_changed.subscribe(
            lambda value:
            get_player().resources.set(HeavyIndustryProducts(value))
            if get_player() else None)
        )

        layout.layer.set_activity(False)
        transforms_switcher.value_had_changed.subscribe(on_transform_value_had_changed)
        return layout.layer

    def _append_square_image_and_value_changer_to[T](self,
                                                     layout: LayoutUi,
                                                     sprite: Sprite,
                                                     changer: ValueChanger[T]) -> TwoButtonsValueChanger[T]:
        horizontal = HorizontalLayoutUi(Rectangle.ones(), reserved=2, margin_ratio=0.05)
        layout.append(horizontal)
        height = horizontal.rectangle.shape.y
        non_empty_width = horizontal.rectangle.shape.x * (1 - horizontal.margin_ratio)
        ratio = height / non_empty_width
        weight = ratio / (1 - ratio)
        horizontal.append(ImageUi.make(self._drawer, Rectangle.ones(), sprite), weight=weight)

        rectangle = Rectangle(Vector2.zero(),
                              Vector2(layout.elements_count * layout.rectangle.shape.x / layout.rectangle.shape.y,
                                      1 - layout.margin_ratio) * 100)
        horizontal.append(
            value_changer := TwoButtonsValueChanger.make_horizontal(
                Rectangle(
                    Vector2.zero(),
                    rectangle.shape.with_x(rectangle.shape.x
                                           * (1 - horizontal.margin_ratio)
                                           / (weight + 1))
                ),
                changer,
                self._sprites_loader,
                self._drawer,
                self._mouse_movement_observer,
                get_text=NumberShortener.shorten
            )
        )

        return value_changer

    def _make_player_adding_menu(self,
                                 transforms_changer: ListChanger[str],
                                 exit_was_pressed: OnEventSubscriber[None]) -> Layer:
        layout = VerticalLayoutUi(RectangleBuilder(self._screen_shape)
                                  .from_left_up()
                                  .move(Vector2(20, 20))
                                  .set_shape(Vector2(self._screen_shape.x / 5,
                                                     self._screen_shape.y * .4))
                                  .adjust_for_shape()
                                  .build(),
                                  reserved=5,
                                  margin_ratio=.2)

        def can_append_player() -> bool:
            name = player_name.text
            if name.isspace() or not name:
                return False

            if name == self._language.get_players_name_message():
                return False

            if name in transforms_changer.values:
                return False

            return True

        def try_append_player() -> None:
            if not can_append_player():
                return

            name = player_name.text
            color = Color(color_r.value, color_g.value, color_b.value)
            player = Player(PlayerData(color, name), BotPlayerInputer(BotIgor()), ResourcesStockpile())

            self._map_editor.append_player_transform(player)
            transforms_changer.insert(0, name)
            player_name.set_text(self._language.get_players_name_message())

        synchroniser = TextSizeSynchroniser()
        line_edit_text_data = (TextDataBuilder()
                               .debug_font(round(0.03 * self._screen_shape.y))
                               .set_text(self._language.get_players_name_message())
                               .white_colored()
                               .build())
        player_name = LineEditUi.make(self._window, exit_was_pressed, Rectangle.ones(), line_edit_text_data)
        layout.append(player_name)
        self._add_changer(synchroniser, layout, "R", color_r := IntChanger(125, 0, 255, 5), name_size_ratio=.2)
        self._add_changer(synchroniser, layout, "G", color_g := IntChanger(125, 0, 255, 5), name_size_ratio=.2)
        self._add_changer(synchroniser, layout, "B", color_b := IntChanger(125, 0, 255, 5), name_size_ratio=.2)
        layout.append(add_player := self._make_null_button(self._language.get_add_player_message(), try_append_player))
        synchroniser.append(add_player.text)
        synchroniser.synchronise()
        return layout.layer

    def _add_changer[T](self,
                        synchroniser: TextSizeSynchroniser,
                        layout: LayoutUi,
                        text: str,
                        changer: ValueChanger[T],
                        *,
                        name_size_ratio: float = .5) -> None:
        text = f"{text}:"
        margin_ratio = .13
        rectangle = Rectangle(Vector2.zero(),
                              Vector2(layout.elements_count * layout.rectangle.shape.x / layout.rectangle.shape.y,
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
            changer, self._sprites_loader, self._drawer, self._mouse_movement_observer))
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
                                                                    self._drawer,
                                                                    self._mouse_movement_observer)
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
        button_background = self._sprites_loader.load_button_3_to_2().colored_in(RECTANGLE_BUTTON)
        button_text = TextData.debug(text)
        button = ButtonUi.make(self._drawer,
                               get_image_rectangle(Rectangle(Vector2.zero(), button_background.shape.as_vector2)),
                               button_background,
                               self._mouse_movement_observer,
                               button_text)
        button.was_clicked.subscribe(on_button_pressed)
        return button
