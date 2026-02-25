from types import TracebackType

from attrs import define, field

import appearance.protocols as proto
from appearance.scenes.game_scene import GameScene
from statuses import Status, MISSING


@define
class MultibotScene(proto.Scene):
    _game: GameScene

    _next_scene: proto.Scene | Status = field(init=False, default=MISSING)

    def next(self) -> proto.Scene | Status:
        return self._next_scene

    def update(self) -> None:
        self._game.update()

    def draw(self) -> None:
        self._game.draw()

    def on_reload(self, scene: proto.Scene) -> None:
        self._next_scene = scene

    def __enter__(self) -> proto.Scene:
        return self

    def __exit__(self, exc_type: type[BaseException], exc_val: BaseException, exc_tb: TracebackType) -> bool | None:
        return None
