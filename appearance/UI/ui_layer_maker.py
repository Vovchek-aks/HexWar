from appearance.UI.button import ButtonUi
from appearance.UI.text import TextUi, TextData
from appearance.graphics.sprites import SpritesLoader
from appearance.UI.drawer import UiDrawer
from appearance.layer import Layer
from appearance.graphics.colors import PLAYER_RED, PLAYER_YELLOW
from mathematics.vector import Vector2, Vector2Int


def make_ui_layer(drawer: UiDrawer, screen_shape: Vector2Int) -> Layer:
    text = TextUi.make(drawer,
                       Vector2(80, 40),
                       TextData.debug("Your turn"))
    text.set_color(PLAYER_RED)

    button_background = (SpritesLoader
                         .from_meta()
                         .load_small_button())
    button_text = TextData.debug("End turn")
    button_position = screen_shape.as_vector2 - button_text.shape / 2 - Vector2(60, 30)
    button = ButtonUi.make(drawer,
                           button_position,
                           button_background,
                           button_text)

    def on_end_turn_was_clicked() -> None:
        text.set_text("Yellow player's turn")
        text.set_color(PLAYER_YELLOW)
        button.layer.set_activity(False)

    button.layer.was_clicked.subscribe(lambda click: on_end_turn_was_clicked())

    layers = [
        text,
        button
    ]
    return Layer.as_multiple(layers)
