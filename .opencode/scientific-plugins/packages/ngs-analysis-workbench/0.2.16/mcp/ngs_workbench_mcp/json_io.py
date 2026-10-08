"""Small JSON file helpers shared by the MCP package."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_json_object(path: Path) -> dict[str, Any]:
    """Read a JSON file whose top-level value must be an object."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object in {path}")
    return value


def write_json_object(path: Path, value: dict[str, Any]) -> None:
    """Atomically write a JSON object, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(f"{path.suffix}.tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
