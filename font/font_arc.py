from pathlib import Path
from typing import ClassVar

from attrs import frozen
import arcade as arc

FONTS_FOLDER = Path("data/fonts")
DEFAULT = "Calibri"

_NAME_OF = {
    "TypewriterRegular": "GNUTypewriter Standard",
    "PT_Serif-Web-Regular": "PT Serif"
}


@frozen
class Font:
    _loaded: ClassVar[set[str]] = set()

    @classmethod
    def make(cls,
             path: str | Path | None,
             size: int = 12,
             is_bold: bool = False,
             is_italic: bool = False) -> "Font":
        name = _NAME_OF.get(str(path), DEFAULT)

        if path and path not in cls._loaded:
            cls._loaded.add(path)
            path = (FONTS_FOLDER / path).with_suffix(".ttf")
            arc.load_font(path)

        return cls(name, size, is_bold, is_italic)

    _name: str
    _size: int = 12
    _is_bold: bool = False
    _is_italic: bool = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def size(self) -> int:
        return self._size

    @property
    def is_bold(self) -> bool:
        return self._is_bold

    @property
    def is_italic(self) -> bool:
        return self._is_italic
