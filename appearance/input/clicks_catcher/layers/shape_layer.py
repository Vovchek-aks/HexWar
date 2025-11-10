from typing import Protocol, Callable

from attrs import frozen, field

import appearance.protocols as proto
from mathematics.vector import Vector2


@frozen
class ShapeLayer(proto.ClicksCatchingLayer):
    _shape: "_Shape"
    _catch: Callable[[proto.Click], None] = field(default=lambda click: None)

    def can_catch(self, click: proto.Click) -> bool:
        return self._shape.is_surrounding(click.screen_position)

    def catch(self, click: proto.Click) -> None:
        self._catch(click)


class _Shape(Protocol):
    def is_surrounding(self, point: Vector2) -> bool:
        ...
