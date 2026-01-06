from types import TracebackType

from attrs import define, field
import arcade as arc

from appearance import protocols as proto
from statuses import Status, MISSING
from mathematics.vector import Vector2
from mathematics.angle import Angle
from appearance.graphics.camera.camera_orientation import CameraOrientation


@define
class CameraAssistant(proto.CameraAssistant):
    @classmethod
    def make(cls, camera: proto.Camera) -> "CameraAssistant":
        arcade_camera = arc.Camera2D()
        self = cls(camera, camera.orientation.mutable_copy(), arcade_camera)
        camera.orientation.has_changed.subscribe(self._update_arcade_camera_orientation)
        return self

    _camera: proto.Camera
    _orientation: CameraOrientation
    _arcade_camera: arc.Camera2D

    _last_orientation: CameraOrientation | Status = field(init=False, default=MISSING)

    def _update_arcade_camera_orientation(self) -> None:
        self._orientation = self._camera.orientation.mutable_copy()

    def _update_arcade_camera(self, orientation: CameraOrientation) -> None:
        position, rotation, zoom = orientation.tuple
        self._arcade_camera.position = position.tuple
        self._arcade_camera.angle = rotation.degrees
        self._arcade_camera.zoom = zoom

    def __enter__(self) -> "CameraAssistant":
        assert self._last_orientation is MISSING

        camera = self._arcade_camera
        self._last_orientation = CameraOrientation(Vector2(*camera.position), Angle(camera.angle), camera.zoom)
        self._update_arcade_camera(self._orientation)
        self._arcade_camera.use()
        return self

    def __exit__(self,
                 exc_type: type[BaseException],
                 exc_val: BaseException,
                 exc_tb: TracebackType) -> bool | None:
        assert self._last_orientation is not MISSING

        self._update_arcade_camera(self._last_orientation)
        self._arcade_camera.use()
        self._last_orientation = MISSING
        return None
