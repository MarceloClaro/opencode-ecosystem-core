"""SPEC-935-R1232: isolated adapters and curated references for external tools.

The default operations are metadata/status/plan only. Install and process launch
are explicit; the process runner is restricted to version/help probes and uses a
private HOME, fixed argv, no shell, and bounded output. No third-party MCP is
registered here.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any, Callable, Mapping, Sequence


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPOSITORY_ROOT / "federation" / "repository-curation-r1232.json"
MAX_TIMEOUT_SECONDS = 600
MAX_OUTPUT_CHARS = 16_384


class UnsafeInvocationError(ValueError):
    """The request exceeds this integration's deliberately narrow safe surface."""


@dataclass(frozen=True)
class CompletedResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""


Runner = Callable[..., Any]


def load_manifest(path: Path | str = MANIFEST_PATH) -> dict[str, Any]:
    """Load the checked-in provenance manifest without network or execution."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    errors = validate_manifest(data)
    if errors:
        raise ValueError("Manifest R1232 inválido: " + "; ".join(errors))
    return data


def validate_manifest(data: Mapping[str, Any]) -> list[str]:
    """Return deterministic structural/policy errors; never probes a tool."""
    errors: list[str] = []
    if data.get("schema_version") != "r1232.v1":
        errors.append("schema_version deve ser r1232.v1")
    entries = data.get("repositories")
    if not isinstance(entries, list):
        return errors + ["repositories deve ser uma lista"]
    seen: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, Mapping):
            errors.append(f"repositories[{index}] deve ser objeto")
            continue
        tool_id = entry.get("id")
        if not isinstance(tool_id, str) or not tool_id:
            errors.append(f"repositories[{index}].id ausente")
            continue
        if tool_id in seen:
            errors.append(f"id duplicado: {tool_id}")
        seen.add(tool_id)
        if not isinstance(entry.get("source"), Mapping) or not entry["source"].get("url"):
            errors.append(f"{tool_id}: origem URL ausente")
        if not isinstance(entry.get("license"), Mapping):
            errors.append(f"{tool_id}: proveniência de licença ausente")
        runtime = entry.get("runtime")
        if not isinstance(runtime, Mapping):
            errors.append(f"{tool_id}: runtime ausente")
            continue
        for key in ("installed", "executed", "enabled", "mcp_enabled"):
            if not isinstance(runtime.get(key), bool):
                errors.append(f"{tool_id}: runtime.{key} deve ser booleano")
        adoption = entry.get("adoption")
        if adoption in {"reference_only", "blocked_legal_review"}:
            if runtime.get("installed") or runtime.get("executed") or runtime.get("enabled") or runtime.get("mcp_enabled"):
                errors.append(f"{tool_id}: fonte {adoption} não pode alegar instalação/execução/ativação")
        if adoption != "existing_reuse" and runtime.get("mcp_enabled"):
            errors.append(f"{tool_id}: MCP externo não pode estar habilitado por esta integração")
        if entry.get("mcp_config") is not None:
            errors.append(f"{tool_id}: configuração MCP não é aceita no manifesto")
    return errors


def _entry(tool_id: str) -> dict[str, Any]:
    for entry in load_manifest()["repositories"]:
        if entry["id"] == tool_id:
            return entry
    raise ValueError(f"Ferramenta não registrada em R1232: {tool_id}")


def status() -> dict[str, Any]:
    """Report checked-in policy plus isolated executable presence only."""
    manifest = load_manifest()
    root = default_install_root()
    rows = []
    for item in manifest["repositories"]:
        row = {"id": item["id"], "adoption": item["adoption"], "runtime": dict(item["runtime"])}
        if item["id"] in {"rust-anything", "universal-os", "caveman"}:
            executable = executable_path(item["id"], root)
            row["isolated_executable_present"] = executable.is_file() if executable else False
            row["isolated_executable"] = str(executable) if executable and executable.is_file() else None
        rows.append(row)
    return {"spec_id": "SPEC-935-R1232", "verification": "local_inventory_only", "repositories": rows}


def default_install_root() -> Path:
    return Path.home() / ".local" / "share" / "opencode-core" / "external-tools" / "r1232"


def install_plan(tool_id: str, root: Path | str | None = None) -> dict[str, Any]:
    """Prepare a pinned isolated installation command; does not execute it."""
    item = _entry(tool_id)
    if item["adoption"] != "isolated_cli":
        raise ValueError(f"{tool_id} não tem política de instalação isolada")
    base = Path(root or default_install_root()).expanduser().resolve()
    target = base / tool_id
    if tool_id in {"rust-anything", "caveman"}:
        package = item["source"]["package"]
        npm = shutil.which("npm") or "npm"
        argv = [
            npm, "install", "--prefix", str(target), "--ignore-scripts", "--no-audit",
            "--no-fund", "--save-exact", package,
        ]
        cache = base / "npm-cache"
        environment = isolated_environment(tool_id, base)
        environment["npm_config_cache"] = str(cache)
        integrity = item["source"].get("integrity")
    elif tool_id == "universal-os":
        uv = shutil.which("uv") or "uv"
        source = f"git+{item['source']['url']}@{item['source']['commit']}"
        argv = [
            uv, "tool", "install", "--tool-dir", str(target), "--bin-dir", str(target / "bin"),
            "--from", source, "universal-os",
        ]
        environment = isolated_environment(tool_id, base)
        environment["UV_CACHE_DIR"] = str(base / "uv-cache")
        integrity = None
    else:  # pragma: no cover - guarded by manifest/adoption contract
        raise ValueError(f"Sem instalador isolado suportado: {tool_id}")
    return {
        "tool_id": tool_id,
        "argv": argv,
        "cwd": str(target),
        "environment": environment,
        "target": str(target),
        "integrity": integrity,
        "mcp_enabled": False,
        "dry_run": True,
    }


def isolated_environment(
    tool_id: str,
    root: Path | str | None = None,
    *,
    base_env: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Create a minimal environment; never forwards API/account credentials."""
    base = Path(root or default_install_root()).expanduser().resolve()
    private_home = (base / tool_id / "home").resolve()
    source_env = os.environ if base_env is None else base_env
    allowed = {"PATH", "LANG", "LC_ALL", "LC_CTYPE", "TERM", "TMPDIR", "TEMP", "SYSTEMROOT", "WINDIR"}
    env = {key: value for key, value in source_env.items() if key in allowed and isinstance(value, str)}
    env["HOME"] = str(private_home)
    env["XDG_CONFIG_HOME"] = str(private_home / ".config")
    env["XDG_CACHE_HOME"] = str(private_home / ".cache")
    if tool_id == "caveman":
        env.update({
            "CAVEMAN_HOME": str(private_home),
            "DO_NOT_TRACK": "1",
            "CAVEMAN_TELEMETRY": "0",
            "CAVEMAN_OFFLINE": "1",
        })
    elif tool_id == "universal-os":
        env["UOS_HOME"] = str(private_home)
    return env


def executable_path(tool_id: str, root: Path | str | None = None) -> Path | None:
    """Resolve only known executable locations inside the dedicated prefix."""
    base = Path(root or default_install_root()).expanduser().resolve()
    if tool_id == "rust-anything":
        return base / tool_id / "node_modules" / ".bin" / "rust-anything"
    if tool_id == "caveman":
        return base / tool_id / "node_modules" / ".bin" / "caveman"
    if tool_id == "universal-os":
        return base / tool_id / "bin" / "uos"
    return None


_SAFE_PROBES: dict[str, frozenset[tuple[str, ...]]] = {
    "rust-anything": frozenset({("--version",), ("--help",), ("-h",)}),
    "universal-os": frozenset({("--version",), ("--help",), ("-h",)}),
    "caveman": frozenset({("--version",), ("--help",), ("-h",)}),
}


def run_safe(
    tool_id: str,
    args: Sequence[str],
    root: Path | str | None = None,
    *,
    timeout: float = 15,
    runner: Runner | None = None,
) -> dict[str, Any]:
    """Run only an allowlisted non-target probe from the isolated prefix."""
    if tool_id not in _SAFE_PROBES:
        raise UnsafeInvocationError(f"Ferramenta sem execução permitida nesta spec: {tool_id}")
    if not isinstance(args, (list, tuple)) or any(not isinstance(arg, str) for arg in args):
        raise UnsafeInvocationError("argv deve ser lista de strings")
    if tuple(args) not in _SAFE_PROBES[tool_id]:
        raise UnsafeInvocationError(f"Somente --version/--help são permitidos para {tool_id}")
    if timeout <= 0 or timeout > 30:
        raise UnsafeInvocationError("timeout deve estar entre 0 e 30 segundos")
    executable = executable_path(tool_id, root)
    if executable is None or not executable.is_file():
        return {"ok": False, "tool_id": tool_id, "status": "not_installed_isolated", "stdout": "", "stderr": "CLI ausente no prefixo isolado."}
    prefix = Path(root or default_install_root()).expanduser().resolve()
    resolved = executable.resolve()
    try:
        resolved.relative_to(prefix)
    except ValueError as exc:
        raise UnsafeInvocationError("Executável resolve para fora do prefixo isolado") from exc
    invoke = runner or subprocess.run
    env = isolated_environment(tool_id, prefix)
    try:
        completed = invoke(
            [str(resolved), *args],
            cwd=str(prefix / tool_id),
            env=env,
            shell=False,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        stdout = str(getattr(completed, "stdout", "") or "")[:MAX_OUTPUT_CHARS]
        stderr = str(getattr(completed, "stderr", "") or "")[:MAX_OUTPUT_CHARS]
        return {
            "ok": int(getattr(completed, "returncode", 1)) == 0,
            "tool_id": tool_id,
            "status": "completed" if int(getattr(completed, "returncode", 1)) == 0 else "failed",
            "returncode": int(getattr(completed, "returncode", 1)),
            "command": [str(resolved), *args],
            "stdout": stdout,
            "stderr": stderr,
        }
    except subprocess.TimeoutExpired as exc:
        return {"ok": False, "tool_id": tool_id, "status": "timeout", "stdout": "", "stderr": str(exc)[:MAX_OUTPUT_CHARS]}
    except OSError as exc:
        return {"ok": False, "tool_id": tool_id, "status": "execution_error", "stdout": "", "stderr": str(exc)[:MAX_OUTPUT_CHARS]}


def install_tool(
    tool_id: str,
    *,
    root: Path | str | None = None,
    yes: bool = False,
    runner: Runner | None = None,
    timeout: int = 600,
) -> dict[str, Any]:
    """Execute a pinned install only after explicit ``yes``; otherwise dry-run."""
    plan = install_plan(tool_id, root)
    if not yes:
        return plan
    if timeout <= 0 or timeout > MAX_TIMEOUT_SECONDS:
        raise ValueError(f"timeout deve estar entre 1 e {MAX_TIMEOUT_SECONDS} segundos")
    target = Path(plan["target"])
    target.mkdir(parents=True, exist_ok=True)
    invoke = runner or subprocess.run
    try:
        completed = invoke(
            plan["argv"],
            cwd=str(target),
            env=plan["environment"],
            shell=False,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            **plan,
            "dry_run": False,
            "status": "installed" if getattr(completed, "returncode", 1) == 0 else "install_failed",
            "returncode": int(getattr(completed, "returncode", 1)),
            "stdout": str(getattr(completed, "stdout", "") or "")[:MAX_OUTPUT_CHARS],
            "stderr": str(getattr(completed, "stderr", "") or "")[:MAX_OUTPUT_CHARS],
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {**plan, "dry_run": False, "status": "install_error", "stderr": str(exc)[:MAX_OUTPUT_CHARS]}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ferramentas externas R1232 isoladas")
    sub = parser.add_subparsers(dest="operation", required=True)
    sub.add_parser("status", help="Inventário local read-only")
    plan_parser = sub.add_parser("plan", help="Mostrar comando de instalação, sem executá-lo")
    plan_parser.add_argument("tool_id", choices=("rust-anything", "universal-os", "caveman"))
    plan_parser.add_argument("--root", type=Path)
    install_parser = sub.add_parser("install", help="Instalar em prefixo isolado; exige --yes")
    install_parser.add_argument("tool_id", choices=("rust-anything", "universal-os", "caveman"))
    install_parser.add_argument("--root", type=Path)
    install_parser.add_argument("--yes", action="store_true")
    install_parser.add_argument("--timeout", type=int, default=600)
    probe_parser = sub.add_parser("probe", help="Somente --version/--help no prefixo isolado")
    probe_parser.add_argument("tool_id", choices=("rust-anything", "universal-os", "caveman"))
    probe_parser.add_argument("probe", choices=("--version", "--help"))
    probe_parser.add_argument("--root", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.operation == "status":
            result = status()
        elif args.operation == "plan":
            result = install_plan(args.tool_id, args.root)
        elif args.operation == "install":
            result = install_tool(args.tool_id, root=args.root, yes=args.yes, timeout=args.timeout)
        else:
            result = run_safe(args.tool_id, [args.probe], args.root)
    except (ValueError, UnsafeInvocationError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok", result.get("status") not in {"install_failed", "install_error"}) else 1


if __name__ == "__main__":  # pragma: no cover - CLI smoke tests cover main
    raise SystemExit(main())
