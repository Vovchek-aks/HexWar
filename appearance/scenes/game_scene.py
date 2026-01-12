from types import TracebackType
from typing import Callable

from attrs import define, field

import appearance.protocols as proto
from statuses import Status, MISSING


@define
class GameScene(proto.Scene):
    _drawer: proto.FrameDrawer
    _updater: proto.Updater
    _input_state: proto.InputState
    _get_main_menu_loading_scene: Callable[[], proto.Scene]

    _next_scene: proto.Scene | Status = field(init=False, default=MISSING)

    def next(self) -> proto.Scene | Status:
        return self._next_scene

    def update(self) -> None:
        self._updater.update(self._input_state)

    def draw(self) -> None:
        self._drawer.draw_frame(self._input_state.mouse_position)

    def on_pause_menu_open_requested(self) -> None:
        # make proper pause menu
        self._next_scene = self._get_main_menu_loading_scene()

    def __enter__(self) -> proto.Scene:
        return self

    def __exit__(self, exc_type: type[BaseException], exc_val: BaseException, exc_tb: TracebackType) -> bool | None:
        return None
