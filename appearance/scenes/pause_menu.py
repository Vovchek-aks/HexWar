from attrs import define

import appearance.protocols as proto
from appearance.graphics.layer_drawers.layers_drawer import LayersDrawer
from appearance.input.clicks_catcher import ClicksCatcher
from appearance.input.pause_menu_opener import PauseMenuOpener
from appearance.input.screenshot_saver import ScreenshotSaver


@define
class PauseMenu:
    @classmethod
    def make(cls,
             screenshot_saver: ScreenshotSaver,
             input_state: proto.InputState,
             layers: list[proto.LayerHolder],
             pause_menu_opener: PauseMenuOpener) -> "PauseMenu":
        assert layers
        return cls(screenshot_saver, ClicksCatcher(layers), input_state, LayersDrawer(layers[::-1]), pause_menu_opener)

    _screenshot_saver: ScreenshotSaver
    _clicks_catcher: ClicksCatcher
    _input_state: proto.InputState
    _layers: LayersDrawer
    _pause_menu_opener: PauseMenuOpener

    def update(self) -> None:
        self._screenshot_saver.update(self._input_state.pressed_keys)
        self._clicks_catcher.update(self._input_state.last_frame_clicks)
        self._pause_menu_opener.update(self._input_state.pressed_keys)

    def draw(self) -> None:
        self._layers.draw(self._input_state.mouse_position)
