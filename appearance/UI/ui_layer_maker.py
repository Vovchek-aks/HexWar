from attrs import frozen

from appearance.UI.button import ButtonUi
from appearance.UI.number_shortener import NumberShortener
from appearance.UI.text import TextUi, TextData
from appearance.graphics.sprites import SpritesLoader
from appearance.UI.drawer import UiDrawer
from appearance.language import Language
from appearance.layer import Layer
from appearance.protocols import CellSelector
from core.player.inputers.event_player_inputer import EventPlayerInputerBuilder
from core.protocols import GameSession, Player, MovesMaker, ValidMove, ResourcesStockpile
from core.resources import Dollars
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2, Vector2Int
import core.figures as fig
from observer import Event
from statuses import MISSING


@frozen
class UiLayerMaker:
    _drawer: UiDrawer
    _screen_shape: Vector2Int
    _session: GameSession
    _cell_selector: CellSelector
    _button_press_action_happened: Event[type[fig.Figure], None]
    _moves_maker: MovesMaker

    def make(self, user_inputer_builder: EventPlayerInputerBuilder) -> Layer:
        language = Language.from_meta()

        players_turn = TextUi.make(self._drawer,
                                   Rectangle(Vector2(10, 10), Vector2(130, 50)),
                                   TextData.debug('...'))

        dollars = TextUi.make(self._drawer,
                              Rectangle(Vector2(10, 60), Vector2(100, 30)),
                              TextData.debug('...'))

        def on_resources_had_changed(resources: ResourcesStockpile) -> None:
            amount = NumberShortener.shorten(resources.get(Dollars).amount)
            dollars.set_text(f"{language.get_resource_name(Dollars)}: {amount}")

        self._session.resources.has_changed.subscribe(on_resources_had_changed)

        end_turn_button = self._make_end_turn_button()
        user_inputer_builder.set_need_to_end_turn(end_turn_button.was_clicked)

        def on_turn_passed(player: Player) -> None:
            name = player.data.name
            players_turn.set_text(language.get_players_turn_message(name))
            end_turn_button.layer.set_activity(self._is_player_need_ui(player))

        self._session.master.turn_has_passed.subscribe(on_turn_passed)

        layers = [
            players_turn,
            dollars,
            self._make_figures_creation_buttons(),
            end_turn_button,
        ]

        on_turn_passed(self._session.master.current_player)
        on_resources_had_changed(self._session.resources)

        return Layer.as_multiple(layers)

    def _make_end_turn_button(self) -> ButtonUi:
        button_background = (SpritesLoader
                             .from_meta()
                             .load_button_2_to_3())
        button_text = TextData.debug(Language.from_meta().get_end_turn_message())
        button_position = self._screen_shape.as_vector2 - button_text.shape / 2 - Vector2(30, 30)
        button = ButtonUi.make(self._drawer,
                               Rectangle.with_center_at(button_position, button_text.shape),
                               button_background,
                               button_text)
        return button

    def _make_figures_creation_buttons(self) -> Layer:
        buttons = [
            self._make_figure_creation_button(Vector2(100, 250), fig.Bunker),

            self._make_figure_creation_button(Vector2(100, 190), fig.Motorization),
            self._make_figure_creation_button(Vector2(100, 140), fig.Tank),
            self._make_figure_creation_button(Vector2(100, 90), fig.Artillery),
            self._make_figure_creation_button(Vector2(100, 40), fig.Infantry),
        ]
        layer = Layer.as_multiple(buttons)
        layer.set_activity(False)

        self._cell_selector.cell_was_selected.subscribe(
            lambda coord: layer.set_activity(self._is_figures_making_buttons_needed(coord)))
        self._cell_selector.cell_was_unselected.subscribe(lambda: layer.set_activity(False))

        def on_board_move_was_made(_: ValidMove) -> None:
            if (coord := self._cell_selector.get_coord()) is MISSING:
                layer.set_activity(False)
                return

            return layer.set_activity(self._is_figures_making_buttons_needed(coord))

        self._moves_maker.board_move_was_made.subscribe(on_board_move_was_made)

        return layer

    def _make_figure_creation_button(self, delta_position: Vector2, figure: type[fig.Figure]) -> ButtonUi:
        background = (SpritesLoader
                      .from_meta()
                      .load_button_2_to_3())

        text = TextData.debug(Language.from_meta().get_figure_name(figure))
        position = self._get_position_from_left_bottom(delta_position)
        button = ButtonUi.make(self._drawer,
                               Rectangle.with_center_at(position, text.shape),
                               background,
                               text)

        button.was_clicked.subscribe(lambda: self._button_press_action_happened.invoke(figure))
        return button

    def _get_position_from_left_bottom(self, delta: Vector2) -> Vector2:
        position = Vector2(0, self._screen_shape.y)
        position += Vector2(delta.x, -delta.y)
        return position

    def _is_figures_making_buttons_needed(self, cell_coord: Vector2Int) -> bool:
        cell = self._session.board[cell_coord]
        player = self._session.master.current_player
        is_needed_by_current_player = cell.owner is player and cell.is_empty
        return is_needed_by_current_player and self._is_current_player_need_ui()

    def _is_current_player_need_ui(self) -> bool:
        player = self._session.master.current_player
        return self._is_player_need_ui(player)

    @staticmethod
    def _is_player_need_ui(player: Player) -> bool:
        return player.data.name == "Red"
