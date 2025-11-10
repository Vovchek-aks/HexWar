from typing import Protocol, Callable

from attrs import frozen, field

import appearance.protocols as proto
from mathematics.vector import Vector2
from observer import Event, OnEventSubscriber


@frozen
class ShapeLayer(proto.ClicksCatchingLayer):
    _shape: "_Shape"
    _was_clicked: Event[proto.Click, None] = field(init=False, factory=Event)

    @property
    def was_clicked(self) -> OnEventSubscriber[proto.Click, None]:
        return self._was_clicked.subscriber

    def can_catch(self, click: proto.Click) -> bool:
        return self._shape.is_surrounding(click.screen_position)

    def catch(self, click: proto.Click) -> None:
        assert self.can_catch(click)

        self._was_clicked.invoke(click)


class _Shape(Protocol):
    def is_surrounding(self, point: Vector2) -> bool:
        ...
