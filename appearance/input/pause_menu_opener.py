from typing import Callable

from attrs import define
import arcade as arc

PAUSE_MENU_KEY = arc.key.ESCAPE


@define
class PauseMenuOpener:
    _open_pause_menu: Callable[[], None]
    _is_currently_pressed: bool = False

    def update(self, keys: set[int]) -> None:
        if PAUSE_MENU_KEY not in keys:
            self._is_currently_pressed = False
            return

        if self._is_currently_pressed:
            return

        self._is_currently_pressed = True
        self._open_pause_menu()
