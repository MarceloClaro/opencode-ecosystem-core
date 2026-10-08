"""Target-side input inspection and approved preparation, runnable with only Python's stdlib."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from collections.abc import Callable
from contextlib import nullcontext, suppress
from pathlib import Path
from typing import Any


def validate_path(path: Path) -> None:
    if not path.is_absolute() or path.resolve(strict=False) != path:
        raise ValueError(
            f"input or preparation path must be absolute and contain no symlinks: {path}"
        )


def check_run_directory(value: str) -> None:
    path = Path(value)
    validate_path(path)
    if path.exists():
        raise ValueError(f"run_dir already exists: {path}")
    parent = next(parent for parent in path.parents if parent.exists())
    if not parent.is_dir() or not os.access(parent, os.W_OK | os.X_OK):
        raise ValueError(f"run_dir parent is not writable: {parent}")


def inspect_file(path: str, read_text: bool = False) -> dict[str, Any]:
    source = Path(path)
    validate_path(source)
    if not source.is_file():
        raise ValueError(f"input is not a regular file: {source}")
    digest = hashlib.sha256()
    size = 0
    content = bytearray()
    with source.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            size += len(chunk)
            digest.update(chunk)
            if read_text:
                content.extend(chunk)
    return {
        "bytes": size,
        "sha256": f"sha256:{digest.hexdigest()}",
        **({"content": content.decode("utf-8-sig")} if read_text else {}),
    }


def file_identity(path: Path) -> tuple[int, str]:
    observed = inspect_file(str(path))
    return observed["bytes"], observed["sha256"]


def download_file(executable: str, item: dict[str, Any], destination: Path) -> None:
    # Inherit the remote controller's process group so cancellation also stops curl.
    subprocess.run(
        [
            executable,
            "--fail",
            "--silent",
            "--show-error",
            "--proto",
            "=https",
            "--max-redirs",
            "0",
            "--output",
            str(destination),
            item["url"],
        ],
        check=True,
        timeout=300,
    )


def prepare(
    preparation: dict[str, Any] | None,
    *,
    download: Callable = download_file,
    lock: Any = None,
    checkpoint: Callable[[], None] = lambda: None,
) -> None:
    if preparation is None:
        return
    lock = lock or nullcontext()
    destination = Path(preparation["destination_dir"])
    validate_path(destination)
    with lock:
        checkpoint()
        destination.mkdir(parents=True, mode=0o755, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=".ngs-preparation.", dir=destination))
    created: list[Path] = []
    try:
        for index, item in enumerate(preparation["operations"]):
            relative = Path(item["relative_path"])
            target = destination / relative
            if relative.is_absolute() or ".." in relative.parts or str(target) != item["path"]:
                raise ValueError(f"unsafe approved preparation destination: {target}")
            validate_path(target)
            expected = (item["bytes"], item["sha256"])
            if target.exists():
                if file_identity(target) != expected:
                    raise ValueError(f"preparation would overwrite a conflicting file: {target}")
                continue
            temporary = staging / f"operation-{index}"
            if item["operation"] == "download_verified_file":
                download(preparation["transfer_executable"], item, temporary)
            elif item["operation"] == "write_generated_file":
                temporary.write_text(item["content"], encoding="utf-8")
            else:
                raise ValueError(f"unsupported approved preparation: {item['operation']}")
            if file_identity(temporary) != expected:
                raise ValueError(f"preparation artifact differs from the approved plan: {target}")
            with lock:
                checkpoint()
                validate_path(target)
                target.parent.mkdir(parents=True, exist_ok=True)
                try:
                    os.link(temporary, target)
                except FileExistsError:
                    if file_identity(target) != expected:
                        raise ValueError(
                            f"conflicting approved preparation file: {target}"
                        ) from None
                else:
                    created.append(target)
    except Exception:
        for path in reversed(created):
            with suppress(OSError, ValueError):
                validate_path(path)
                path.unlink(missing_ok=True)
        raise
    finally:
        with suppress(OSError, ValueError):
            validate_path(staging)
            shutil.rmtree(staging)


def run(plan_path: str, expected_plan: str, inputs: dict[str, str]) -> None:
    plan = json.loads(Path(plan_path).read_text(encoding="utf-8"))
    plan.pop("plan_checksum", None)
    if hashlib.sha256(json.dumps(plan, sort_keys=True).encode()).hexdigest() != expected_plan:
        raise ValueError("approved plan changed before target-side preparation")
    prepare(plan.get("preparation"))
    for path, checksum in inputs.items():
        if inspect_file(path)["sha256"] != checksum:
            raise ValueError(f"approved input file changed before controller launch: {path}")
    os.execvp(plan["command_argv"][0], plan["command_argv"])
