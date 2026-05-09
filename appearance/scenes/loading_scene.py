from appearance.settings import Settings
from my_types import TracebackType
from typing import Iterator

from attrs import frozen

import appearance.protocols as proto
from appearance.UI.drawer import UiDrawer
from appearance.UI.text import TextUi, TextData
from appearance.graphics.sprites import SpritesLoader
from appearance.graphics.sprites.sprite import Sprite
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2, Vector2Int
from statuses import Status, MISSING

PROCESS = Iterator[str | proto.Scene]


@frozen
class LoadingScene(proto.Scene):
    @classmethod
    def make(cls, process: PROCESS) -> "LoadingScene":
        screen_shape = Settings.open().screen_shape
        text = TextUi.make(UiDrawer(),
                           Rectangle.with_center_at(screen_shape.as_vector2 * .5 - Vector2(0, screen_shape.y / 4),
                                                    Vector2(screen_shape.x / 2, 30)),
                           TextData.debug(" "),
                           is_center=True)
        self = cls(_loading_screen(screen_shape), text, process)
        return self

    _screen: Sprite
    _text: TextUi
    _process: PROCESS

    def next(self) -> proto.Scene | Status:
        if isinstance(result := next(self._process), proto.Scene):
            return result

        self._text.set_text(result)
        return MISSING

    def update(self) -> None:
        pass

    def draw(self) -> None:
        self._screen.blit_at(Vector2.zero())
        self._text.layer.draw(Vector2.zero())

    def __enter__(self) -> proto.Scene:
        return self

    def __exit__(self, exc_type: type[BaseException], exc_val: BaseException, exc_tb: TracebackType) -> bool | None:
        return None


def _loading_screen(screen_shape: Vector2Int) -> Sprite:
    loading = SpritesLoader.from_meta().load_loading_screen()
    return loading.reshape(screen_shape)
