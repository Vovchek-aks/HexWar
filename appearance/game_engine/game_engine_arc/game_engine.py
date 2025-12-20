from types import TracebackType

from attrs import frozen

from appearance.game_engine.game_engine_arc.input_state import InputState
from appearance.game_engine.game_engine_arc.frame_drawer import FrameDrawer
from appearance.game_engine.game_engine_arc.updater import Updater

from appearance.game_engine.game_engine_arc.window import Window


@frozen
class GameEngine:
    @classmethod
    def make(cls,
             caption: str,
             window: Window,
             drawer: FrameDrawer,
             updater: Updater,
             input_state: InputState) -> "GameEngine":
        self = cls(caption, window, drawer, updater, input_state)
        window.fixed_update_started.subscribe(self.update)
        window.draw_event.subscribe(self.draw)
        return self

    _caption: str
    _window: Window
    _drawer: FrameDrawer
    _updater: Updater
    _input_state: InputState

    def run(self) -> None:
        self._window.run()

    def update(self, dt: float) -> None:
        self._updater.update(self._input_state)

        self._window.set_caption(f"{self._caption} {1 / dt:.0f}FPS")

    def draw(self) -> None:
        self._drawer.draw_frame(self._input_state.mouse_position)

    def __enter__(self) -> "GameEngine":
        return self

    def __exit__(self,
                 exc_type: type[BaseException],
                 exc_val: BaseException,
                 exc_tb: TracebackType) -> bool | None:
        return None
