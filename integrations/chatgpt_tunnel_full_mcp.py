"""R1218: túnel ChatGPT com o MCP completo do Core, sob operação explícita.

Este runner não substitui o pacote `tunnel-client`: apenas monta a linha de
comando oficial do binário vendored com `--mcp.command` apontando para
`integrations.ecosystem_mcp`. Nenhuma credencial é lida ou impressa; a chave é
passada por referência `file:` ao control plane.
"""
from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import os
import shlex
import signal
import stat
import subprocess
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TUNNEL_ID = "tunnel_6af9e26d203c8191ab67eb7e9aa3d805"
CORE_DIR = Path(__file__).resolve().parents[1]
STATE_DIR = Path.home() / ".local/state/opencode-core-tunnel-full"
KEY_FILE = Path.home() / ".local/state/opencode-core-tunnel/runtime.key"
BUNDLE = Path(
    "/mnt/c/Users/marce/AppData/Local/OpenCodeEcosystemCore/Tunnel-v0.0.21/vendor/"
    "tunnel-client-runtime-v0.0.21-linux-amd64.zip"
)
BUNDLE_SHA256 = "fa53182b766aeaceb652d86aee291c48daf7b90b5d73586dba370f4c1801325e"
MCP_MODULE = "integrations.ecosystem_mcp"
BASE_ENV = {"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8", "HOME": str(Path.home())}


class UserError(Exception):
    """Erro acionável pelo operador, sem dados sensíveis."""


def build_mcp_command(core_dir: Path | str = CORE_DIR) -> list[str]:
    root = Path(core_dir)
    return [str(root / ".venv/bin/python"), "-B", "-m", MCP_MODULE]


def build_tunnel_argv(
    *,
    binary: Path | str,
    state_dir: Path | str,
    key_file: Path | str,
    mcp_command: list[str],
    tunnel_id: str = TUNNEL_ID,
) -> list[str]:
    state = Path(state_dir)
    return [
        str(binary),
        "run",
        "--control-plane.base-url=https://api.openai.com",
        f"--control-plane.tunnel-id={tunnel_id}",
        f"--control-plane.api-key=file:{Path(key_file)}",
        f"--mcp.command={shlex.join(mcp_command)}",
        "--health.listen-addr=127.0.0.1:0",
        f"--health.url-file={state / 'health-url'}",
        f"--pid.file={state / 'tunnel.pid'}",
        f"--log.file={state / 'tunnel.log'}",
        "--log.level=info",
        "--log.format=struct-text",
        "--log.http-raw-unsafe=false",
        "--tracing.enabled=false",
        "--mcp.oauth-discovery=disabled",
    ]


def _sha256_file(path: Path | str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_private_file(path: Path | str) -> Path:
    target = Path(path)
    try:
        info = target.lstat()
    except OSError:
        raise UserError("Arquivo privado ausente ou inacessível.") from None
    mode = stat.S_IMODE(info.st_mode)
    if (
        not target.is_absolute()
        or not stat.S_ISREG(info.st_mode)
        or info.st_uid != os.getuid()
        or mode != 0o600
    ):
        raise UserError("Use um arquivo privado absoluto, deste usuário, com modo 0600.")
    return target


def validate_core(core_dir: Path | str) -> Path:
    root = Path(core_dir)
    required = (
        root / ".venv/bin/python",
        root / "integrations/ecosystem_mcp.py",
    )
    if not root.is_absolute() or not all(p.is_file() for p in required):
        raise UserError("Confira a raiz do Core, a .venv e o módulo integrations.ecosystem_mcp.")
    return root


def extract_runtime(
    bundle: Path | str,
    state_dir: Path | str,
    expected_sha: str = BUNDLE_SHA256,
) -> Path:
    source = Path(bundle)
    state = Path(state_dir)
    state.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(state, 0o700)
    if _sha256_file(source) != expected_sha:
        raise UserError("SHA-256 do bundle oficial diverge; extração abortada.")
    with zipfile.ZipFile(source) as archive:
        payload = archive.read("tunnel-client-runtime")
    target = state / "tunnel-client-runtime"
    if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() == hashlib.sha256(payload).hexdigest():
        os.chmod(target, 0o700)
        return target
    temporary = state / ".tunnel-client-runtime.tmp"
    with open(temporary, "xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    os.chmod(temporary, 0o700)
    os.replace(temporary, target)
    return target


def record(state_dir: Path | str, event: str, fields: dict[str, Any]) -> None:
    state = Path(state_dir)
    state.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = state / "eventos.jsonl"
    flags = os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK
    fd = os.open(path, flags, 0o600)
    value = {
        "hora_utc": datetime.now(timezone.utc).isoformat(),
        "evento": event,
        **fields,
    }
    with os.fdopen(fd, "a", encoding="utf-8") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o600:
            raise UserError("Registro de eventos precisa ser arquivo privado 0600.")
        stream.write(json.dumps(value, ensure_ascii=True, separators=(",", ":")) + "\n")


def _pid(state_dir: Path | str) -> int | None:
    path = Path(state_dir) / "tunnel.pid"
    try:
        value = int(path.read_text(encoding="ascii").strip())
    except (OSError, TypeError, ValueError):
        return None
    return value if value > 1 else None


def _proc_cmdline(pid: int) -> list[bytes]:
    try:
        raw = (Path("/proc") / str(pid) / "cmdline").read_bytes()
    except OSError:
        return []
    return [part for part in raw.split(b"\0") if part]


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _fetch(base: str, path: str, *, json_body: bool = False) -> Any:
    try:
        port = int(base.rsplit(":", 1)[1])
    except (AttributeError, IndexError, ValueError):
        return {} if json_body else None
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
    try:
        connection.request("GET", path)
        response = connection.getresponse()
        if not json_body:
            return response.status
        body = response.read(65_537)
        if len(body) <= 65_536:
            value = json.loads(body)
            return value if isinstance(value, dict) else {}
    except (OSError, ValueError, http.client.HTTPException, RecursionError):
        pass
    finally:
        connection.close()
    return {} if json_body else None


def status(state_dir: Path | str = STATE_DIR) -> dict[str, Any]:
    state = Path(state_dir)
    pid = _pid(state)
    result: dict[str, Any] = {"tunel": "parado", "mcp": MCP_MODULE}
    if pid is None or not _alive(pid):
        return result
    result["pid"] = pid
    health_file = state / "health-url"
    try:
        base = health_file.read_text(encoding="ascii")[:120].strip()
    except OSError:
        return {**result, "tunel": "aguardando_listener"}
    if not base.startswith("http://127.0.0.1:"):
        return {**result, "tunel": "aguardando_listener"}
    ready = _fetch(base, "/readyz") == 200
    health = _fetch(base, "/health/control-plane", json_body=True)
    details = health.get("details") if isinstance(health.get("details"), dict) else {}
    # v0.0.21 passou a publicar `observed_at`; versões anteriores usavam
    # `last_success`. Ambos indicam o último poll observado com sucesso.
    last_success = details.get("last_success") or details.get("observed_at")
    recent = False
    if isinstance(last_success, str):
        try:
            observed = datetime.fromisoformat(last_success)
            now = datetime.now(timezone.utc)
            recent = now - __import__("datetime").timedelta(seconds=120) <= observed <= now
        except (TypeError, ValueError):
            recent = False
    if ready and recent and details.get("consecutive_failures", 0) == 0:
        return {**result, "tunel": "polling_confirmado", "ultimo_poll_utc": last_success}
    outcome = {**result, "tunel": "aguardando_polling", "readyz": ready}
    http_status = details.get("http_status")
    if type(http_status) is int and 100 <= http_status <= 599:
        outcome["http"] = http_status
    return outcome


def stop(state_dir: Path | str = STATE_DIR) -> dict[str, Any]:
    state = Path(state_dir)
    pid = _pid(state)
    if pid is None:
        return {"tunel": "parado", "mcp": MCP_MODULE}
    cmdline = _proc_cmdline(pid)
    joined = b" ".join(cmdline)
    if TUNNEL_ID.encode() not in joined or b"tunnel-client-runtime" not in joined:
        raise UserError("PID registrado não pertence ao túnel gerenciado; nada foi encerrado.")
    os.kill(pid, signal.SIGTERM)
    deadline = time.monotonic() + 6
    while time.monotonic() < deadline and _alive(pid):
        time.sleep(0.1)
    if _alive(pid):
        os.kill(pid, signal.SIGKILL)
    (state / "tunnel.pid").unlink(missing_ok=True)
    (state / "health-url").unlink(missing_ok=True)
    record(state, "tunel_encerrado", {"pid": pid})
    return {"tunel": "parado", "mcp": MCP_MODULE, "pid_encerrado": pid}


def plan(args: argparse.Namespace) -> int:
    root = validate_core(args.core_dir)
    key_ref = f"file:{Path(args.key_file)}"
    binary = Path(args.state_dir) / "tunnel-client-runtime"
    mcp_command = build_mcp_command(root)
    argv = build_tunnel_argv(
        binary=binary,
        state_dir=args.state_dir,
        key_file=args.key_file,
        mcp_command=mcp_command,
    )
    print(json.dumps({
        "acao": "plan",
        "tunnel_id": TUNNEL_ID,
        "mcp": MCP_MODULE,
        "mcp_command": mcp_command,
        "key_reference": key_ref,
        "argv": argv,
        "efeitos": "nenhum processo iniciado; nenhuma rede aberta; chave não lida",
        "seguinte": "use start --confirm para executar",
    }, ensure_ascii=False, indent=2))
    return 0


def start(args: argparse.Namespace) -> int:
    if not args.confirm:
        print("start exige --confirm; nada foi iniciado.", file=sys.stderr)
        return 2
    root = validate_core(args.core_dir)
    validate_private_file(args.key_file)
    binary = extract_runtime(args.bundle, args.state_dir, BUNDLE_SHA256)
    mcp_command = build_mcp_command(root)
    argv = build_tunnel_argv(
        binary=binary,
        state_dir=args.state_dir,
        key_file=args.key_file,
        mcp_command=mcp_command,
    )
    current = status(args.state_dir)
    if current.get("pid") is not None and current.get("tunel") != "parado":
        raise UserError("Já há túnel gerenciado ativo; use status/stop antes de reiniciar.")
    flags = os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW
    fd = os.open(args.state_dir / "tunnel.log", flags, 0o600)
    process = subprocess.Popen(
        argv,
        cwd=root,
        env=BASE_ENV,
        stdin=subprocess.DEVNULL,
        stdout=fd,
        stderr=fd,
        start_new_session=True,
    )
    os.close(fd)
    (args.state_dir / "tunnel.pid").write_text(f"{process.pid}\n", encoding="ascii")
    os.chmod(args.state_dir / "tunnel.pid", 0o600)
    record(args.state_dir, "tunnel_iniciado", {
        "pid": process.pid,
        "mcp": MCP_MODULE,
        "tunnel_id": TUNNEL_ID,
        "modo": "mcp_completo_risco_aceito",
    })
    deadline = time.monotonic() + 30
    outcome = status(args.state_dir)
    while time.monotonic() < deadline and outcome.get("tunel") == "aguardando_listener":
        time.sleep(0.5)
        outcome = status(args.state_dir)
    print(json.dumps(outcome, ensure_ascii=False, indent=2))
    return 0 if outcome.get("tunel") == "polling_confirmado" else 1


def _parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--state-dir", type=Path, default=STATE_DIR)
    common.add_argument("--core-dir", type=Path, default=CORE_DIR)
    common.add_argument("--key-file", type=Path, default=KEY_FILE)
    common.add_argument("--bundle", type=Path, default=BUNDLE)
    parser = argparse.ArgumentParser(description=__doc__, parents=[common])
    sub = parser.add_subparsers(dest="action")
    sub.add_parser("status", parents=[common])
    sub.add_parser("plan", parents=[common])
    start_parser = sub.add_parser("start", parents=[common])
    start_parser.add_argument("--confirm", action="store_true")
    sub.add_parser("stop", parents=[common])
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.action == "status":
            print(json.dumps(status(args.state_dir), ensure_ascii=False, indent=2))
            return 0
        if args.action == "start":
            return start(args)
        if args.action == "stop":
            print(json.dumps(stop(args.state_dir), ensure_ascii=False, indent=2))
            return 0
        return plan(args)
    except UserError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
