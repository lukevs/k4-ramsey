"""JSON and hash I/O shared by the runner and standalone strategies."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pydantic import BaseModel


def read_json(path: Path):
    """Read finite JSON, rejecting duplicate keys instead of silently losing data."""
    value = json.loads(
        Path(path).read_text(),
        object_pairs_hook=reject_duplicate_keys,
        parse_constant=reject_constant,
    )
    json.dumps(value, allow_nan=False)
    return value


def write_json(path: Path, data) -> None:
    """Atomically replace a checkpoint, never use this to overwrite final evidence."""
    path = Path(path)
    temporary = path.with_name(path.name + ".tmp")
    payload = (
        data.model_dump(mode="json", by_alias=True, exclude_none=True)
        if isinstance(data, BaseModel)
        else data
    )
    temporary.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def hash_file(path: Path) -> str:
    """Identify the exact bytes of a source, candidate, or executable."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    """Assemble one JSON object, refusing ambiguous repeated keys."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key: {key}")
        result[key] = value
    return result


def reject_constant(value: str):
    raise ValueError(f"nonfinite JSON constant: {value}")
