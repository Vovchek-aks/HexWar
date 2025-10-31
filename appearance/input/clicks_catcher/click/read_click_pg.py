import pygame as pg

import appearance.protocols as proto
from appearance.game_engine.game_engine_pg.events import Events
from appearance.input.clicks_catcher.click import Click, Buttons
from mathematics.vector import Vector2
from statuses import Status, MISSING

_LEFT = 1
_MIDDLE = 2
_RIGHT = 3


def read_click(events: Events, mouse_position: Vector2) -> proto.Click | Status:
    if (event := events.get(pg.MOUSEBUTTONDOWN)) is MISSING:
        return MISSING

    is_left = event.button == _LEFT
    is_right = event.button == _RIGHT
    is_middle = event.button == _MIDDLE

    if not any((is_left, is_right, is_middle)):
        return MISSING

    buttons = Buttons(is_left, is_right, is_middle)
    return Click(mouse_position, buttons)
