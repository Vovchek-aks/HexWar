from appearance.UI.button import ButtonUi
from appearance.UI.text import TextUi, TextData
from appearance.UI.image import ImageUi
from appearance.graphics.sprites import SpritesLoader
from color import Color
from appearance.UI.drawer import UiDrawer
from appearance.layer import Layer
from mathematics.vector import Vector2, Vector2Int


def make_ui_layer(drawer: UiDrawer) -> Layer:
    test_sprite = SpritesLoader.from_meta().load_no_sprite().with_pivot(Vector2Int.zero()).reshape(Vector2Int(120, 40))

    text = TextUi(drawer, TextData.with_debug_font("test", 40, Color(255, 255, 255)), Vector2(50, 50))

    image = ImageUi(drawer, test_sprite, Vector2(80, 100))

    button = ButtonUi.make(drawer,
                           test_sprite,
                           TextData.with_debug_font("click me", 40, Color(255, 255, 255)), Vector2(80, 170))
    button.layer.was_clicked.subscribe(lambda click: text.set_text("Батон"))

    layers = [
        text,
        image,
        button
    ]
    return Layer.as_multiple(layers)
