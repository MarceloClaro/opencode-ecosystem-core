"""Run one approved workflow on a frozen, user-managed SSH target."""

from __future__ import annotations

import io
import json
import os
import signal
import subprocess
import threading
from collections.abc import Callable, Iterator
from contextlib import contextmanager, suppress
from pathlib import Path
from typing import Any, TextIO

from .hashing import file_identity, sha256_hex
from .inspection import effective_access

_CONTROLLER = Path(__file__).with_name("remote_controller.py").read_text(encoding="utf-8")
_REMOTE_PROGRAM = Path(__file__).with_name("remote_operations.py").read_text(encoding="utf-8")
_INPUT_PROGRAM = Path(__file__).with_name("input_files.py").read_text(encoding="utf-8")


class TransportError(ValueError):
    """The frozen SSH target could not currently be reached or trusted."""


def _invoke(remote: dict[str, Any], operation: str, *, timeout: int = 30, **payload: Any) -> Any:
    request = {
        "run_dir": remote["run_dir"],
        "workspace_root": remote["workspace_root"],
        "operation": operation,
        **payload,
    }
    source = (
        f"{_REMOTE_PROGRAM}\n"
        f"print(json.dumps(execute(json.loads({json.dumps(request, separators=(',', ':'))!r}), "
        f"{_CONTROLLER!r}), separators=(',', ':')))\n"
    )
    return _run_program(remote, source, operation, timeout)


def _run_program(remote: dict[str, Any], source: str, operation: str, timeout: int = 30) -> Any:
    alias = remote["host_access"]["alias"]
    if effective_access(alias) != remote["host_access"]:
        raise TransportError("approved SSH access changed before the remote operation")
    try:
        result = subprocess.run(
            ["ssh", "-T", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", alias, "python3", "-"],
            input=source,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise TransportError(f"approved SSH workflow {operation} is unreachable") from exc
    if result.returncode != 0:
        error = f"approved SSH workflow {operation} failed: {result.stderr.strip()}"
        if "Traceback (most recent call last):" not in result.stderr:
            raise TransportError(error)
        raise ValueError(error)
    return json.loads(result.stdout)


def inspect_input(remote: dict[str, Any], path: str, *, read_text: bool = False) -> dict[str, Any]:
    """Read and bind one explicit target-side input; never stage it locally."""
    source = f"{_INPUT_PROGRAM}\nprint(json.dumps(inspect_file({path!r}, {read_text!r})))\n"
    return _run_program(remote, source, "input inspection")


def preparation_executable(remote: dict[str, Any], destination: str, downloads: bool) -> str | None:
    source = (
        f"{_INPUT_PROGRAM}\nvalidate_path(Path({destination!r}))\n"
        f"print(json.dumps(shutil.which('curl') if {downloads!r} else None))\n"
    )
    return _run_program(remote, source, "preparation inspection")


def check_run_directory(remote: dict[str, Any], path: str) -> None:
    source = f"{_INPUT_PROGRAM}\ncheck_run_directory({path!r})\nprint('null')\n"
    _run_program(remote, source, "run directory inspection")


def tail_file(remote: dict[str, Any], relative_path: str) -> str:
    """Read at most 12 KB from one run file without saving it locally."""
    return _invoke(remote, "file_tail", relative_path=relative_path, timeout=10)


def select_file(remote: dict[str, Any], patterns: tuple[str, ...]) -> str | None:
    """Select the newest regular file from the first matching run-relative pattern."""
    return _invoke(remote, "file_select", patterns=patterns, timeout=10)


@contextmanager
def stream_file(
    remote: dict[str, Any], relative_path: str, *, timeout: float = 10
) -> Iterator[TextIO]:
    """Stream one run file; normal context exit drains and verifies SSH completion."""
    alias = remote["host_access"]["alias"]
    if effective_access(alias) != remote["host_access"]:
        raise TransportError("approved SSH access changed before the remote operation")
    request = {
        "run_dir": remote["run_dir"],
        "workspace_root": remote["workspace_root"],
        "operation": "file_stream",
        "relative_path": relative_path,
    }
    source = f"{_REMOTE_PROGRAM}\nexecute(json.loads({json.dumps(request)!r}), '')\n"
    try:
        process = subprocess.Popen(
            ["ssh", "-T", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", alias, "python3", "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=os.name != "nt",
        )
    except OSError as exc:
        raise TransportError("approved SSH file observation is unreachable") from exc
    expired = threading.Event()
    error = bytearray()

    def kill() -> None:
        if process.poll() is None:
            with suppress(ProcessLookupError):
                if os.name == "nt":
                    process.kill()
                else:
                    os.killpg(process.pid, signal.SIGKILL)

    def expire() -> None:
        expired.set()
        kill()

    def drain_error() -> None:
        for chunk in iter(lambda: process.stderr.read(4096), b""):
            error.extend(chunk)
            del error[:-512]

    timer = threading.Timer(timeout, expire)
    drainer = threading.Thread(target=drain_error, daemon=True)

    def check_exit() -> None:
        process.wait()
        drainer.join()
        if expired.is_set():
            raise TransportError("approved SSH file observation timed out")
        if process.returncode != 0:
            raise TransportError(
                f"approved SSH file observation failed: {error.decode('utf-8', errors='replace').strip()}"
            )

    timer.start()
    drainer.start()
    try:
        process.stdin.write(source.encode())
        process.stdin.close()
        with io.TextIOWrapper(
            process.stdout,
            encoding="utf-8-sig",
            newline="",
        ) as lines:
            yield lines
            # A parser may return early after handling a parse error. Drain the rest
            # so SSH cannot block on a full stdout pipe while we wait for its exit.
            while lines.read(64 * 1024):
                pass
            check_exit()
    except OSError as exc:
        raise TransportError("approved SSH file observation is unreachable") from exc
    finally:
        timer.cancel()
        kill()
        process.wait()
        drainer.join()
        with suppress(OSError):
            process.stdin.close()
        process.stdout.close()
        process.stderr.close()


def _upload(
    remote: dict[str, Any],
    source: str,
    destination: str,
    *,
    expected_bytes: int = 0,
    transfer: Callable[[subprocess.Popen[str] | None], None] | None = None,
) -> None:
    alias = remote["host_access"]["alias"]
    if effective_access(alias) != remote["host_access"]:
        raise ValueError("approved SSH access changed before file transfer")
    process = subprocess.Popen(
        ["scp", "-p", "-q", "-o", "BatchMode=yes", source, f"{alias}:{destination}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        if transfer is not None:
            transfer(process)
        _, error = process.communicate(timeout=120 + expected_bytes // (1024 * 1024))
    except subprocess.TimeoutExpired as exc:
        process.kill()
        process.wait()
        raise ValueError("approved SSH file transfer timed out") from exc
    except Exception:
        if process.poll() is None:
            process.kill()
            process.wait()
        raise
    finally:
        if transfer is not None:
            transfer(None)
    if process.returncode != 0:
        detail = f"approved SSH file transfer failed: {error.strip()}"
        if process.returncode == 255:
            raise TransportError(detail)
        raise ValueError(detail)


def stage(
    plan: dict[str, Any],
    local_run_dir: Path,
    *,
    checkpoint: Callable[[], None],
    transfer: Callable[[subprocess.Popen[str] | None], None],
) -> None:
    """Stage only approved, digest-bound files before controller launch."""
    remote = plan["request"]["remote"]
    staged = remote["staged_files"]
    for item in staged:
        if "source" in item:
            source = Path(item["source"])
            if source.is_symlink() or file_identity(source) != (item["bytes"], item["sha256"]):
                raise ValueError("approved workflow input changed before remote staging")
    approved_plan = local_run_dir / "workflow" / "approved_plan.json"
    generated = [
        {"destination": item["destination"], "content": item["content"]}
        for item in staged
        if "content" in item
    ]
    generated.append(
        {
            "destination": f"{remote['run_dir']}/workflow/approved_plan.json",
            "content": approved_plan.read_text(encoding="utf-8"),
        }
    )
    _invoke(
        remote,
        "prepare",
        destinations=[item["destination"] for item in staged],
        generated=generated,
    )
    checkpoint()
    for item in staged:
        if "source" not in item:
            continue
        source = Path(item["source"])
        if source.is_symlink() or file_identity(source) != (item["bytes"], item["sha256"]):
            raise ValueError("approved workflow input changed before remote staging")
        _upload(
            remote,
            str(source),
            item["destination"],
            expected_bytes=item["bytes"],
            transfer=transfer,
        )
        checkpoint()
    _invoke(
        remote,
        "verify",
        files=[
            {"destination": item["destination"], "bytes": item["bytes"], "sha256": item["sha256"]}
            for item in staged
        ],
        timeout=30 + sum(item["bytes"] for item in staged) // (1024 * 1024),
    )


def launch(plan: dict[str, Any], inputs: dict[str, str] | None = None) -> dict[str, Any]:
    """Detach one controller using its exact native-approved argv."""
    effects = plan["effects"]
    relative_log = Path(effects["launch_log"]).relative_to(effects["run_dir"]).as_posix()
    argv = plan["command_argv"]
    if plan.get("preparation") is not None or inputs:
        # Read the staged audit file to keep generated preparation content out of argv.
        plan_path = f"{effects['run_dir']}/workflow/approved_plan.json"
        digest = sha256_hex(json.dumps(plan, sort_keys=True).encode())
        argv = [
            "python3",
            "-c",
            f"{_INPUT_PROGRAM}\nrun({plan_path!r}, {digest!r}, {inputs or {}!r})\n",
        ]
    return _invoke(plan["request"]["remote"], "launch", argv=argv, log_path=relative_log)


def identity(remote: dict[str, Any], pid: int | None = None) -> dict[str, Any]:
    """Recover the exact detached controller identity recorded on the remote host."""
    return _invoke(remote, "identity", **({"pid": pid} if pid is not None else {}))


def status(remote: dict[str, Any], identity: dict[str, Any]) -> dict[str, Any]:
    """Read the exact remote controller's process identity or terminal receipt."""
    return _invoke(remote, "status", identity=identity)


def stop(remote: dict[str, Any], identity: dict[str, Any]) -> None:
    """Signal only the approved remote controller after process identity verification."""
    _invoke(remote, "stop", identity=identity)
