from typing import Callable

from attrs import frozen, Factory

import appearance.protocols as proto
from appearance.UI.button import ButtonUi, get_image_rectangle
from appearance.UI.text import TextData, TextUi
from appearance.graphics.sprites import SpritesLoader
from appearance.language import Language
from appearance.layer import Layer
from core.protocols import Player
from mathematics.rectangle import Rectangle, RectangleBuilder
from mathematics.vector import Vector2Int, Vector2
from observer import OnEventSubscriber


@frozen
class PlayersSelectionUiLayerMaker:
    _drawer: proto.UiDrawer
    _screen_shape: Vector2Int

    _language: Language = Factory(Language.from_meta)
    _sprites_loader: SpritesLoader = Factory(SpritesLoader.from_meta)

    def make(self,
             on_exit_was_pressed: Callable[[], None],
             on_play_was_pressed: Callable[[], None],
             selected_players_were_changed: OnEventSubscriber[list[Player], None]) -> Layer:
        layers = [
            self._make_back_button(on_exit_was_pressed),
            self._make_play_button(on_play_was_pressed),
            self._make_selected_players_text(selected_players_were_changed),
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

    def _make_play_button(self, on_play_was_pressed: Callable[[], None]) -> ButtonUi:
        button = self._make_null_button(self._language.get_play_message(), on_play_was_pressed)
        button.set_rectangle(self._get_play_button_rectangle())
        return button

    def _get_play_button_rectangle(self) -> Rectangle:
        width = self._screen_shape.x / 10
        height = self._screen_shape.y / 15

        return (RectangleBuilder(self._screen_shape)
                .from_right_bottom()
                .set_shape(Vector2(width, height))
                .move(Vector2(20, 20))
                .adjust_for_shape()
                .build())

    def _make_selected_players_text(self,
                                    selected_players_were_changed: OnEventSubscriber[list[Player], None]) -> TextUi:
        text = TextUi.make(self._drawer,
                           self._get_selected_players_text_rectangle(),
                           TextData.debug(self._language.get_selected_players_message([])))

        selected_players_were_changed.subscribe(lambda selected_players: text.set_text(
            self._language.get_selected_players_message([player.data.name for player in selected_players])))

        return text

    def _get_selected_players_text_rectangle(self) -> Rectangle:
        height = self._screen_shape.y / 20
        width = self._screen_shape.x * .8

        return (RectangleBuilder(self._screen_shape)
                .from_left_up()
                .set_shape(Vector2(width, height))
                .move(Vector2(20, 20))
                .adjust_for_shape()
                .build())

    def _make_null_button(self, text: str, on_button_pressed: Callable[[], None]) -> ButtonUi:
        return ButtonUi.make_null(text, on_button_pressed, self._sprites_loader, self._drawer)
