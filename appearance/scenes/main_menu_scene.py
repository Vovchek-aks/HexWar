from types import TracebackType

from attrs import define, field

import appearance.protocols as proto
from appearance.graphics.layer_drawers.layers_drawer import LayersDrawer
from appearance.input.clicks_catcher import ClicksCatcher
from appearance.input.screenshot_saver import ScreenshotSaver
from statuses import Status, MISSING, ABORT_NEEDED


@define
class MainMenuScene(proto.Scene):
    @classmethod
    def make(cls,
             screenshot_saver: ScreenshotSaver,
             input_state: proto.InputState,
             layers: list[proto.LayerHolder]) -> "MainMenuScene":
        return cls(screenshot_saver, ClicksCatcher(layers), input_state, LayersDrawer(layers[::-1]))

    _screenshot_saver: ScreenshotSaver
    _clicks_catcher: ClicksCatcher
    _input_state: proto.InputState
    _layers: LayersDrawer
    _next_scene: proto.Scene | Status = field(init=False, default=MISSING)

    def next(self) -> proto.Scene | Status:
        return self._next_scene

    def update(self) -> None:
        self._screenshot_saver.update(self._input_state.pressed_keys)
        self._clicks_catcher.update(self._input_state.last_frame_clicks)

    def draw(self) -> None:
        self._layers.draw(self._input_state.mouse_position)

    def on_play_was_pressed(self, scene: proto.Scene) -> None:
        self._next_scene = scene

    def on_exit_was_pressed(self) -> None:
        self._next_scene = ABORT_NEEDED

    def __enter__(self) -> proto.Scene:
        return self

    def __exit__(self, exc_type: type[BaseException], exc_val: BaseException, exc_tb: TracebackType) -> bool | None:
        return None
