from attrs import define

from core import protocols as proto
from color import Color


@define
class Player(proto.Player):
    _color: Color

    @property
    def color(self) -> Color:
        return self._color
