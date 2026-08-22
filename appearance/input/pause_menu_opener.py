from typing import Callable

from attrs import define
import arcade as arc

ESCAPE_KEY = arc.key.ESCAPE


@define
class EscapePressHandler:
    _prepare_pause_menu_opening: Callable[[], bool]
    _open_pause_menu: Callable[[], None]
    _is_currently_pressed: bool = False

    def update(self, keys: set[int]) -> None:
        if ESCAPE_KEY not in keys:
            self._is_currently_pressed = False
            return

        if self._is_currently_pressed:
            return

        self._is_currently_pressed = True
        if self._prepare_pause_menu_opening():
            self._open_pause_menu()
