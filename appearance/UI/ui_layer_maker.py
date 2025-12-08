from attrs import frozen, Factory

from appearance.UI.button import ButtonUi, get_image_rectangle
from appearance.UI.image import ImageUi
from appearance.UI.layouts import VerticalLayout, HorizontalLayout
from appearance.UI.number_shortener import NumberShortener
from appearance.UI.text import TextUi, TextData
from appearance.UI.text.text_data_pg import TextDataBuilder
from appearance.graphics.sprites import SpritesLoader
from appearance.UI.drawer import UiDrawer
from appearance.input.moves_inputer.input_actions import ButtonPressAction, CreationButtonPressAction, \
    ConversionButtonPressAction, CaptureButtonPressAction, AttackButtonPressAction
from appearance.language import Language
from appearance.layer import Layer
from appearance.protocols import CellSelector
from core.player.inputers.event_player_inputer import EventPlayerInputerBuilder
from core.protocols import GameSession, Player, MovesMaker, ValidMove, ResourcesStockpile
from core.resources import Dollars
from mathematics.rectangle import Rectangle, RectangleBuilder
from mathematics.vector import Vector2, Vector2Int
import core.figures.figures as fig
from observer import Event
from statuses import MISSING, Status


@frozen
class UiLayerMaker:
    _drawer: UiDrawer
    _screen_shape: Vector2Int
    _session: GameSession
    _cell_selector: CellSelector
    _button_press_action_happened: Event[ButtonPressAction, None]
    _moves_maker: MovesMaker
    _language: Language = Factory(Language.from_meta)
    _sprites_loader: SpritesLoader = Factory(SpritesLoader.from_meta)

    def make(self, user_inputer_builder: EventPlayerInputerBuilder) -> Layer:
        players_turn = TextUi.make(self._drawer,
                                   Rectangle(Vector2(10, 10), Vector2(110, 30)),
                                   TextData.debug('...'))

        dollars = TextUi.make(self._drawer,
                              Rectangle(Vector2(12, 60), Vector2(100, 20)),
                              TextData.debug('...'))

        def on_resources_had_changed(resources: ResourcesStockpile) -> None:
            amount = NumberShortener.shorten(resources.get(Dollars).amount)
            dollars.set_text(f"{self._language.get_resource_name(Dollars)}: {amount}")

        self._session.master.current_player.resources.has_changed.subscribe(on_resources_had_changed)

        end_turn_button = self._make_end_turn_button()
        user_inputer_builder.set_need_to_end_turn(end_turn_button.was_clicked)

        def on_turn_passed(player: Player) -> None:
            name = player.data.name
            players_turn.set_text(self._language.get_players_turn_message(name))

        self._session.master.turn_has_passed.subscribe(on_turn_passed)

        layers = [
            players_turn,
            dollars,
            self._make_current_turn_ui(end_turn_button)
        ]

        on_turn_passed(self._session.master.current_player)
        on_resources_had_changed(self._session.master.current_player.resources)

        return Layer.as_multiple(layers)

    def _make_current_turn_ui(self, end_turn_button: ButtonUi) -> Layer:
        layer = Layer.as_multiple([
            self._make_figures_creation_buttons(),
            self._make_infantry_menu(),
            self._make_motorization_menu(),
            self._make_tank_menu(),
            self._make_artillery_menu(),
            self._make_town_menu(),
            self._make_bunker_menu(),
            end_turn_button,
        ])
        self._session.master.turn_has_passed.subscribe(lambda player:
                                                       layer.set_activity(self._is_player_need_ui(player)))
        return layer

    def _make_end_turn_button(self) -> ButtonUi:
        button_background = self._sprites_loader.load_button_2_to_3()
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

    def _make_figures_creation_buttons(self) -> Layer:
        layout = VerticalLayout(RectangleBuilder(self._screen_shape)
                                .from_left_bottom()
                                .move(Vector2(20, 20))
                                .set_shape(Vector2(200, 210))
                                .adjust_for_shape()
                                .build(),
                                margin_ratio=.2)
        layout.append(self._make_figure_creation_button(fig.Town))
        layout.append(self._make_figure_creation_button(fig.Bunker))

        horizontal_layout = HorizontalLayout(Rectangle.zero(), margin_ratio=.07)
        layout.append(horizontal_layout)
        horizontal_layout.append(self._make_figure_creation_button(fig.Tank))
        horizontal_layout.append(self._make_figure_creation_button(fig.Infantry))

        layout.append(self._make_figure_creation_button(fig.Artillery))

        layer = layout.layer
        self._bind_layer_to_cell_with_figure_selection(layer, fig.Empty)
        return layer

    def _make_figure_creation_button(self, figure: type[fig.Figure]) -> ButtonUi:
        background = self._sprites_loader.load_button_2_to_3()

        text = TextData.debug(self._language.get_figure_name(figure))
        position = Vector2.zero()
        button = ButtonUi.make(self._drawer,
                               get_image_rectangle(Rectangle.with_center_at(position, text.shape)),
                               background,
                               text)

        button.was_clicked.subscribe(lambda:
                                     self._button_press_action_happened
                                     .invoke(CreationButtonPressAction(self._cell_selector.get_coord(), figure)))
        return button

    def _make_infantry_menu(self) -> Layer:
        to_motorize = self._make_null_button(Language.from_meta().get_to_motorize_message())
        to_motorize.was_clicked.subscribe(lambda: self._button_press_action_happened
                                          .invoke(ConversionButtonPressAction(self._cell_selector.get_coord(),
                                                                              fig.Motorization)))

        capture = self._make_null_button(Language.from_meta().get_capture_message())
        capture.was_clicked.subscribe(lambda: self._button_press_action_happened
                                      .invoke(CaptureButtonPressAction(self._cell_selector.get_coord())))

        return self._make_figure_menu(fig.Infantry, [to_motorize, capture])

    def _make_motorization_menu(self) -> Layer:
        to_infantry = self._make_null_button(Language.from_meta().get_to_infantry_message())
        to_infantry.was_clicked.subscribe(lambda: self._button_press_action_happened
                                          .invoke(ConversionButtonPressAction(self._cell_selector.get_coord(),
                                                                              fig.Infantry)))

        return self._make_figure_menu(fig.Motorization, [to_infantry])

    def _make_town_menu(self) -> Layer:
        return self._make_figure_menu(fig.Town, [])

    def _make_bunker_menu(self) -> Layer:
        return self._make_figure_menu(fig.Bunker, [])

    def _make_tank_menu(self) -> Layer:
        attack = self._make_null_button(Language.from_meta().get_attack_message())
        attack.was_clicked.subscribe(lambda: self._button_press_action_happened
                                     .invoke(AttackButtonPressAction(self._cell_selector.get_coord())))

        return self._make_figure_menu(fig.Tank, [attack])

    def _make_artillery_menu(self) -> Layer:
        attack = self._make_null_button(Language.from_meta().get_attack_message())
        attack.was_clicked.subscribe(lambda: self._button_press_action_happened
                                     .invoke(AttackButtonPressAction(self._cell_selector.get_coord())))

        return self._make_figure_menu(fig.Artillery, [attack])

    def _make_figure_menu(self, figure_type: type[fig.Figure], buttons: list[ButtonUi]) -> Layer:
        background_margin = Vector2(20, 20)
        background = ImageUi.make(self._drawer,
                                  RectangleBuilder(self._screen_shape)
                                  .from_left_bottom()
                                  .move(background_margin)
                                  .set_shape(Vector2(3, 2) * 100)
                                  .adjust_for_shape()
                                  .build(),
                                  self._sprites_loader.load_background_2_to_3())

        title_margin = Vector2(15, 10)
        title = TextUi.make(self._drawer,
                            RectangleBuilder(self._screen_shape)
                            .move(background.rectangle.left_up_corner + title_margin)
                            .set_shape(Vector2(background.rectangle.shape.x / 2 - title_margin.x,
                                               background.rectangle.shape.y / 4))
                            .build(),
                            TextDataBuilder()
                            .set_text(self._language.get_figure_name(figure_type))
                            .debug_font()
                            .black_colored()
                            .build())
        *_, title_bottom = title.rectangle.left_right_up_bottom
        combat_ability_position = Vector2(title.rectangle.left_up_corner.x, title_bottom)
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
        layout = HorizontalLayout(RectangleBuilder(self._screen_shape)
                                  .from_left_bottom()
                                  .move(background_margin + layout_margin)
                                  .set_shape(Vector2(buttons_width, background.rectangle.shape.y / 4))
                                  .adjust_for_shape()
                                  .build())
        layout.extend(buttons)

        layer = Layer.as_multiple([
            title,
            combat_ability,
            layout,
            background,
        ])

        self._bind_layer_to_cell_with_figure_selection(layer, figure_type)
        return layer

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

    def _make_null_button(self, text: str) -> ButtonUi:
        background = self._sprites_loader.load_button_2_to_3()
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
        player = self._session.master.current_player
        return self._is_player_need_ui(player)

    @staticmethod
    def _is_player_need_ui(player: Player) -> bool:
        return player.data.name == "Red"
