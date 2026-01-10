from types import TracebackType

from attrs import frozen

import appearance.protocols as proto
from statuses import Status, MISSING


@frozen
class GameScene(proto.Scene):
    _drawer: proto.FrameDrawer
    _updater: proto.Updater
    _input_state: proto.InputState

    def next(self) -> proto.Scene | Status:
        return MISSING

    def update(self) -> None:
        self._updater.update(self._input_state)

    def draw(self) -> None:
        self._drawer.draw_frame(self._input_state.mouse_position)

    def __enter__(self) -> proto.Scene:
        return self

    def __exit__(self, exc_type: type[BaseException], exc_val: BaseException, exc_tb: TracebackType) -> bool | None:
        return None
