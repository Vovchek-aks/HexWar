from pathlib import Path


class Font:
    def __init__(self, file_path: Path | None = None, size: int = 12) -> None:
        self._file_path = file_path
        self._font_size = size

    @property
    def file_path(self) -> Path | None:
        return self._file_path

    @property
    def font_size(self) -> int:
        return self._font_size
