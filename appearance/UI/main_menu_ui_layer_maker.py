from typing import Callable
import webbrowser
import subprocess

from attrs import frozen, Factory

import appearance.protocols as proto
from appearance.UI.button import ButtonUi
from appearance.UI.image import ImageUi
from appearance.UI.layouts import VerticalLayoutUi, HorizontalLayoutUi
from appearance.UI.layouts.layout import LayoutUi
from appearance.UI.text import TextData, TextUi, TextDataBuilder
from appearance.UI.text.test_size_synchroniser import TextSizeSynchroniser
from appearance.UI.two_buttons_value_changer import TwoButtonsValueChanger, ValueChanger, ListChanger
from appearance.UI.two_buttons_value_changer.int_changer import IntChanger
from appearance.graphics.sprites import SpritesLoader
from appearance.language import Language
from appearance.layer import Layer
from appearance.settings import Settings, MUSIC, VOICE, EFFECTS, LANGUAGE, IS_FULLSCREEN, WIDTH, HEIGHT, \
    NEED_TO_PLAY_BOT_MOVE_ANIMATIONS
from files import read_build_info, read_random_bot_names
from game_session_saver import get_saved_maps, get_tutorials, SAVE_FOLDER, EDIT_MAP_FILE
from mathematics.rectangle import Rectangle, RectangleBuilder
from mathematics.vector import Vector2Int, Vector2
from observer import Event
from statuses import Status, MISSING

_AUDIO_SETTER_STEPS = 100
_AUDIO_SETTER_STEP = 5


@frozen
class MainMenuUiLayerMaker:
    _drawer: proto.UiDrawer
    _screen_shape: Vector2Int

    _language: Language = Factory(Language.from_meta)
    _sprites_loader: SpritesLoader = Factory(SpritesLoader.from_meta)

    @property
    def _screen_rectangle(self) -> Rectangle:
        return Rectangle(Vector2.zero(), self._screen_shape.as_vector2)

    def make(self,
             on_map_was_selected: Callable[[str, Status | int], None],
             on_exit_was_pressed: Callable[[], None],
             reload: Callable[[], None]) -> Layer:
        play_was_pressed = Event[None]()
        tutorial_was_pressed = Event[None]()
        settings_was_pressed = Event[None]()
        authors_was_pressed = Event[None]()
        map_editor_was_pressed = Event[None]()
        to_main_menu_was_pressed = Event[None]()

        tabs = list[Layer]()

        def turn_tabs_off() -> None:
            for tab in tabs:
                tab.set_activity(False)

        tabs.append(self._make_label(turn_tabs_off, to_main_menu_was_pressed, play_was_pressed, tutorial_was_pressed,
                                     settings_was_pressed, authors_was_pressed, map_editor_was_pressed,
                                     on_exit_was_pressed))
        tabs.append(self._make_map_selection(turn_tabs_off, get_saved_maps(), on_map_was_selected, play_was_pressed,
                                             to_main_menu_was_pressed))
        tabs.append(self._make_map_selection(turn_tabs_off, get_tutorials(), on_map_was_selected, tutorial_was_pressed,
                                             to_main_menu_was_pressed, allow_random_players=False))
        tabs.append(self._make_settings_tab(turn_tabs_off, settings_was_pressed, to_main_menu_was_pressed, reload))
        tabs.append(self._make_authors_tab(turn_tabs_off, authors_was_pressed, to_main_menu_was_pressed))
        tabs.append(self._make_map_editor_tab(turn_tabs_off, map_editor_was_pressed, to_main_menu_was_pressed))

        return Layer.as_multiple(tabs)

    def _make_map_editor_tab(self,
                             turn_tabs_off: Callable[[], None],
                             tab_was_selected: Event[None],
                             to_main_menu_was_pressed: Event[None]) -> Layer:
        layers = [
            self._make_map_editor_buttons(),
            self._make_back_button(to_main_menu_was_pressed.invoke, turn_tabs_off),
        ]
        layer = Layer.as_multiple(layers)
        layer.set_activity(False)
        tab_was_selected.subscribe(lambda: layer.set_activity(True))
        return layer

    def _make_map_editor_buttons(self) -> LayoutUi:
        synchroniser = TextSizeSynchroniser()

        layout = VerticalLayoutUi(self._get_map_editor_buttons_rectangle(), reserved=2, margin_ratio=.15)
        top_layout = VerticalLayoutUi(self._get_map_editor_buttons_rectangle(), reserved=2, margin_ratio=.3)
        layout.append(top_layout)
        bottom_layout = VerticalLayoutUi(self._get_map_editor_buttons_rectangle(), reserved=2, margin_ratio=.15)
        layout.append(bottom_layout)
        new_open = HorizontalLayoutUi(self._get_map_editor_buttons_rectangle(), reserved=2, margin_ratio=.05)
        bottom_layout.append(new_open)

        rectangle = Rectangle(Vector2.zero(),
                              Vector2(2 * top_layout.rectangle.shape.x / top_layout.rectangle.shape.y,
                                      (1 - top_layout.margin_ratio)) * 100)

        width = self._language.get_width_message()
        height = self._language.get_height_message()
        changers = {
            width: IntChanger(50, 5, 500, 5),
            height: IntChanger(50, 5, 500, 5),
        }
        self._add_changer(synchroniser, top_layout, width, width, changers, {}, rectangle)
        self._add_changer(synchroniser, top_layout, height, height, changers, {}, rectangle)
        new_open.append(new_button := self._make_null_button(self._language.get_make_new_map_message(), lambda: None))
        new_open.append(
            open_button := self._make_null_button(self._language.get_load_existing_map_message(), lambda: None))
        bottom_layout.append(open_in_explorer := self._make_null_button(
            self._language.get_open_file_in_explorer_message(),
            lambda: subprocess.run(['explorer', '/select,', SAVE_FOLDER / EDIT_MAP_FILE])
        ))

        synchroniser.extend(new_button.text, open_button.text, open_in_explorer.text)
        synchroniser.synchronise()

        return layout

    def _get_map_editor_buttons_rectangle(self) -> Rectangle:
        width = self._screen_shape.x / 2
        height = self._screen_shape.y / 2
        bottom_margin = (self._screen_shape.y - height) / 2

        center_x = self._screen_shape.x / 2
        x = center_x - width / 2

        return (RectangleBuilder(self._screen_shape)
                .from_left_bottom()
                .set_shape(Vector2(width, height))
                .move(Vector2(x, bottom_margin))
                .adjust_for_shape()
                .build())

    def _make_authors_tab(self,
                          turn_tabs_off: Callable[[], None],
                          tab_was_selected: Event[None],
                          to_main_menu_was_pressed: Event[None]) -> Layer:
        synchroniser = TextSizeSynchroniser()
        layout = HorizontalLayoutUi(self._get_authors_cards_rectangle(), margin_ratio=.21, reserved=2)
        self._add_author_card("_cyberDilf",
                              self._sprites_loader.load_cyber_dilf(),
                              self._language.get_cyber_dilf_roles(),
                              synchroniser,
                              [
                                  self._make_link(self._sprites_loader.load_telegram(),
                                                  "https://t.me/cyberdilf"),
                                  self._make_link(self._sprites_loader.load_twitch(),
                                                  "https://www.twitch.tv/cyberdilff"),
                                  self._make_link(self._sprites_loader.load_itch(),
                                                  "https://cyberdilf.itch.io/"),
                                  self._make_link(self._sprites_loader.load_github(),
                                                  "https://github.com/Vovchek-aks"),
                              ],
                              layout)
        self._add_author_card("Divan0_0",
                              self._sprites_loader.load_divan(),
                              self._language.get_divan_roles(),
                              synchroniser,
                              [
                                  self._make_link(self._sprites_loader.load_github(),
                                                  "https://github.com/Ktoto888550303"),
                              ],
                              layout)
        synchroniser.synchronise()
        layers = [
            layout,
            self._make_back_button(to_main_menu_was_pressed.invoke, turn_tabs_off),
        ]
        layer = Layer.as_multiple(layers)
        layer.set_activity(False)
        tab_was_selected.subscribe(lambda: layer.set_activity(True))
        return layer

    def _get_authors_cards_rectangle(self) -> Rectangle:
        width_to_height = 2.5 / 3
        center = self._screen_shape.as_vector2 / 2
        height = self._screen_shape.y
        width = height * width_to_height
        shape = Vector2(width, height)
        return Rectangle(center - shape / 2, shape)

    def _make_link(self, sprite: proto.Sprite, url: str) -> ButtonUi:
        button = ButtonUi.make(self._drawer,
                               Rectangle(Vector2.zero(), sprite.shape.as_vector2),
                               sprite,
                               TextData.debug(' '))
        button.was_clicked.subscribe(lambda: webbrowser.open(url))
        return button

    def _add_author_card(self,
                         name: str,
                         sprite: proto.Sprite,
                         roles: list[str],
                         roles_synchroniser: TextSizeSynchroniser,
                         links: list[ButtonUi],
                         layout: LayoutUi) -> None:
        max_links = 4
        max_roles = 6
        assert len(links) <= max_links
        assert len(roles) <= max_links

        card = VerticalLayoutUi(Rectangle(Vector2.zero(), Vector2(200, 600)), reserved=3)
        layout.append(card)
        roles_ui = VerticalLayoutUi(Rectangle.zero(), reserved=max_roles)
        card.append(roles_ui)

        while len(roles) < max_roles:
            roles.insert(0, ' ')
        for role in roles:
            data = TextDataBuilder.like(TextData.debug(role)).button_font().build()
            line = TextUi.make(self._drawer, Rectangle.zero(), data, is_center=True)
            roles_ui.append(line)
            roles_synchroniser.append(line)

        card.append(ImageUi.make(self._drawer, Rectangle(Vector2.zero(), Vector2.ones()), sprite))

        links_halfer = VerticalLayoutUi(Rectangle.zero(), margin_ratio=.2, reserved=3)
        card.append(links_halfer)
        links_ui = HorizontalLayoutUi(Rectangle.zero(), reserved=max_links)
        links_halfer.append(TextUi.make(self._drawer, Rectangle.zero(), TextData.debug(name), is_center=True))
        links_halfer.append(links_ui)
        links_ui.extend(links)

    def _make_map_selection(self,
                            turn_tabs_off: Callable[[], None],
                            map_names: list[str],
                            on_map_was_selected: Callable[[str, Status | int], None],
                            tab_was_selected: Event[None],
                            to_main_menu_was_pressed: Event[None],
                            allow_random_players: bool = True) -> Layer:
        on_map_name_was_selected = Event[str, None]()
        players_mode_selection, players_mode, players_count = self._make_players_mode_selection()
        layers = [
            self._make_map_selection_buttons(map_names, on_map_name_was_selected.invoke),
            self._make_back_button(to_main_menu_was_pressed.invoke, turn_tabs_off),
        ]
        if allow_random_players:
            layers.append(players_mode_selection)

        layer = Layer.as_multiple(layers)
        layer.set_activity(False)
        tab_was_selected.subscribe(lambda: layer.set_activity(True))

        on_map_name_was_selected.subscribe(
            lambda name: on_map_was_selected(name,
                                             players_count.value
                                             if allow_random_players and
                                                players_mode.value == self._language.get_players_mode_random_message()
                                             else
                                             MISSING))

        return layer

    def _make_players_mode_selection(self) -> tuple[Layer, ValueChanger[str], ValueChanger[int]]:
        mode_changer = ListChanger([self._language.get_players_mode_random_message(),
                                    self._language.get_players_mode_states_message()])
        min_count = 2
        max_count = len(read_random_bot_names())
        start_count = (max_count + min_count) // 2
        count_changer = IntChanger(start_count, min_count, max_count, 5)

        title_synchroniser = TextSizeSynchroniser()
        synchroniser = TextSizeSynchroniser()
        layout = HorizontalLayoutUi(self._get_players_mode_selection_rectangle(), reserved=2)
        count, _ = self._add_named_value_changer(title_synchroniser, synchroniser, layout,
                                                 self._language.get_count_message(), count_changer)
        count.set_activity(False)
        _, mode = self._add_named_value_changer(title_synchroniser, synchroniser,
                                                layout, self._language.get_players_mode_message(), mode_changer)
        title_synchroniser.synchronise()
        synchroniser.synchronise()

        mode.next()
        mode.value_had_changed.subscribe(
            lambda value: count.set_activity(value == self._language.get_players_mode_random_message()))
        return layout.layer, mode_changer, count_changer

    def _get_players_mode_selection_rectangle(self) -> Rectangle:
        return (RectangleBuilder(self._screen_shape)
                .from_right_bottom()
                .move(Vector2(20, 20))
                .set_shape(Vector2(self._screen_shape.x / 3, self._screen_shape.y / 10))
                .adjust_for_shape()
                .build())

    def _add_named_value_changer[T](self,
                                    title_synchroniser: TextSizeSynchroniser,
                                    synchroniser: TextSizeSynchroniser,
                                    outer_layout: LayoutUi,
                                    name: str,
                                    changer: ValueChanger[T]) -> tuple[Layer, TwoButtonsValueChanger[T]]:
        margin_ratio = .1
        layout = VerticalLayoutUi(Rectangle.zero(), margin_ratio, reserved=2)
        outer_layout.append(layout)
        layout.append(text := TextUi.make(self._drawer, Rectangle.zero(), TextData.debug(name), is_center=True))
        title_synchroniser.append(text)
        layout.append(value_changer := TwoButtonsValueChanger.make_horizontal(
            Rectangle(Vector2.zero(), Vector2(layout.rectangle.shape.x,
                                              layout.rectangle.shape.y * (1 - margin_ratio * 2) / 2)),
            changer, self._sprites_loader, self._drawer, margin_ratio=.05
        ))
        synchroniser.append(value_changer.text)

        return layout.layer, value_changer

    def _make_map_selection_buttons(self,
                                    map_names: list[str],
                                    on_map_was_selected: Callable[[str], None]) -> VerticalLayoutUi:
        buttons_shape = Vector2Int(5, 5)

        buttons = list[ButtonUi]()
        synchroniser = TextSizeSynchroniser()
        for map_name in map_names:
            buttons.append(button := self._make_map_selection_button(map_name, on_map_was_selected))
            synchroniser.append(button.text)

        assert len(buttons) <= buttons_shape.x * buttons_shape.y

        layout = VerticalLayoutUi(self._get_maps_buttons_rectangle(), margin_ratio=.2, reserved=buttons_shape.y)
        for index in range(0, len(buttons), buttons_shape.x):
            row = buttons[index:index + buttons_shape.x]
            horizontal = HorizontalLayoutUi(Rectangle.zero(), reserved=buttons_shape.x)
            layout.append(horizontal)
            horizontal.extend(row)

        synchroniser.synchronise()

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

    def _make_settings_tab(self,
                           turn_tabs_off: Callable[[], None],
                           tab_was_selected: Event[None],
                           to_main_menu_was_pressed: Event[None],
                           reload: Callable[[], None]) -> Layer:
        value_changers = dict[str, TwoButtonsValueChanger[str | int]]()
        layers = [
            self._make_settings_changers(to_main_menu_was_pressed, value_changers),
            self._make_back_button(to_main_menu_was_pressed.invoke, turn_tabs_off),
            self._make_apply_button(value_changers, reload),
        ]
        layer = Layer.as_multiple(layers)
        layer.set_activity(False)
        tab_was_selected.subscribe(lambda: layer.set_activity(True))
        return layer

    def _make_apply_button(self,
                           value_changers: dict[str, TwoButtonsValueChanger[str | int]],
                           reload: Callable[[], None]) -> Layer:
        def apply() -> None:
            settings: dict[str, str | float] = {
                key: value_changers[key].value / _AUDIO_SETTER_STEPS
                for key in (MUSIC, VOICE, EFFECTS)
            }
            settings[LANGUAGE] = value_changers[LANGUAGE].value
            settings[IS_FULLSCREEN] = value_changers[IS_FULLSCREEN].value == self._language.get_fullscreen_message()
            settings[WIDTH] = value_changers[WIDTH].value
            settings[HEIGHT] = value_changers[HEIGHT].value
            settings[NEED_TO_PLAY_BOT_MOVE_ANIMATIONS] = (value_changers[NEED_TO_PLAY_BOT_MOVE_ANIMATIONS].value
                                                          == self._language.get_on_message())

            Settings.from_keys(settings).save()
            reload()

        button = self._make_null_button(self._language.get_apply_message(), apply)
        button.set_rectangle(self._get_apply_button_rectangle())
        return button.layer

    def _get_apply_button_rectangle(self) -> Rectangle:
        width = self._screen_shape.x / 10
        height = self._screen_shape.y / 15

        return (RectangleBuilder(self._screen_shape)
                .from_right_bottom()
                .set_shape(Vector2(width, height))
                .move(Vector2(20, 20))
                .adjust_for_shape()
                .build())

    def _make_settings_changers(self,
                                to_main_menu_was_pressed: Event[None],
                                value_changers: dict[str, TwoButtonsValueChanger[str | int]]) -> Layer:
        def reset() -> None:
            old_changers = self._get_changers()
            for key, changer in value_changers.items():
                changer.set(old_changers[key].value)

        to_main_menu_was_pressed.subscribe(reset)

        count = 10
        margin_ratio = .3
        layout = VerticalLayoutUi(self._get_changers_rectangle(), margin_ratio=margin_ratio, reserved=count)
        rectangle = Rectangle(Vector2.zero(),
                              Vector2(count * layout.rectangle.shape.x / layout.rectangle.shape.y,
                                      1 - margin_ratio) * 100)

        changers = self._get_changers()
        synchroniser = TextSizeSynchroniser()

        layout.append(audio := TextUi.make(self._drawer, Rectangle.zero(),
                                           TextData.debug(self._language.get_audio_message()), is_center=True))
        self._add_changer(synchroniser, layout, self._language.get_music_volume_message(), MUSIC, changers,
                          value_changers,
                          rectangle)
        self._add_changer(synchroniser, layout, self._language.get_voice_volume_message(), VOICE, changers,
                          value_changers,
                          rectangle)
        self._add_changer(synchroniser, layout, self._language.get_effects_volume_message(), EFFECTS, changers,
                          value_changers, rectangle)

        layout.append(graphics := TextUi.make(self._drawer, Rectangle.zero(),
                                              TextData.debug(self._language.get_graphics_message()), is_center=True))
        self._add_changer(synchroniser, layout, self._language.get_width_message(), WIDTH, changers,
                          value_changers, rectangle)
        self._add_changer(synchroniser, layout, self._language.get_height_message(), HEIGHT, changers,
                          value_changers, rectangle)
        self._add_changer(synchroniser, layout, self._language.get_screen_message(), IS_FULLSCREEN, changers,
                          value_changers, rectangle)

        layout.append(other := TextUi.make(self._drawer, Rectangle.zero(),
                                           TextData.debug(self._language.get_other_message()), is_center=True))
        self._add_changer(synchroniser, layout, self._language.get_selected_language_message(), LANGUAGE, changers,
                          value_changers, rectangle)
        self._add_changer(synchroniser, layout, self._language.get_need_to_play_bot_move_animations_message(),
                          NEED_TO_PLAY_BOT_MOVE_ANIMATIONS, changers, value_changers, rectangle)

        titles_synchroniser = TextSizeSynchroniser()
        titles_synchroniser.extend(other, audio, graphics)

        titles_synchroniser.synchronise()
        synchroniser.synchronise()

        return layout.layer

    def _add_changer[T](self,
                        synchroniser: TextSizeSynchroniser,
                        layout: LayoutUi,
                        text: str,
                        key: str,
                        changers: dict[str, ValueChanger[T]],
                        value_changers: dict[str, TwoButtonsValueChanger[T]],
                        rectangle: Rectangle) -> None:
        changer = changers[key]
        text = f"{text}:"
        margin_ratio = .13
        horizontal = HorizontalLayoutUi(rectangle, margin_ratio=margin_ratio, reserved=2)
        layout.append(horizontal)
        horizontal.append(text_ui := TextUi.make_with_anchors(self._drawer, Rectangle.zero(), TextData.debug(text),
                                                              anchor_x=TextUi.RIGHT, anchor_y=TextUi.CENTER))
        horizontal.append(value_changer := TwoButtonsValueChanger.make_horizontal(
            Rectangle(Vector2.zero(), rectangle.shape.with_x(rectangle.shape.x * (1 - margin_ratio) / 2)), changer,
            self._sprites_loader, self._drawer))
        synchroniser.append(text_ui)
        value_changers[key] = value_changer

    def _get_changers_rectangle(self) -> Rectangle:
        width = self._screen_shape.x / 2
        height = self._screen_shape.y / 1.3
        bottom_margin = (self._screen_shape.y - height) / 1.5

        center_x = self._screen_shape.x / 2
        x = center_x - width / 2

        return (RectangleBuilder(self._screen_shape)
                .from_left_bottom()
                .set_shape(Vector2(width, height))
                .move(Vector2(x, bottom_margin))
                .adjust_for_shape()
                .build())

    def _get_changers(self) -> dict[str, ValueChanger[str | int]]:
        settings = Settings.open()

        languages = self._language.languages()
        languages.remove(settings.selected_language)
        languages.insert(0, settings.selected_language)

        screen_mods = [self._language.get_fullscreen_message(), self._language.get_windowed_message()]
        if not settings.if_fullscreen:
            screen_mods = screen_mods[::-1]

        bot_animation_states = [self._language.get_on_message(), self._language.get_off_message()]
        if not settings.need_to_play_bot_move_animations:
            bot_animation_states = bot_animation_states[::-1]

        audio_changer_range = 0, _AUDIO_SETTER_STEPS, _AUDIO_SETTER_STEP
        screen_shape_changer_range = 400, 6400, 20
        return {
            MUSIC: IntChanger(round(_AUDIO_SETTER_STEPS * settings.music_volume), *audio_changer_range),
            VOICE: IntChanger(round(_AUDIO_SETTER_STEPS * settings.voice_volume), *audio_changer_range),
            EFFECTS: IntChanger(round(_AUDIO_SETTER_STEPS * settings.effects_volume), *audio_changer_range),
            WIDTH: IntChanger(settings.screen_shape.x, *screen_shape_changer_range),
            HEIGHT: IntChanger(settings.screen_shape.y, *screen_shape_changer_range),
            IS_FULLSCREEN: ListChanger(screen_mods),
            LANGUAGE: ListChanger(languages),
            NEED_TO_PLAY_BOT_MOVE_ANIMATIONS: ListChanger(bot_animation_states)
        }

    def _make_back_button(self, on_to_main_menu_was_pressed: Callable[[], None],
                          turn_tabs_off: Callable[[], None]) -> ButtonUi:
        button = self._make_menu_button(self._language.get_back_message(), on_to_main_menu_was_pressed, turn_tabs_off)
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
                    turn_tabs_off: Callable[[], None],
                    to_main_menu_was_pressed: Event[None],
                    play_was_pressed: Event[None],
                    tutorial_was_pressed: Event[None],
                    settings_was_pressed: Event[None],
                    authors_was_pressed: Event[None],
                    map_editor_was_pressed: Event[None],
                    exit_was_pressed: Callable[[], None]) -> Layer:
        layers = [
            self._make_title(),
            self._make_buttons(play_was_pressed, tutorial_was_pressed, settings_was_pressed, authors_was_pressed,
                               map_editor_was_pressed, exit_was_pressed, turn_tabs_off),
            self._make_build_info(),
        ]

        layer = Layer.as_multiple(layers)
        to_main_menu_was_pressed.subscribe(lambda: layer.set_activity(True))

        return layer

    def _make_buttons(self,
                      play_was_pressed: Event[None],
                      tutorial_was_pressed: Event[None],
                      settings_was_pressed: Event[None],
                      authors_was_pressed: Event[None],
                      map_editor_was_pressed: Event[None],
                      exit_was_pressed: Callable[[], None],
                      turn_tabs_off: Callable[[], None]) -> Layer:
        layout = VerticalLayoutUi(self._get_buttons_rectangle(), margin_ratio=0.1, reserved=3)

        tutorial_settings = HorizontalLayoutUi(Rectangle.zero(), reserved=2)
        layout.append(tutorial_settings)
        tutorial_settings.append(tutorial := self._make_menu_button(self._language.get_tutorial_message(),
                                                                    tutorial_was_pressed.invoke, turn_tabs_off))
        tutorial_settings.append(settings := self._make_menu_button(self._language.get_settings_message(),
                                                                    settings_was_pressed.invoke, turn_tabs_off))

        layout.append(self._make_menu_button(self._language.get_play_message(), play_was_pressed.invoke, turn_tabs_off))

        authors_close = HorizontalLayoutUi(Rectangle.zero(), reserved=2)
        layout.append(authors_close)
        authors_close.append(authors := self._make_menu_button(self._language.get_authors_message(),
                                                               authors_was_pressed.invoke, turn_tabs_off))
        authors_close.append(close := self._make_null_button(self._language.get_exit_message(), exit_was_pressed))

        synchroniser = TextSizeSynchroniser()
        synchroniser.extend(tutorial.text, settings.text, close.text, authors.text)
        synchroniser.synchronise()

        map_editor = self._make_menu_button("R", map_editor_was_pressed.invoke, turn_tabs_off)
        map_editor.set_rectangle(RectangleBuilder(self._screen_shape)
                                 .from_left_bottom()
                                 .set_shape(Vector2(50, 50))
                                 .move(Vector2(10, 10))
                                 .adjust_for_shape()
                                 .build())

        return Layer.as_multiple([layout.layer, map_editor])

    def _get_buttons_rectangle(self) -> Rectangle:
        width_to_height_ratio = 1.3
        height = self._screen_shape.y / 3
        center_x = self._screen_shape.x / 2
        width = height * width_to_height_ratio
        x = center_x - width / 2
        bottom_margin = self._screen_shape.y / 10

        return (RectangleBuilder(self._screen_shape)
                .from_left_bottom()
                .set_shape(Vector2(width, height))
                .move(Vector2(x, bottom_margin))
                .adjust_for_shape()
                .build())

    def _make_menu_button(self,
                          text: str,
                          on_button_pressed: Callable[[], None],
                          turn_tabs_off: Callable[[], None]) -> ButtonUi:
        def new_on_button_pressed() -> None:
            turn_tabs_off()
            on_button_pressed()

        return self._make_null_button(text, new_on_button_pressed)

    def _make_null_button(self, text: str, on_button_pressed: Callable[[], None]) -> ButtonUi:
        return ButtonUi.make_null(text, on_button_pressed, self._sprites_loader, self._drawer)

    def _make_title(self) -> Layer:
        title = ImageUi.make(self._drawer, self._get_title_rectangle(), self._sprites_loader.load_logo())
        return title.layer

    def _get_title_rectangle(self) -> Rectangle:
        buttons = self._get_buttons_rectangle()
        _, _, buttons_top, buttons_bottom = buttons.left_right_up_bottom

        width_to_height_ratio = 17 / 5
        possible_height = self._screen_shape.y - buttons_bottom - buttons_top
        height = possible_height * .7
        center_x = self._screen_shape.x / 2
        width = height * width_to_height_ratio
        x = center_x - width / 2
        top_margin = (possible_height - height) / 2

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
    return f"{build_info[version_prefix]} {build_info[version]} from {build_info[date]}  (с) _cyberDilf"
