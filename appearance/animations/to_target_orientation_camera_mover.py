from attrs import define, field

from appearance.game_engine.game_engine_arc.in_game_time import InGameTime
from mathematics.basic import sign
from appearance import protocols as proto
from mathematics.vector import Vector2
from observer import Event, OnEventSubscriber
from statuses import Status, MISSING, DEFAULT

DEFAULT_MOVEMENT_SPEED = 150
INFINITY = float("inf")


@define
class ToTargetOrientationCameraMover:
    _orientation: proto.CameraOrientation
    _in_game_time: InGameTime
    _target_orientation: proto.CameraOrientation | Status = MISSING
    _movement_speed: float = DEFAULT_MOVEMENT_SPEED
    _time_to_move: float = 0
    _movement_start: float = 0

    _target_has_been_reached: Event[None] = field(init=False, factory=Event)

    @property
    def has_target(self) -> bool:
        return self._target_orientation is not MISSING

    @property
    def target_has_been_reached(self) -> OnEventSubscriber[None]:
        return self._target_has_been_reached.subscriber

    @property
    def _delta_position(self) -> Vector2:
        return (self._target_orientation.position -
                self._orientation.position)

    def set_target(self, target: proto.CameraOrientation, *, time: float | Status = DEFAULT) -> None:
        self._target_orientation = target
        self._movement_start = self._in_game_time.get()

        if time == DEFAULT:
            self._movement_speed = DEFAULT_MOVEMENT_SPEED
            self._time_to_move = self._delta_position.length() / self._movement_speed
            return

        self._movement_speed = self._delta_position.length() * self._orientation.zoom ** .5 / time
        self._time_to_move = time

    def update(self, dt: float) -> None:
        if not self.has_target:
            return

        if not (self._in_game_time.get() > self._movement_start + self._time_to_move
                or all((self._movement(dt),
                        self._zoom(dt)))):
            return

        self._orientation.take_from(self._target_orientation)
        self._target_orientation = MISSING
        self._target_has_been_reached.invoke()

    def _movement(self, dt: float) -> bool:
        ds = self._get_movement_speed() * dt

        direction = self._delta_position
        if direction.length() < ds or ds == 0:
            return True

        if direction.length() > 1:
            direction = direction.normalize()

        direction = self._orientation.rotation.apply(direction)

        self._orientation.move(ds * direction)
        return False

    def _zoom(self, dt: float) -> bool:
        direction = self._target_orientation.zoom - self._orientation.zoom
        abs_dz = self._get_zoom_speed() * dt

        if abs(direction) < abs_dz or abs_dz == 0:
            return True

        direction = sign(direction)
        zoom = self._orientation.zoom
        multiplier = (zoom + abs_dz * direction) / zoom

        self._orientation.zoom_in(multiplier)
        return False

    def _get_zoom_speed(self) -> float:
        speed = self._get_movement_speed()
        if speed == 0:
            return 0

        time = self._delta_position.length() / speed
        if time == 0:
            return 0

        return abs(self._target_orientation.zoom - self._orientation.zoom) / time

    def _get_movement_speed(self) -> float:
        return self._movement_speed / self._orientation.zoom ** .5
