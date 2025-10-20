from abc import ABCMeta

from attrs import frozen

from appearance.protocols import ClicksCatchingLayer, Click


class _DebugLayer(ClicksCatchingLayer, metaclass=ABCMeta):
    def catch(self, click: Click) -> None:
        print(f"{type(self).__name__} had caught a click at {click.screen_position}")


class WholeScreenDebugLayer(_DebugLayer):
    def can_catch(self, click: Click) -> bool:
        return True


@frozen
class RightSideDebugLayer(_DebugLayer):
    _threshold_x: int

    def can_catch(self, click: Click) -> bool:
        return click.screen_position.x > self._threshold_x
