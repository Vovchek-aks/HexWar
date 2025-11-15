from pathlib import Path
import json

META_FILE = "meta.json"


def read_meta(folder: Path | str) -> dict[str, ...]:
    path = folder / META_FILE
    return read_json(path)


def read_json(path: Path) -> dict[str, ...]:
    with path.open(encoding='utf-8') as file:
        return json.load(file)
