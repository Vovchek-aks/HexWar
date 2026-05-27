from attrs import define, frozen, field

from core.protocols import Board, Cells
from mathematics.angle import Angle
from mathematics.hex_geometry import get_world_position, DISTANCE_BETWEEN_CENTERS
from mathematics.vector import Vector2
from appearance import protocols as proto
from observer import Event, OnEventSubscriber


@define
class CameraOrientation(proto.CameraOrientation):
    @classmethod
    def starter(cls) -> "CameraOrientation":
        return cls(Vector2(0, 0), Angle(0), 1)

    @classmethod
    def for_board(cls, board: Board) -> "CameraOrientation":
        size = max(board.shape.tuple)
        rotation = Angle(-60)
        zoom = 450 / size
        position = Vector2(1.7, -1) * size * 0.43

        return cls(position, rotation, zoom)

    @classmethod
    def for_cells(cls, cells: Cells, board: Board, camera: proto.Camera, *, margin: float = 0) -> "CameraOrientation":
        assert cells

        screen_positions = [camera.world_to_screen(get_world_position(board.coordinates_of(cell)))
                            for cell in cells]
        max_x = max(position.x for position in screen_positions)
        min_x = min(position.x for position in screen_positions)
        max_y = max(position.y for position in screen_positions)
        min_y = min(position.y for position in screen_positions)

        orientation = camera.orientation
        width = max_x - min_x + DISTANCE_BETWEEN_CENTERS * orientation.zoom * (1 + margin * 2)
        height = max_y - min_y + DISTANCE_BETWEEN_CENTERS * orientation.zoom * (1 + margin * 2)
        screen_shape = camera.screen_shape
        zoom_ratio = min(screen_shape.x / width,
                         screen_shape.y / height)

        center = Vector2(max_x + min_x,
                         max_y + min_y) / 2
        position = camera.screen_to_world(center)

        return cls(position,
                   orientation.rotation,
                   orientation.zoom * zoom_ratio)

    _position: Vector2
    _rotation: Angle
    _zoom: float
    _had_changed: bool = field(init=False, default=False)

    _has_changed: Event[None] = field(init=False, factory=Event)

    @property
    def has_changed(self) -> OnEventSubscriber[None]:
        return self._has_changed.subscriber

    @property
    def position(self) -> Vector2:
        return self._position

    @property
    def rotation(self) -> Angle:
        return self._rotation

    @property
    def zoom(self) -> float:
        return self._zoom

    @property
    def tuple(self) -> tuple[Vector2, Angle, float]:
        return self._position, self._rotation, self._zoom

    def take_from(self, orientation: "CameraOrientation") -> None:
        self._position = orientation.position
        self._rotation = orientation.rotation
        self._zoom = orientation.zoom
        self._had_changed = True

    def update(self) -> None:
        if not self._had_changed:
            return

        self._has_changed.invoke()
        self._had_changed = False

    def move(self, delta: Vector2) -> "CameraOrientation":
        if delta == Vector2.zero():
            return self

        self._position += self._rotation.inverse.apply(delta)
        self._had_changed = True
        return self

    def rotate(self, angle: Angle) -> "CameraOrientation":
        if angle.degrees == 0:
            return self

        self._rotation += angle
        self._had_changed = True
        return self

    def zoom_in(self, ratio: float) -> "CameraOrientation":
        if ratio == 0:
            return self

        self._zoom *= ratio
        self._had_changed = True
        return self


@frozen
class ReadonlyCameraOrientation(proto.ReadonlyCameraOrientation):
    _orientation: proto.CameraOrientation

    @property
    def has_changed(self) -> OnEventSubscriber[None]:
        return self._orientation.has_changed

    @property
    def position(self) -> Vector2:
        return self._orientation.position

    @property
    def rotation(self) -> Angle:
        return self._orientation.rotation

    @property
    def zoom(self) -> float:
        return self._orientation.zoom

    @property
    def tuple(self) -> tuple[Vector2, Angle, float]:
        return self._orientation.tuple

    def mutable_copy(self) -> proto.CameraOrientation:
        return CameraOrientation(*self.tuple)
