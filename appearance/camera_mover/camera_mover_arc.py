from attrs import frozen

from appearance.input.keyboard_camera_mover import KeyboardCameraMover
from appearance.animations.to_target_orientation_camera_mover import ToTargetOrientationCameraMover


@frozen
class CameraMover:
    _keyboard_kamera_mover: KeyboardCameraMover
    _to_target_camera_mover: ToTargetOrientationCameraMover

    def update(self, mouse_wheel_delta: float, keys: set[int], dt: float) -> None:
        if self._to_target_camera_mover.has_target:
            self._to_target_camera_mover.update(dt)
            return

        self._keyboard_kamera_mover.update(mouse_wheel_delta, keys, dt)
