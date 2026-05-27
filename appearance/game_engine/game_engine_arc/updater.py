from typing import Iterator

from attrs import frozen

from appearance.audio.music.music_player import MusicPlayer
from appearance.camera_mover import CameraMover
from appearance.game_engine.game_engine_arc.in_game_time import InGameTime
from appearance.game_engine.game_engine_arc.input_state import InputState
from appearance.input.clicks_catcher import ClicksCatcher
from appearance.input.pause_menu_opener import PauseMenuOpener
from appearance.input.screenshot_saver import ScreenshotSaver
from appearance.layer import Layer
import appearance.protocols as proto


@frozen
class Updater(proto.Updater):
    @classmethod
    def make(cls,
             camera_mover: CameraMover,
             camera_orientation: proto.CameraOrientation,
             screenshot_saver: ScreenshotSaver,
             pause_manu_opener: PauseMenuOpener,
             mouse_movement_observer: proto.MouseMovementObserver,
             layers: list[Layer],
             player_turner: Iterator[None],
             music_player: MusicPlayer,
             in_game_time: InGameTime) -> "Updater":
        clicks_catcher = ClicksCatcher(layers)
        return cls(camera_mover,
                   camera_orientation,
                   screenshot_saver,
                   pause_manu_opener,
                   mouse_movement_observer,
                   clicks_catcher,
                   player_turner,
                   music_player,
                   in_game_time)

    _camera_mover: CameraMover
    _camera_orientation: proto.CameraOrientation
    _screenshot_saver: ScreenshotSaver
    _pause_menu_opener: PauseMenuOpener
    _mouse_movement_observer: proto.MouseMovementObserver
    _clicks_catcher: ClicksCatcher
    _player_turner: Iterator[None]
    _music_player: MusicPlayer
    _in_game_time: InGameTime

    def update(self, input_state: InputState) -> None:
        self._camera_mover.update(input_state.last_frame_mouse_wheel_delta,
                                  input_state.pressed_keys,
                                  input_state.dt)
        self._camera_orientation.update()
        self._screenshot_saver.update(input_state.pressed_keys)
        self._pause_menu_opener.update(input_state.pressed_keys)
        self._mouse_movement_observer.update(input_state.mouse_position)
        self._clicks_catcher.update(input_state.last_frame_clicks)
        self._music_player.update()
        self._in_game_time.update(input_state.dt)
        next(self._player_turner)
