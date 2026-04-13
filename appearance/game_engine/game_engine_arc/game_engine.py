from my_types import TracebackType
from typing import Callable

from attrs import frozen

from appearance.game_engine.game_engine_arc.window import Window
import appearance.protocols as proto
from appearance.scenes.scene_switcher import SceneSwitcher
from mathematics.vector import Vector2Int


@frozen
class GameEngine:
    @classmethod
    def make(cls,
             caption: str,
             ups: int,
             is_fullscreen: bool,
             screen_shape: Vector2Int,
             make_scene: Callable[[Vector2Int, Window], proto.Scene]) -> "GameEngine":
        window = Window(ups, is_fullscreen, caption, screen_shape)
        scene_switcher = SceneSwitcher.make(make_scene(screen_shape, window))
        self = cls(caption, window, scene_switcher)
        window.update_started.subscribe(self.update)
        window.draw_event.subscribe(self.draw)
        return self

    _caption: str
    _window: Window
    _scene_switcher: proto.SceneSwitcher

    def run(self) -> None:
        self._window.run()

    def update(self, dt: float) -> None:
        self._scene_switcher.update(self._window.close)
        self._scene_switcher.scene.update()
        # print(f"FPS: {1 / dt:.0f}")

    def draw(self) -> None:
        self._scene_switcher.scene.draw()

    def __enter__(self) -> "GameEngine":
        return self

    def __exit__(self,
                 exc_type: type[BaseException],
                 exc_val: BaseException,
                 exc_tb: TracebackType) -> bool | None:
        return None
