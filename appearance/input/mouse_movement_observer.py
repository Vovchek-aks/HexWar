from attrs import define, field

from mathematics.vector import Vector2
from observer import Event, OnEventSubscriber
import appearance.protocols as proto


@define
class MouseMovementObserver(proto.MouseMovementObserver):
    _mouse_was_moved: Event[Vector2, None] = field(init=False, factory=Event)
    _previous_mouse_position: Vector2 = field(init=False, default=Vector2.zero())

    @property
    def mouse_was_moved(self) -> OnEventSubscriber[Vector2, None]:
        return self._mouse_was_moved.subscriber

    def update(self, mouse_position: Vector2) -> None:
        if mouse_position == self._previous_mouse_position:
            return

        self._previous_mouse_position = mouse_position
        self._mouse_was_moved.invoke(mouse_position)
