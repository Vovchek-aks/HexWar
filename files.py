from pathlib import Path
import json

DATA = Path("data")
META_FILE = "meta.json"
BUILD_INFO_FILE = DATA / "build_info.json"
RANDOM_BOT_NAMES_FILE = DATA / "random_bot_names.json"


def read_meta[T](folder: Path | str) -> dict[str, T]:
    path = folder / META_FILE
    return read_json(path)


def read_build_info() -> dict[str, str]:
    return read_json(BUILD_INFO_FILE)


def read_random_bot_names() -> list[str]:
    return read_json(RANDOM_BOT_NAMES_FILE)


def read_json[T](path: Path) -> dict[str, T] | list[T]:
    with path.open(encoding='utf-8') as file:
        return json.load(file)


def write_json[T](content: dict[str, T], path: Path) -> None:
    with path.open(encoding='utf-8', mode='w') as file:
        json.dump(content, file)
