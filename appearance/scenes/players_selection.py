from types import TracebackType

from attrs import define, field

import appearance.protocols as proto
from appearance.graphics.layer_drawers.layers_drawer import LayersDrawer
from appearance.input.camera_mover import CameraMover
from appearance.input.clicks_catcher import ClicksCatcher
from appearance.input.screenshot_saver import ScreenshotSaver
from statuses import Status, MISSING, ABORT_NEEDED


@define
class PlayersSelectionScene(proto.Scene):
    @classmethod
    def make(cls,
             camera_mover: CameraMover,
             camera_orientation: proto.CameraOrientation,
             screenshot_saver: ScreenshotSaver,
             input_state: proto.InputState,
             layers: list[proto.LayerHolder]) -> "PlayersSelectionScene":
        return cls(camera_mover,
                   camera_orientation,
                   screenshot_saver,
                   ClicksCatcher(layers),
                   input_state,
                   LayersDrawer(layers[::-1]))

    _camera_mover: CameraMover
    _camera_orientation: proto.CameraOrientation
    _screenshot_saver: ScreenshotSaver
    _clicks_catcher: ClicksCatcher
    _input_state: proto.InputState
    _layers: LayersDrawer
    _next_scene: proto.Scene | Status = field(init=False, default=MISSING)

    def next(self) -> proto.Scene | Status:
        return self._next_scene

    def update(self) -> None:
        self._camera_mover.update(self._input_state.last_frame_mouse_wheel_delta,
                                  self._input_state.pressed_keys,
                                  self._input_state.dt)
        self._camera_orientation.update()
        self._screenshot_saver.update(self._input_state.pressed_keys)
        self._clicks_catcher.update(self._input_state.last_frame_clicks)

    def draw(self) -> None:
        self._layers.draw(self._input_state.mouse_position)

    def switch_to(self, scene: proto.Scene) -> None:
        self._next_scene = scene

    def __enter__(self) -> proto.Scene:
        return self

    def __exit__(self, exc_type: type[BaseException], exc_val: BaseException, exc_tb: TracebackType) -> bool | None:
        return None
