from abc import ABC

from attrs import frozen

from appearance.input.clicks_catcher.click import Buttons
from mathematics.vector import Vector2Int


class InputAction(ABC):
    ...


@frozen
class CellClickAction(InputAction):
    coord: Vector2Int
    buttons: Buttons
