"""Execute a fixed, bounded workflow operation on an approved Linux SSH host."""

from __future__ import annotations

import hashlib
import json
import os
import signal
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any, BinaryIO

LOG_TAIL_BYTES = 12_000


def read_tail(handle: BinaryIO, limit: int = LOG_TAIL_BYTES) -> str:
    """Shared local/SSH reader, included in this standalone remote program."""
    handle.seek(0, os.SEEK_END)
    handle.seek(max(0, handle.tell() - limit))
    return handle.read(limit).decode("utf-8", errors="replace")


def _path(root: Path, value: str) -> Path:
    candidate = Path(value)
    if (
        not candidate.is_absolute()
        or (candidate != root and root not in candidate.parents)
        or candidate.resolve(strict=False) != candidate
    ):
        raise ValueError("approved remote path escapes its run or contains a symlink")
    return candidate


def _digest(candidate: Path) -> tuple[int, str]:
    value = hashlib.sha256()
    with candidate.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return candidate.stat().st_size, "sha256:" + value.hexdigest()


def execute(request: dict[str, Any], controller: str) -> Any:
    root = Path(request["run_dir"])
    if not root.is_absolute() or root.resolve(strict=False) != root:
        raise ValueError("approved remote run path is unsafe")

    operation = request["operation"]
    if operation == "file_select":
        for pattern in request["patterns"]:
            query = Path(pattern)
            directory = _path(root, str(root / query.parent))
            candidates = [_path(root, str(path)) for path in directory.glob(query.name)]
            files = [path for path in candidates if path.is_file()]
            if files:
                return str(max(files, key=lambda path: (path.stat().st_mtime_ns, path.name)))
        return None

    if operation in {"file_tail", "file_stream"}:
        path = _path(root, str(root / request["relative_path"]))
        with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), "rb") as handle:
            metadata = os.fstat(handle.fileno())
            if not stat.S_ISREG(metadata.st_mode):
                raise ValueError("remote evidence is not a regular file")
            if operation == "file_tail":
                return read_tail(handle)
            remaining = metadata.st_size
            while remaining:
                chunk = handle.read(min(remaining, 64 * 1024))
                if not chunk:
                    raise ValueError("remote evidence was truncated during observation")
                sys.stdout.buffer.write(chunk)
                remaining -= len(chunk)
            return None

    if operation == "prepare":
        if root.exists():
            raise ValueError("approved remote run directory already exists")
        root.mkdir(parents=True, mode=0o700)
        for value in request["destinations"]:
            _path(root, value).parent.mkdir(parents=True, exist_ok=True)
        for item in request["generated"]:
            destination = _path(root, item["destination"])
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(item["content"], encoding="utf-8")
        return {"ok": True}

    if operation == "verify":
        for item in request["files"]:
            candidate = _path(root, item["destination"])
            if candidate.is_symlink() or _digest(candidate) != (item["bytes"], item["sha256"]):
                raise ValueError("remote staged file differs from approved bytes")
        return {"ok": True}

    if operation == "launch":
        receipt = _path(root, str(root / "workflow" / "controller.json"))
        if receipt.is_file():
            identity = json.loads(receipt.read_text())
            execute({**request, "operation": "status", "identity": identity}, controller)
            return identity
        log = _path(root, str(root / request.get("log_path", "logs/nextflow.log")))
        log.parent.mkdir(parents=True, exist_ok=True)
        terminal = _path(root, str(root / "workflow" / "controller.exit"))
        payload = {
            "argv": request["argv"],
            "run_dir": str(root),
            "log": str(log),
            "exit": str(terminal),
        }
        process = subprocess.Popen(
            [sys.executable, "-c", controller, json.dumps(payload)],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        fields = Path(f"/proc/{process.pid}/stat").read_text().split()
        result = {"pid": process.pid, "start_time": fields[21], "run_dir": str(root)}
        receipt.write_text(json.dumps(result))
        return result

    if operation == "identity":
        result = json.loads(_path(root, str(root / "workflow" / "controller.json")).read_text())
        if result["pid"] != request.get("pid", result["pid"]) or result["run_dir"] != str(root):
            raise ValueError("remote controller does not match its durable run identity")
        return result

    if operation in {"status", "stop"}:
        identity = request["identity"]
        receipt = json.loads(_path(root, str(root / "workflow" / "controller.json")).read_text())
        if identity != receipt:
            raise ValueError("remote controller identity does not match its durable receipt")
        terminal = _path(root, str(root / "workflow" / "controller.exit"))
        if terminal.is_file() and not terminal.is_symlink():
            return {"running": False, "return_code": int(terminal.read_text().strip())}

        process = Path(f"/proc/{identity['pid']}")
        try:
            fields = (process / "stat").read_text().split()
            command = (process / "cmdline").read_bytes()
            running = (
                fields[2] != "Z"
                and fields[21] == identity["start_time"]
                and json.loads(command.split(b"\0")[-2])["run_dir"] == str(root)
            )
        except (OSError, IndexError, KeyError, TypeError, ValueError):
            running = False
        if operation == "stop" and running:
            os.killpg(identity["pid"], signal.SIGTERM)
        elif operation == "stop":
            raise ValueError("refusing to signal an unverified remote controller")
        return {"running": running, "return_code": None}

    raise ValueError("unsupported remote workflow operation")


if __name__ == "__main__" and len(sys.argv) > 1:
    request = json.loads(sys.argv[1])
    controller = Path(__file__).with_name("remote_controller.py").read_text(encoding="utf-8")
    result = execute(request, controller)
    if request["operation"] != "file_stream":
        sys.stdout.write(json.dumps(result, separators=(",", ":")) + "\n")
