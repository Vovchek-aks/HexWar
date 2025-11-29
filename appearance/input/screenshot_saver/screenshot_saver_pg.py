from datetime import datetime
from pathlib import Path

from attrs import frozen
import pygame as pg

SCREENSHOT_KEY = pg.K_F2
SCREENSHOTS_FOLDER = Path("data/screenshots")


@frozen
class ScreenshotSaver:
    _screen: pg.Surface

    def update(self, keys: pg.key.ScancodeWrapper) -> None:
        if not keys[SCREENSHOT_KEY]:
            return

        date = datetime.now()
        filename = f"{date.day}_{date.month}_{date.year} {date.hour}_{date.minute}_{date.second}.png"
        pg.image.save(self._screen, SCREENSHOTS_FOLDER / filename)
