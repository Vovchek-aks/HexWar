from appearance.graphics.sprites import SpritesLoader
from color import Color

from appearance.UI.drawer import UiDrawer
from appearance.UI.text import TextUi, TextData
from appearance.UI.image import ImageUi
from appearance.graphics.layer_drawers.layers_drawer import LayersDrawer
from appearance.input.clicks_catcher.layers.layers_container_layer import LayersContainerLayer
from appearance.layer import Layer
from mathematics.vector import Vector2, Vector2Int


def make_ui_layer(drawer: UiDrawer) -> Layer:
    test_sprite = SpritesLoader.from_meta().load_no_sprite().with_pivot(Vector2Int.zero()).resize(.3)
    layers = [
        TextUi(drawer, TextData.with_debug_font("test", 40, Color(255, 255, 255), Vector2(20, 20))),
        ImageUi(drawer, test_sprite, Vector2(20, 80))
    ]
    return Layer(LayersDrawer(layers[::-1]),
                 LayersContainerLayer.make(layers))
