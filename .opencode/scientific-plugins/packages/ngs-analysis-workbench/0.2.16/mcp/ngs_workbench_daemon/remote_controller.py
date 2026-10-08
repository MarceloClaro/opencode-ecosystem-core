"""Run one detached approved controller and publish its terminal receipt."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def run(request: dict[str, Any]) -> None:
    with Path(request["log"]).open("ab") as output:
        result = subprocess.run(
            request["argv"],
            cwd=request["run_dir"],
            stdout=output,
            stderr=subprocess.STDOUT,
            check=False,
        )
    temporary = Path(request["exit"] + ".tmp")
    temporary.write_text(str(result.returncode), encoding="utf-8")
    temporary.replace(request["exit"])


if __name__ == "__main__":
    run(json.loads(sys.argv[1]))
