from attrs import frozen, field

from appearance import protocols as proto
from mathematics.vector import Vector2


@frozen
class Camera(proto.Camera):
    _screen_shape: Vector2
    _orientation: proto.ReadonlyCameraOrientation

    @property
    def screen_shape(self) -> Vector2:
        return self._screen_shape

    @property
    def orientation(self) -> proto.ReadonlyCameraOrientation:
        return self._orientation

    def world_to_screen(self, point: Vector2) -> Vector2:
        center = self._screen_shape / 2
        position, rotation, zoom = self._orientation.tuple
        return rotation.apply(point - position) * zoom + center

    def screen_to_world(self, point: Vector2) -> Vector2:
        center = self._screen_shape / 2
        position, rotation, zoom = self._orientation.tuple
        return rotation.inverse.apply((point - center) / zoom) + position


@frozen
class CachedCamera(proto.Camera):
    @classmethod
    def make(cls, camera: proto.Camera) -> "CachedCamera":
        self = cls(camera)
        camera.orientation.has_changed.subscribe(self._clear_cache)
        return self

    _camera: proto.Camera
    _cache: dict[tuple[float, float], Vector2] = field(init=False, factory=dict)

    @property
    def screen_shape(self) -> Vector2:
        return self._camera.screen_shape

    @property
    def orientation(self) -> proto.ReadonlyCameraOrientation:
        return self._camera.orientation

    def world_to_screen(self, point: Vector2) -> Vector2:
        if (xy := point.tuple) in self._cache:
            return self._cache[xy]

        result = self._camera.world_to_screen(point)
        self._cache[xy] = result
        return result

    def screen_to_world(self, point: Vector2) -> Vector2:
        return self._camera.screen_to_world(point)

    def _clear_cache(self) -> None:
        self._cache.clear()
