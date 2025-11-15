from attrs import define

from core import protocols as proto
from color import Color


@define
class PlayerData(proto.PlayerData):
    _color: Color
    _name: str

    @property
    def color(self) -> Color:
        return self._color

    @property
    def name(self) -> str:
        return self._name
