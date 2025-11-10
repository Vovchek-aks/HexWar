from attrs import frozen

from appearance import protocols as proto
from mathematics.vector import Vector2Int, Vector2


@frozen
class Camera(proto.Camera):
    _screen_shape: Vector2Int
    _orientation: proto.ReadonlyCameraOrientation

    @property
    def orientation(self) -> proto.ReadonlyCameraOrientation:
        return self._orientation

    def world_to_screen(self, point: Vector2) -> Vector2:
        center = self._screen_shape.as_vector2 / 2
        position, rotation, zoom = self._orientation.tuple
        return rotation.apply(point - position) * zoom + center

    def screen_to_world(self, point: Vector2) -> Vector2:
        center = self._screen_shape.as_vector2 / 2
        position, rotation, zoom = self._orientation.tuple
        return rotation.inverse.apply((point - center) / zoom) + position
