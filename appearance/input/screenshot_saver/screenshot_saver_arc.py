from datetime import datetime
from pathlib import Path

from attrs import frozen
import arcade as arc
from PIL import Image

SCREENSHOT_KEY = arc.key.F2
SCREENSHOTS_FOLDER = Path("data/screenshots")


@frozen
class ScreenshotSaver:
    def update(self, keys: set[int]) -> None:
        if SCREENSHOT_KEY not in keys:
            return

        date = datetime.now()
        image = arc.get_image()
        pil_image = Image.frombytes("RGBA", image.size, image.tobytes())
        filename = f"{date.day}_{date.month}_{date.year} {date.hour}_{date.minute}_{date.second}.png"
        pil_image.save(SCREENSHOTS_FOLDER / filename)
