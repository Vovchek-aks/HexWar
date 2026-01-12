from typing import Callable

from attrs import frozen, Factory

from appearance.UI.box import BoxUi
from appearance.UI.button import ButtonUi, get_image_rectangle
from appearance.UI.image import ImageUi
from appearance.UI.layouts import VerticalLayoutUi, HorizontalLayoutUi
from appearance.UI.layouts.layout import LayoutUi
from appearance.UI.stretcher import StretcherUi
from appearance.UI.text import TextUi, TextData
from appearance.UI.text.text_data_pg import TextDataBuilder
from appearance.graphics.sprites import SpritesLoader
from appearance.UI.drawer import UiDrawer
from appearance.input.clicks_catcher.click import Click, MouseButtons
from appearance.input.mouse_movement_observer import MouseMovementObserver
from appearance.input.moves_inputer.actions_reader import InputActionsReader
from appearance.input.moves_inputer.input_actions import ButtonPressAction, CreationButtonPressAction, \
    ConversionButtonPressAction, CaptureButtonPressAction, AttackButtonPressAction
from appearance.language import Language, ARTILLERY_ATTACK, TANK_ATTACK, MOTORIZATION_TO_INFANTRY, INFANTRY_CAPTURE, \
    INFANTRY_TO_MOTORIZATION
from appearance.layer import Layer
from appearance.protocols import CellSelector, InputAction
from core.player.inputers.event_player_inputer import EventPlayerInputerBuilder
from core.protocols import GameSession, Player, MovesMaker, ValidMove, ResourcesStockpile, Creatable
from core.resources import Dollars
from mathematics.rectangle import Rectangle, RectangleBuilder
from mathematics.vector import Vector2, Vector2Int
import core.figures.figures as fig
from observer import Event
from statuses import MISSING, Status


@frozen
class GameUiLayerMaker:
    _drawer: UiDrawer
    _screen_shape: Vector2Int
    _session: GameSession
    _cell_selector: CellSelector
    _mouse_movement_observer: MouseMovementObserver
    _button_press_action_happened: Event[ButtonPressAction, None]
    _moves_maker: MovesMaker
    _actions_reader: InputActionsReader

    _language: Language = Factory(Language.from_meta)
    _sprites_loader: SpritesLoader = Factory(SpritesLoader.from_meta)

    def make(self, user_inputer_builder: EventPlayerInputerBuilder) -> Layer:
        players_turn = TextUi.make(self._drawer,
                                   (RectangleBuilder(self._screen_shape)
                                    .from_left_up()
                                    .move(Vector2(10, 10))
                                    .set_shape(Vector2(110, 30))
                                    .adjust_for_shape()
                                    .build()),
                                   TextData.debug('...'))

        dollars = TextUi.make(self._drawer,
                              (RectangleBuilder(self._screen_shape)
                               .from_left_up()
                               .move(Vector2(12, 60))
                               .set_shape(Vector2(100, 20))
                               .adjust_for_shape()
                               .build()),
                              TextData.debug('...'))

        def on_resources_had_changed(resources: ResourcesStockpile) -> None:
            dollars.set_text(self._language.get_message_from_resource(resources.get(Dollars)))

        self._session.master.current_player.resources.has_changed.subscribe(on_resources_had_changed)

        end_turn_button = self._make_end_turn_button()
        user_inputer_builder.set_need_to_end_turn(end_turn_button.was_clicked)

        def on_turn_passed(player: Player) -> None:
            name = player.data.name
            players_turn.set_text(self._language.get_players_turn_message(name))

        self._session.master.turn_has_passed.subscribe(on_turn_passed)

        layers = [
            players_turn,
            self._make_current_turn_ui(dollars, end_turn_button)
        ]

        on_turn_passed(self._session.master.current_player)
        on_resources_had_changed(self._session.master.current_player.resources)

        return Layer.as_multiple(layers)

    def _make_current_turn_ui(self, dollars: TextUi, end_turn_button: ButtonUi) -> Layer:
        layer = Layer.as_multiple([
            self._make_figures_creation_menu(),
            self._make_infantry_menu(),
            self._make_motorization_menu(),
            self._make_tank_menu(),
            self._make_artillery_menu(),
            self._make_town_menu(),
            self._make_bunker_menu(),
            dollars,
            end_turn_button,
        ])
        self._session.master.turn_has_passed.subscribe(lambda player: layer.set_activity(player.need_ui))
        return layer

    def _make_end_turn_button(self) -> ButtonUi:
        button_background = self._sprites_loader.load_button_3_to_2()
        button_text = TextData.debug(self._language.get_end_turn_message())
        button = ButtonUi.make(self._drawer,
                               get_image_rectangle(RectangleBuilder(self._screen_shape)
                                                   .from_right_bottom()
                                                   .move(Vector2(30, 30))
                                                   .set_shape(Vector2(130, 20))
                                                   .adjust_for_shape()
                                                   .build()),
                               button_background,
                               button_text)

        return button

    def _make_figures_creation_menu(self) -> Layer:
        layout = HorizontalLayoutUi(RectangleBuilder(self._screen_shape)
                                    .from_left_bottom()
                                    .move(Vector2(20, 20))
                                    .set_shape(Vector2(410, 210))
                                    .adjust_for_shape()
                                    .build())

        hint_box = BoxUi(Rectangle(Vector2.zero(), Vector2(200, 200)))
        buttons = self._make_figures_creation_buttons(hint_box)
        layout.append(buttons)
        layout.append(hint_box)

        self._bind_layer_to_cell_with_figure_selection(layout.layer, fig.Empty)

        return layout.layer

    def _make_figures_creation_buttons(self, hint_box: BoxUi) -> LayoutUi:
        layout = VerticalLayoutUi(RectangleBuilder(self._screen_shape)
                                  .from_left_bottom()
                                  .move(Vector2(20, 20))
                                  .set_shape(Vector2(200, 210))
                                  .adjust_for_shape()
                                  .build(),
                                  margin_ratio=.2)
        layout.append(self._make_figure_creation_button(fig.Town, hint_box))
        layout.append(self._make_figure_creation_button(fig.Bunker, hint_box))

        horizontal_layout = HorizontalLayoutUi(Rectangle.zero(), margin_ratio=.07)
        layout.append(horizontal_layout)
        horizontal_layout.append(self._make_figure_creation_button(fig.Tank, hint_box))
        horizontal_layout.append(self._make_figure_creation_button(fig.Infantry, hint_box))

        layout.append(self._make_figure_creation_button(fig.Artillery, hint_box))

        return layout

    def _make_figure_creation_button(self, figure: type[fig.Figure], hint_box: BoxUi) -> ButtonUi:
        background = self._sprites_loader.load_button_3_to_2()

        text = TextData.debug(self._language.get_figure_name(figure))
        position = Vector2.zero()
        button = ButtonUi.make(self._drawer,
                               get_image_rectangle(Rectangle.with_center_at(position, text.shape)),
                               background,
                               text)

        button.was_clicked.subscribe(lambda:
                                     self._button_press_action_happened
                                     .invoke(CreationButtonPressAction(self._cell_selector.get_coord(), figure)))

        hint_box.append(self._make_figure_creation_button_hint(figure, button))

        return button

    def _make_figure_creation_button_hint(self, figure: type[fig.Figure], button: ButtonUi) -> StretcherUi:
        title = self._language.get_figure_name(figure)
        content = [
            *self._language.get_creation_hint(figure),
            *self._language.get_cost(figure.FLAGS.get(Creatable).cost)
        ]
        hint = self._make_button_hint(title, content, button)

        return hint

    def _make_infantry_menu(self) -> Layer:
        to_motorize = self._make_null_button(Language.from_meta().get_to_motorize_message())
        to_motorize.was_clicked.subscribe(lambda: self._button_press_action_happened
                                          .invoke(ConversionButtonPressAction(self._cell_selector.get_coord(),
                                                                              fig.Motorization)))

        capture = self._make_activatable_button(self._language.get_capture_message(),
                                                lambda: CaptureButtonPressAction(self._cell_selector.get_coord()))

        return self._make_figure_menu(fig.Infantry, [to_motorize, capture],
                                      [INFANTRY_TO_MOTORIZATION, INFANTRY_CAPTURE])

    def _make_motorization_menu(self) -> Layer:
        to_infantry = self._make_null_button(Language.from_meta().get_to_infantry_message())
        to_infantry.was_clicked.subscribe(lambda: self._button_press_action_happened
                                          .invoke(ConversionButtonPressAction(self._cell_selector.get_coord(),
                                                                              fig.Infantry)))

        return self._make_figure_menu(fig.Motorization, [to_infantry], [MOTORIZATION_TO_INFANTRY])

    def _make_town_menu(self) -> Layer:
        return self._make_figure_menu(fig.Town, [], [])

    def _make_bunker_menu(self) -> Layer:
        return self._make_figure_menu(fig.Bunker, [], [])

    def _make_tank_menu(self) -> Layer:
        attack = self._make_activatable_button(self._language.get_attack_message(),
                                               lambda: AttackButtonPressAction(self._cell_selector.get_coord()))

        return self._make_figure_menu(fig.Tank, [attack], [TANK_ATTACK])

    def _make_artillery_menu(self) -> Layer:
        attack = self._make_activatable_button(self._language.get_attack_message(),
                                               lambda: AttackButtonPressAction(self._cell_selector.get_coord()))

        return self._make_figure_menu(fig.Artillery, [attack], [ARTILLERY_ATTACK])

    def _make_figure_menu(self,
                          figure: type[fig.Figure],
                          buttons: list[ButtonUi],
                          button_tags: list[str]) -> Layer:
        assert len(buttons) == len(button_tags)

        menu = self._make_figure_menu_without_hints(figure, buttons)
        menu_width, menu_height = menu.rectangle.shape
        hint_box = BoxUi(Rectangle(menu.rectangle.position + Vector2.right() * (10 + menu_width),
                                   Vector2(menu_height, menu_height)))

        for button, tag in zip(buttons, button_tags):
            hint_box.append(self._make_figure_menu_button_hint(button, tag))

        layer = Layer.as_multiple([
            menu,
            hint_box,
        ])

        self._bind_layer_to_cell_with_figure_selection(layer, figure)
        return layer

    def _make_figure_menu_without_hints(self, figure_type: type[fig.Figure], buttons: list[ButtonUi]) -> StretcherUi:
        background_margin = Vector2(20, 20)
        background = ImageUi.make(self._drawer,
                                  RectangleBuilder(self._screen_shape)
                                  .from_left_bottom()
                                  .move(background_margin)
                                  .set_shape(Vector2(3, 2) * 100)
                                  .adjust_for_shape()
                                  .build(),
                                  self._sprites_loader.load_background_3_to_2())

        title_margin = Vector2(15, background.rectangle.shape.y - 60)
        title = TextUi.make(self._drawer,
                            RectangleBuilder(self._screen_shape)
                            .move(background.rectangle.position + title_margin)
                            .set_shape(Vector2(background.rectangle.shape.x - title_margin.x * 2,
                                               background.rectangle.shape.y / 4))
                            .build(),
                            TextDataBuilder()
                            .set_text(self._language.get_figure_name(figure_type))
                            .debug_font()
                            .black_colored()
                            .build())
        title_bottom = title.rectangle.position.y
        combat_ability_position = Vector2(title.rectangle.position.x, title_bottom - 40)
        combat_ability = TextUi.make(self._drawer,
                                     RectangleBuilder(self._screen_shape)
                                     .move(combat_ability_position)
                                     .set_shape(Vector2(background.rectangle.shape.x / 2 - title_margin.x,
                                                        background.rectangle.shape.y / 4))
                                     .build(),
                                     TextDataBuilder()
                                     .set_text(self._language.get_combat_ability_message(0))
                                     .debug_font()
                                     .black_colored()
                                     .build())

        def update_combat_ability(coord: Vector2Int | Status) -> None:
            if coord is MISSING:
                return

            figure = self._session.board[coord].figure
            if not isinstance(figure, figure_type):
                return

            if (budget := figure.MOVES_BUDGET) == 0:
                combat_ability.set_text('')
                return

            spent = self._session.figures_budget.of(figure)
            combat_ability_ratio = (budget - spent) / budget
            combat_ability.set_text(self._language.get_combat_ability_message(combat_ability_ratio))

        self._cell_selector.cell_was_selected.subscribe(update_combat_ability)
        self._moves_maker.board_move_was_made.subscribe(
            lambda _: update_combat_ability(self._cell_selector.get_coord()))
        self._session.master.turn_has_passed.subscribe(
            lambda _: update_combat_ability(self._cell_selector.get_coord()))

        layout_margin = Vector2(15, 15)
        buttons_width = background.rectangle.shape.x - layout_margin.x * 2
        layout = HorizontalLayoutUi(RectangleBuilder(self._screen_shape)
                                    .from_left_bottom()
                                    .move(background_margin + layout_margin)
                                    .set_shape(Vector2(buttons_width, background.rectangle.shape.y / 4))
                                    .adjust_for_shape()
                                    .build())
        layout.extend(buttons)

        menu = StretcherUi(background.rectangle)
        menu.extend([
            title,
            combat_ability,
            layout,
            background,
        ])

        return menu

    def _make_figure_menu_button_hint(self, button: ButtonUi, tag: str) -> StretcherUi:
        return self._make_button_hint(button.text.text, self._language.get_figure_menu_hint_for(tag), button)

    def _make_button_hint(self, title: str, content: list[str], button: ButtonUi) -> StretcherUi:
        hint = self._make_null_hint(title, content)

        hint.layer.set_activity(False)
        self._mouse_movement_observer.mouse_was_moved.subscribe(
            lambda position: hint.layer.set_activity(button.layer.can_catch(Click(position, MouseButtons()))))

        return hint

    def _make_null_hint(self, title: str, content: list[str]) -> StretcherUi:
        MIN_LINES_COUNT = 8
        MAX_LINE_LENGTH = 25

        background = ImageUi.make(self._drawer,
                                  Rectangle(Vector2.zero(), Vector2(200, 300)),
                                  self._sprites_loader.load_background_2_to_3())

        title_ui = TextUi.make(self._drawer,
                               RectangleBuilder(Vector2Int.from_vector2(background.rectangle.shape))
                               .from_left_up()
                               .set_shape(Vector2(180, 30))
                               .move(Vector2(10, 20))
                               .adjust_for_shape()
                               .build(),
                               TextDataBuilder()
                               .set_text(title)
                               .debug_font()
                               .black_colored()
                               .build())

        white_spaces = [" "] * (MIN_LINES_COUNT - len(content))
        content = white_spaces[:len(white_spaces) // 2] + content + white_spaces[len(white_spaces) // 2:]
        content_ui = VerticalLayoutUi(RectangleBuilder(Vector2Int.from_vector2(background.rectangle.shape))
                                      .from_left_up()
                                      .set_shape(Vector2(180, 235))
                                      .move(Vector2(10, 55))
                                      .adjust_for_shape()
                                      .build())
        for line in content:
            line_ui = TextUi.make(self._drawer,
                                  Rectangle.zero(),
                                  TextDataBuilder()
                                  .set_text(line.ljust(MAX_LINE_LENGTH, " "))
                                  .debug_font()
                                  .black_colored()
                                  .build())
            content_ui.append(line_ui)

        stretcher = StretcherUi(background.rectangle)
        stretcher.append(title_ui)
        stretcher.append(content_ui)
        stretcher.append(background)
        return stretcher

    def _bind_layer_to_cell_with_figure_selection(self, layer: Layer, figure: type[fig.Figure]) -> None:
        layer.set_activity(False)

        self._cell_selector.cell_was_selected.subscribe(
            lambda coord: layer.set_activity(self._is_ui_needed(coord, figure)))
        self._cell_selector.cell_was_unselected.subscribe(lambda: layer.set_activity(False))

        def on_board_move_was_made(_: ValidMove) -> None:
            if (coord := self._cell_selector.get_coord()) is MISSING:
                layer.set_activity(False)
                return

            return layer.set_activity(self._is_ui_needed(coord, figure))

        self._moves_maker.board_move_was_made.subscribe(on_board_move_was_made)

    def _make_activatable_button(self,
                                 text: str,
                                 action_maker: Callable[[], ButtonPressAction]) -> ButtonUi:
        button = self._make_null_button(text)
        image = button.image
        not_active = image.sprite
        active = self._sprites_loader.load_button_3_to_2_active()

        def set_active() -> None:
            image.set_sprite(active)
            self._button_press_action_happened.invoke(action_maker())

        def set_not_active(action: InputAction, is_last: bool) -> None:
            if not isinstance(action, type(action_maker())):
                return
            if not is_last:
                return

            image.set_sprite(not_active)

        button.was_clicked.subscribe(set_active)
        self._actions_reader.action_was_removed.subscribe(set_not_active)

        return button

    def _make_null_button(self, text: str) -> ButtonUi:
        background = self._sprites_loader.load_button_3_to_2()
        text_data = TextData.debug(text)
        button = ButtonUi.make(self._drawer,
                               Rectangle(Vector2.zero(), text_data.shape),
                               background,
                               text_data)
        return button

    def _get_position_from_left_bottom(self, delta: Vector2) -> Vector2:
        position = Vector2(0, self._screen_shape.y)
        position += Vector2(delta.x, -delta.y)
        return position

    def _is_ui_needed(self, cell_coord: Vector2Int, figure: type[fig.Figure]) -> bool:
        cell = self._session.board[cell_coord]
        player = self._session.master.current_player
        return (self._is_current_player_need_ui() and
                cell.owner is player and
                isinstance(cell.figure, figure))

    def _is_current_player_need_ui(self) -> bool:
        return self._session.master.current_player.need_ui
