from typing import Callable

from attrs import frozen
import arcade as arc

PAUSE_MENU_KEY = arc.key.ESCAPE


@frozen
class PauseMenuOpener:
    _open_pause_manu: Callable[[], None]

    def update(self, keys: set[int]) -> None:
        if PAUSE_MENU_KEY not in keys:
            return

        self._open_pause_manu()
