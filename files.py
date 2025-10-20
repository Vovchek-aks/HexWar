from pathlib import Path
import json

META_FILE = "meta.json"


def read_meta(folder: Path | str) -> dict:
    path = folder / META_FILE
    with path.open(encoding='utf-8') as file:
        return json.load(file)
