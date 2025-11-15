from appearance.UI.button import ButtonUi
from appearance.UI.text import TextUi, TextData
from appearance.graphics.sprites import SpritesLoader
from appearance.UI.drawer import UiDrawer
from appearance.layer import Layer
from core.player.inputers.event_player_inputer import EventPlayerInputerBuilder
from core.protocols import GameSession, Player
from mathematics.vector import Vector2, Vector2Int


def make_ui_layer(drawer: UiDrawer,
                  screen_shape: Vector2Int,
                  user_inputer_builder: EventPlayerInputerBuilder,
                  session: GameSession) -> Layer:
    player_name = session.master.current_player.data.name
    text = TextUi.make(drawer,
                       Vector2(80, 40),
                       TextData.debug(f"{player_name}'s turn"))

    button_background = (SpritesLoader
                         .from_meta()
                         .load_button_2_to_3())
    button_text = TextData.debug("End turn")
    button_position = screen_shape.as_vector2 - button_text.shape / 2 - Vector2(30, 30)
    button = ButtonUi.make(drawer,
                           button_position,
                           button_background,
                           button_text)

    user_inputer_builder.set_need_to_end_turn(button.was_clicked)

    def on_turn_passed(player: Player) -> None:
        name = player.data.name
        text.set_text(f"{name}'s turn")
        button.layer.set_activity(_is_player_need_ui(player))

    session.master.turn_has_passed.subscribe(on_turn_passed)

    layers = [
        text,
        button
    ]
    return Layer.as_multiple(layers)


def _is_player_need_ui(player: Player) -> bool:
    return player.data.name == "Red"
