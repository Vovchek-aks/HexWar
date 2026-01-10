from types import TracebackType

from attrs import frozen

from appearance.game_engine.game_engine_arc.window import Window
import appearance.protocols as proto


@frozen
class GameEngine:
    @classmethod
    def make(cls,
             caption: str,
             window: Window,
             scene_switcher: proto.SceneSwitcher) -> "GameEngine":
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
        self._scene_switcher.update()
        self._scene_switcher.scene.update()
        self._window.set_caption(f"{self._caption} {1 / dt:.0f}FPS")

    def draw(self) -> None:
        self._scene_switcher.scene.draw()

    def __enter__(self) -> "GameEngine":
        return self

    def __exit__(self,
                 exc_type: type[BaseException],
                 exc_val: BaseException,
                 exc_tb: TracebackType) -> bool | None:
        return None
