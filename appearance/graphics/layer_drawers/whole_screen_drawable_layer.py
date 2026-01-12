from abc import ABCMeta, abstractmethod

from attrs import frozen
from typing_extensions import Protocol

import appearance.protocols as proto
from mathematics.vector import Vector2


@frozen
class WholeScreenDrawableLayer(proto.DrawableLayer):
    _draw: "Draw"

    def draw(self, mouse_position: Vector2) -> None:
        self._draw.background()


class Draw(Protocol, metaclass=ABCMeta):
    @abstractmethod
    def background(self) -> None:
        ...
