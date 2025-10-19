from abc import ABCMeta

from attrs import frozen

from appearance.protocols import ClicksCatchingLayer
from mathematics.vector import Vector2


class _DebugLayer(ClicksCatchingLayer, metaclass=ABCMeta):
    def catch(self, screen_position: Vector2) -> None:
        print(f"{type(self).__name__} had caught a click at {screen_position}")


class WholeScreenDebugLayer(_DebugLayer):
    def can_catch(self, screen_position: Vector2) -> bool:
        return True


@frozen
class RightSideDebugLayer(_DebugLayer):
    _threshold_x: int

    def can_catch(self, screen_position: Vector2) -> bool:
        return screen_position.x > self._threshold_x
