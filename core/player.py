import pygame as pg
from attrs import define, field

from core import protocols as proto


@define
class Player(proto.Player):
    _color: pg.Color

    @property
    def color(self) -> pg.Color:
        return self._color
