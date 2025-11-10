from attrs import frozen

from appearance.input.clicks_catcher.click import MouseButtons, Click
from mathematics.vector import Vector2Int
import appearance.protocols as proto

InputAction = proto.InputAction


@frozen
class NullClickAction(proto.InputAction):
    click: Click


@frozen
class CellClickAction(proto.InputAction):
    coord: Vector2Int
    buttons: MouseButtons
