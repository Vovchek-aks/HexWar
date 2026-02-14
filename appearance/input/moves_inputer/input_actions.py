from abc import ABCMeta

from attrs import frozen

from appearance.input.clicks_catcher.click import MouseButtons, Click
from mathematics.vector import Vector2Int
import appearance.protocols as proto
from core.protocols import Figure
from statuses import Status


class InputAction(proto.InputAction, metaclass=ABCMeta):
    ...


@frozen
class NullClickAction(InputAction):
    click: Click


@frozen
class CellClickAction(InputAction):
    coord: Vector2Int
    buttons: MouseButtons


@frozen
class ButtonPressAction(InputAction, metaclass=ABCMeta):
    coord: Vector2Int | Status


@frozen
class CreationButtonPressAction(ButtonPressAction):
    figure: type[Figure]


@frozen
class ConversionButtonPressAction(ButtonPressAction):
    target: type[Figure]


@frozen
class CaptureButtonPressAction(ButtonPressAction):
    ...


@frozen
class AttackButtonPressAction(ButtonPressAction):
    ...


@frozen
class PullingInitiationButtonPressAction(ButtonPressAction):
    ...


@frozen
class PullingTerminationButtonPressAction(ButtonPressAction):
    ...


@frozen
class OreshnikLaunchButtonPressAction(ButtonPressAction):
    ...
