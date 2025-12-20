from typing import Iterator

from attrs import frozen

from appearance.game_engine.game_engine_arc.input_state import InputState
from appearance.input.camera_mover import CameraMover
from appearance.input.clicks_catcher import ClicksCatcher
from appearance.input.screenshot_saver import ScreenshotSaver
from appearance.layer import Layer
import appearance.protocols as proto


@frozen
class Updater:
    @classmethod
    def make(cls,
             camera_mover: CameraMover,
             screenshot_saver: ScreenshotSaver,
             mouse_movement_observer: proto.MouseMovementObserver,
             layers: list[Layer],
             player_turner: Iterator[None]) -> "Updater":
        clicks_catcher = ClicksCatcher(layers)
        return cls(camera_mover,
                   screenshot_saver,
                   mouse_movement_observer,
                   clicks_catcher,
                   player_turner)

    _camera_mover: CameraMover
    _screenshot_saver: ScreenshotSaver
    _mouse_movement_observer: proto.MouseMovementObserver
    _clicks_catcher: ClicksCatcher
    _player_turner: Iterator[None]

    def update(self, input_state: InputState) -> None:
        self._camera_mover.update(input_state.last_frame_mouse_wheel_delta,
                                  input_state.pressed_keys,
                                  input_state.dt)
        self._screenshot_saver.update(input_state.pressed_keys)
        self._mouse_movement_observer.update(input_state.mouse_position)
        self._clicks_catcher.update(input_state.last_frame_clicks)
        next(self._player_turner)
