from pathlib import Path

import pygame as pg


class Font(pg.font.Font):
    def __init__(self, file_path: Path | None = None, size: int = 12) -> None:
        super().__init__(file_path, size)
        self._file_path = file_path
        self._font_size = size

    @property
    def file_path(self) -> Path | None:
        return self._file_path

    @property
    def font_size(self) -> int:
        return self._font_size
