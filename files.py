from pathlib import Path
import json

META_FILE = "meta.json"
BUILD_INFO_FILE = Path("data") / "build_info.json"


def read_meta[T](folder: Path | str) -> dict[str, T]:
    path = folder / META_FILE
    return read_json(path)


def read_build_info() -> dict[str, str]:
    return read_json(BUILD_INFO_FILE)


def read_json[T](path: Path) -> dict[str, T]:
    with path.open(encoding='utf-8') as file:
        return json.load(file)


def write_json[T](content: dict[str, T], path: Path) -> None:
    with path.open(encoding='utf-8', mode='w') as file:
        json.dump(content, file)
