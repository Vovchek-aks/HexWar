from typing import Callable
import webbrowser

from attrs import frozen, Factory

import appearance.protocols as proto
from appearance.UI.box import BoxUi
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
from appearance.settings import Settings, MUSIC, VOICE, EFFECTS, LANGUAGE
from files import read_build_info
from game_session_saver import get_saved_maps, get_tutorials
from mathematics.rectangle import Rectangle, RectangleBuilder
from mathematics.vector import Vector2Int, Vector2
from observer import Event

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
             on_map_was_selected: Callable[[str], None],
             on_exit_was_pressed: Callable[[], None],
             reload: Callable[[], None]) -> Layer:
        play_was_pressed = Event[None]()
        tutorial_was_pressed = Event[None]()
        settings_was_pressed = Event[None]()
        authors_was_pressed = Event[None]()
        to_main_menu_was_pressed = Event[None]()

        tabs = list[Layer]()

        def turn_tabs_off() -> None:
            for tab in tabs:
                tab.set_activity(False)

        tabs.append(self._make_label(turn_tabs_off, to_main_menu_was_pressed, play_was_pressed, tutorial_was_pressed,
                                     settings_was_pressed, authors_was_pressed, on_exit_was_pressed))
        tabs.append(self._make_map_selection(turn_tabs_off, get_saved_maps(), on_map_was_selected, play_was_pressed,
                                             to_main_menu_was_pressed))
        tabs.append(self._make_map_selection(turn_tabs_off, get_tutorials(), on_map_was_selected, tutorial_was_pressed,
                                             to_main_menu_was_pressed))
        tabs.append(self._make_settings_tab(turn_tabs_off, settings_was_pressed, to_main_menu_was_pressed, reload))
        tabs.append(self._make_authors_tab(turn_tabs_off, authors_was_pressed, to_main_menu_was_pressed))

        return Layer.as_multiple(tabs)

    def _make_authors_tab(self,
                          turn_tabs_off: Callable[[], None],
                          tab_was_selected: Event[None],
                          to_main_menu_was_pressed: Event[None]) -> Layer:
        synchroniser = TextSizeSynchroniser()
        cyber_dilf = self._make_author_card("_cyberDilf",
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
                                            ])
        divan = self._make_author_card("Divan0_0",
                                       self._sprites_loader.load_divan(),
                                       self._language.get_divan_roles(),
                                       synchroniser,
                                       [
                                           self._make_link(self._sprites_loader.load_github(),
                                                           "https://github.com/Ktoto888550303"),
                                       ])
        layout = HorizontalLayoutUi(self._get_authors_cards_rectangle(), margin_ratio=.21)
        layout.append(cyber_dilf)
        layout.append(divan)
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

    def _make_author_card(self,
                          name: str,
                          sprite: proto.Sprite,
                          roles: list[str],
                          roles_synchroniser: TextSizeSynchroniser,
                          links: list[ButtonUi]) -> VerticalLayoutUi:
        max_links = 4
        max_roles = 6
        assert len(links) <= max_links
        assert len(roles) <= max_links

        card = VerticalLayoutUi(Rectangle(Vector2.zero(), Vector2(200, 600)))
        roles_ui = VerticalLayoutUi(Rectangle.zero())
        card.append(roles_ui)
        while len(roles) < max_roles:
            roles.insert(0, ' ')
        for role in roles:
            data = TextDataBuilder.like(TextData.debug(role)).button_font().build()
            line = TextUi.make(self._drawer, Rectangle.zero(), data, is_center=True)
            roles_ui.append(line)
            roles_synchroniser.append(line)

        card.append(ImageUi.make(self._drawer, Rectangle(Vector2.zero(), Vector2.ones()), sprite))

        links_ui = HorizontalLayoutUi(Rectangle.zero())
        links_halfer = VerticalLayoutUi(Rectangle.zero(), margin_ratio=.2)
        card.append(links_halfer)
        links_halfer.append(TextUi.make(self._drawer, Rectangle.zero(), TextData.debug(name), is_center=True))
        links_halfer.append(links_ui)
        links_halfer.append(BoxUi(Rectangle.zero()))
        links_ui.extend(links)
        while len(links_ui) < max_links:
            links_ui.append(BoxUi(Rectangle.zero()))

        return card

    def _make_map_selection(self,
                            turn_tabs_off: Callable[[], None],
                            map_names: list[str],
                            on_map_was_selected: Callable[[str], None],
                            tab_was_selected: Event[None],
                            to_main_menu_was_pressed: Event[None]) -> Layer:
        layers = [
            self._make_map_selection_buttons(map_names, on_map_was_selected),
            self._make_back_button(to_main_menu_was_pressed.invoke, turn_tabs_off),
        ]
        layer = Layer.as_multiple(layers)
        layer.set_activity(False)
        tab_was_selected.subscribe(lambda: layer.set_activity(True))
        return layer

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
        layout = VerticalLayoutUi(self._get_changers_rectangle(), margin_ratio=margin_ratio)
        rectangle = Rectangle(Vector2.zero(),
                              Vector2(count * layout.rectangle.shape.x / layout.rectangle.shape.y,
                                      1 - margin_ratio) * 100)

        changers = self._get_changers()

        layout.append(audio := TextUi.make(self._drawer, Rectangle.zero(),
                                           TextData.debug(self._language.get_audio_message()), is_center=True))

        synchroniser = TextSizeSynchroniser()
        self._add_changer(synchroniser, layout, self._language.get_music_volume_message(), MUSIC, changers,
                          value_changers,
                          rectangle)
        self._add_changer(synchroniser, layout, self._language.get_voice_volume_message(), VOICE, changers,
                          value_changers,
                          rectangle)
        self._add_changer(synchroniser, layout, self._language.get_effects_volume_message(), EFFECTS, changers,
                          value_changers, rectangle)
        layout.append(BoxUi(Rectangle.zero()))

        layout.append(other := TextUi.make(self._drawer, Rectangle.zero(),
                                           TextData.debug(self._language.get_other_message()), is_center=True))
        self._add_changer(synchroniser, layout, self._language.get_selected_language_message(), LANGUAGE, changers,
                          value_changers, rectangle)

        titles_synchroniser = TextSizeSynchroniser()
        titles_synchroniser.extend(other, audio)

        titles_synchroniser.synchronise()
        synchroniser.synchronise()

        for _ in range(count - len(layout)):
            layout.append(BoxUi(Rectangle.zero()))

        return layout.layer

    def _add_changer[T](self,
                        synchroniser: TextSizeSynchroniser,
                        layout: LayoutUi,
                        text: str,
                        key: str,
                        changers: dict[str, ValueChanger[T]],
                        value_changers: dict[str, TwoButtonsValueChanger[T]],
                        rectangle: Rectangle) -> None:
        to_add, value_changer = self._make_changer(text, changers[key], rectangle)
        layout.append(to_add)
        synchroniser.append(value_changer.text)
        value_changers[key] = value_changer

    def _make_changer[T](self,
                         text: str,
                         changer: ValueChanger[T],
                         rectangle: Rectangle) -> tuple[LayoutUi, TwoButtonsValueChanger[T]]:
        text = f"{text}:"
        margin_ratio = .13
        horizontal = HorizontalLayoutUi(rectangle, margin_ratio=margin_ratio)
        horizontal.append(TextUi.make(self._drawer, Rectangle.zero(), TextData.debug(text), is_center=True))
        horizontal.append(value_changer := TwoButtonsValueChanger.make_horizontal(
            Rectangle(Vector2.zero(), rectangle.shape.with_x(rectangle.shape.x * (1 - margin_ratio) / 2)), changer,
            self._sprites_loader, self._drawer))
        return horizontal, value_changer

    def _get_changers_rectangle(self) -> Rectangle:
        width = self._screen_shape.x / 2
        height = self._screen_shape.y / 1.3
        bottom_margin = (self._screen_shape.y - height) / 2

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
        int_changer_range = 0, _AUDIO_SETTER_STEPS, _AUDIO_SETTER_STEP
        return {
            MUSIC: IntChanger(round(_AUDIO_SETTER_STEPS * settings.music_volume), *int_changer_range),
            VOICE: IntChanger(round(_AUDIO_SETTER_STEPS * settings.voice_volume), *int_changer_range),
            EFFECTS: IntChanger(round(_AUDIO_SETTER_STEPS * settings.effects_volume), *int_changer_range),
            LANGUAGE: ListChanger(languages)
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
                    exit_was_pressed: Callable[[], None]) -> Layer:
        layers = [
            self._make_title(),
            self._make_buttons(play_was_pressed, tutorial_was_pressed, settings_was_pressed, authors_was_pressed,
                               exit_was_pressed, turn_tabs_off),
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
                      exit_was_pressed: Callable[[], None],
                      turn_tabs_off: Callable[[], None]) -> Layer:
        layout = VerticalLayoutUi(self._get_buttons_rectangle(), margin_ratio=0.1)
        layout.append(self._make_menu_button(self._language.get_play_message(), play_was_pressed.invoke, turn_tabs_off))

        tutorial_settings = HorizontalLayoutUi(Rectangle.zero())
        layout.append(tutorial_settings)
        tutorial_settings.append(tutorial := self._make_menu_button(self._language.get_tutorial_message(),
                                                                    tutorial_was_pressed.invoke, turn_tabs_off))
        tutorial_settings.append(settings := self._make_menu_button(self._language.get_settings_message(),
                                                                    settings_was_pressed.invoke, turn_tabs_off))

        authors_close = HorizontalLayoutUi(Rectangle.zero())
        layout.append(authors_close)
        authors_close.append(authors := self._make_menu_button(self._language.get_authors_message(),
                                                               authors_was_pressed.invoke, turn_tabs_off))
        authors_close.append(close := self._make_null_button(self._language.get_exit_message(), exit_was_pressed))

        synchroniser = TextSizeSynchroniser()
        synchroniser.extend(tutorial.text, settings.text, close.text, authors.text)
        synchroniser.synchronise()

        return layout.layer

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
    return f"{build_info[version_prefix]} {build_info[version]} from {build_info[date]}"
