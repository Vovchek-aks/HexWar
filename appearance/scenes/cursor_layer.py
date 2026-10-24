import appearance.protocols as proto
from appearance.graphics.sprites import SpritesLoader
from appearance.layer import LayerBuilder


def get_cursor_layer() -> proto.Layer:
    cursor = SpritesLoader.from_meta().load_cursor().resize(.12)
    return (LayerBuilder()
            .not_catching()
            .set_draw_function(lambda coord: cursor.blit_at(coord))
            .build())
