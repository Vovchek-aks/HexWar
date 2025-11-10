from appearance.UI.button import ButtonUi
from appearance.UI.text import TextUi, TextData
from appearance.graphics.sprites import SpritesLoader
from appearance.UI.drawer import UiDrawer
from appearance.layer import Layer
from mathematics.vector import Vector2, Vector2Int


def make_ui_layer(drawer: UiDrawer, screen_shape: Vector2Int) -> Layer:
    text = TextUi.make(drawer,
                       Vector2(80, 40),
                       TextData.debug("Your turn"))

    button_background = (SpritesLoader
                         .from_meta()
                         .load_no_sprite()
                         .with_pivot(Vector2Int.zero())
                         .reshape(Vector2Int(120, 40)))
    button_position = screen_shape - button_background.shape.scale_rounded(.5) - Vector2Int(30, 30)
    button = ButtonUi.make(drawer,
                           button_position.as_vector2,
                           button_background,
                           TextData.debug("End turn"))

    def on_end_turn_was_clicked() -> None:
        text.set_text("Yellow player's turn")
        button.layer.set_activity(False)

    button.layer.was_clicked.subscribe(lambda click: on_end_turn_was_clicked())

    layers = [
        text,
        button
    ]
    return Layer.as_multiple(layers)
