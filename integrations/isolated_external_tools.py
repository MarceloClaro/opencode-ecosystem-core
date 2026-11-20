"""SPEC-935-R1232: isolated adapters and curated references for external tools.

The default operations are metadata/status/plan only. Install and process launch
are explicit; the process runner is restricted to version/help probes and uses a
private HOME, fixed argv, no shell, and bounded output. No third-party MCP is
registered here.
"""

from __future__ import annotations

import argparse
import base64
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Callable, Mapping, Sequence


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPOSITORY_ROOT / "federation" / "repository-curation-r1232.json"
MAX_TIMEOUT_SECONDS = 600
MAX_OUTPUT_CHARS = 16_384
MAX_PACK_METADATA_CHARS = 8 * 1024 * 1024


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
        adoption = entry.get("adoption")
        if not isinstance(adoption, str) or adoption not in {"isolated_cli", "reference_only", "blocked_legal_review", "selected_skill", "existing_reuse"}:
            errors.append(f"{tool_id}: adoption inválido ou ausente")
            adoption = None
        source = entry.get("source")
        if not isinstance(source, Mapping) or not isinstance(source.get("url"), str) or not source["url"].startswith("https://"):
            errors.append(f"{tool_id}: origem URL ausente")
            source = {}
        commit = source.get("commit")
        if commit is not None and (not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit)):
            errors.append(f"{tool_id}: commit deve ser SHA hexadecimal de 40 caracteres")
        if adoption == "isolated_cli":
            if not isinstance(source.get("version"), str) or not source.get("version"):
                errors.append(f"{tool_id}: versão fixa ausente para CLI isolada")
            if tool_id in {"rust-anything", "caveman"}:
                package = source.get("package")
                integrity = source.get("integrity")
                if not isinstance(package, str) or not package.endswith("@" + str(source.get("version"))):
                    errors.append(f"{tool_id}: pacote npm deve fixar a versão exata")
                if not isinstance(integrity, str) or not integrity.startswith("sha512-"):
                    errors.append(f"{tool_id}: SRI SHA-512 ausente para pacote npm")
            if tool_id == "rust-anything" and (
                isinstance(source.get("unpacked_bytes"), bool)
                or not isinstance(source.get("unpacked_bytes"), int)
                or source["unpacked_bytes"] <= 0
            ):
                errors.append("rust-anything: tamanho desempacotado não positivo ou ausente")
        if adoption == "selected_skill":
            if not all(isinstance(source.get(key), str) and source.get(key) for key in ("path", "upstream_git_blob_sha", "license_git_blob_sha")):
                errors.append(f"{tool_id}: proveniência da skill incompleta")
            if source.get("license") != "Apache-2.0" or source.get("license_file") != "LICENSE.txt":
                errors.append(f"{tool_id}: licença da skill não reconciliada")
            if not re.fullmatch(r"[0-9a-f]{64}", str(source.get("imported_skill_sha256", ""))):
                errors.append(f"{tool_id}: SHA-256 da skill importada inválido")
        if not isinstance(entry.get("license"), Mapping):
            errors.append(f"{tool_id}: proveniência de licença ausente")
        license_status = entry.get("license_status")
        if not isinstance(license_status, str) or license_status not in {"source_declared_unreviewed", "human_review_required"}:
            errors.append(f"{tool_id}: license_status inválido ou ausente")
        integration_status = entry.get("integration_status")
        if not isinstance(integration_status, str) or integration_status not in {"planned_isolated", "installed_isolated", "reference_only", "blocked_legal_review", "imported_explicit_only", "existing_reuse"}:
            errors.append(f"{tool_id}: integration_status inválido ou ausente")
            integration_status = None
        if adoption == "reference_only" and integration_status != "reference_only":
            errors.append(f"{tool_id}: estado reference_only inconsistente")
        if adoption == "blocked_legal_review" and (
            integration_status != "blocked_legal_review" or license_status != "human_review_required"
        ):
            errors.append(f"{tool_id}: bloqueio legal deve permanecer fail-closed")
        if adoption == "selected_skill" and integration_status != "imported_explicit_only":
            errors.append(f"{tool_id}: skill selecionada deve permanecer explicit-only")
        if adoption == "existing_reuse" and integration_status != "existing_reuse":
            errors.append(f"{tool_id}: integração existente deve ser marcada como reutilizada")
        runtime = entry.get("runtime")
        if not isinstance(runtime, Mapping):
            errors.append(f"{tool_id}: runtime ausente")
            continue
        for key in ("installed", "executed", "enabled", "mcp_enabled"):
            if not isinstance(runtime.get(key), bool):
                errors.append(f"{tool_id}: runtime.{key} deve ser booleano")
        if adoption in {"reference_only", "blocked_legal_review"}:
            if runtime.get("installed") or runtime.get("executed") or runtime.get("enabled") or runtime.get("mcp_enabled"):
                errors.append(f"{tool_id}: fonte {adoption} não pode alegar instalação/execução/ativação")
        if adoption == "isolated_cli":
            if integration_status == "planned_isolated":
                if runtime.get("installed") or entry.get("installation_observation") is not None:
                    errors.append(f"{tool_id}: plano não pode alegar instalação observada")
            elif integration_status == "installed_isolated":
                observation = entry.get("installation_observation")
                if not runtime.get("installed") or runtime.get("executed") or runtime.get("enabled") or runtime.get("mcp_enabled"):
                    errors.append(f"{tool_id}: estado instalado deve manter execução/ativação/MCP desligados")
                if not isinstance(observation, Mapping):
                    errors.append(f"{tool_id}: instalação observada sem recibo")
                else:
                    if observation.get("status") != "installed" or observation.get("returncode") != 0:
                        errors.append(f"{tool_id}: recibo de instalação sem sucesso observado")
                    if observation.get("target_executed") is not False or observation.get("mcp_enabled") is not False:
                        errors.append(f"{tool_id}: recibo não pode alegar execução do alvo ou ativação MCP")
                    if not isinstance(observation.get("observed_at"), str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", observation["observed_at"]):
                        errors.append(f"{tool_id}: timestamp de instalação inválido")
                    if not isinstance(observation.get("target"), str) or not observation["target"].startswith("~/.local/share/opencode-core/external-tools/r1232/"):
                        errors.append(f"{tool_id}: prefixo de instalação fora do destino isolado")
                    if tool_id in {"rust-anything", "caveman"} and observation.get("integrity_verified") is not True:
                        errors.append(f"{tool_id}: SRI do pacote não foi observado/verificado")
                    if tool_id in {"rust-anything", "caveman"} and (
                        not isinstance(observation.get("durable_tarball"), str)
                        or not observation["durable_tarball"].startswith("verified-packages/")
                        or not observation["durable_tarball"].endswith(".tgz")
                    ):
                        errors.append(f"{tool_id}: tarball verificado não foi retido no prefixo isolado")
                    if tool_id == "rust-anything" and observation.get("unpacked_size_verified") is not True:
                        errors.append("rust-anything: tamanho desempacotado não foi verificado")
                    if tool_id == "universal-os" and (
                        observation.get("source_commit") != source.get("commit")
                        or observation.get("source_commit_observed_in_direct_url") is not True
                    ):
                        errors.append("universal-os: commit instalado diverge do pin ou não foi observado")
            else:
                errors.append(f"{tool_id}: CLI isolada exige estado planejado ou instalado isoladamente")
        elif entry.get("installation_observation") is not None:
            errors.append(f"{tool_id}: observação de instalação não é válida para esta política de adoção")
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


def _is_managed_npm_install(tool_id: str, target: Path) -> bool:
    """Allow a safe repair only when the prefix contains the exact pinned package."""
    if tool_id not in {"rust-anything", "caveman"} or target.is_symlink():
        return False
    item = _entry(tool_id)
    package_spec = item["source"]["package"]
    package_name, _, version = package_spec.rpartition("@")
    package_dir = target / "node_modules" / Path(*package_name.split("/"))
    root_manifest = target / "package.json"
    installed_manifest = package_dir / "package.json"
    try:
        if any(path.is_symlink() or not path.is_file() for path in (root_manifest, installed_manifest)):
            return False
        root_data = json.loads(root_manifest.read_text(encoding="utf-8"))
        package_data = json.loads(installed_manifest.read_text(encoding="utf-8"))
        dependencies = root_data.get("dependencies")
        return (
            isinstance(dependencies, Mapping)
            and set(dependencies) == {package_name}
            and isinstance(dependencies[package_name], str)
            and dependencies[package_name].startswith("file:")
            and package_data.get("name") == package_name
            and package_data.get("version") == version
        )
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return False


def status() -> dict[str, Any]:
    """Report checked-in policy plus isolated executable presence only."""
    manifest = load_manifest()
    root = default_install_root()
    rows = []
    for item in manifest["repositories"]:
        row = {
            "id": item["id"],
            "adoption": item["adoption"],
            "license_status": item["license_status"],
            "integration_status": item["integration_status"],
            "runtime": dict(item["runtime"]),
        }
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
            npm, "pack", "--json", "--ignore-scripts", "--pack-destination",
            str(base / f".{tool_id}-verified-staging"), package,
        ]
        cache = base / "npm-cache"
        environment = isolated_environment(tool_id, base)
        environment["npm_config_cache"] = str(cache)
        environment["npm_config_ignore_scripts"] = "true"
        integrity = item["source"].get("integrity")
    elif tool_id == "universal-os":
        uv = shutil.which("uv") or "uv"
        source = f"git+{item['source']['url']}@{item['source']['commit']}"
        argv = [uv, "tool", "install", "--from", source, "universal-os"]
        environment = isolated_environment(tool_id, base)
        environment["UV_CACHE_DIR"] = str(base / "uv-cache")
        environment["UV_TOOL_DIR"] = str(target / "tools")
        environment["UV_TOOL_BIN_DIR"] = str(target / "bin")
        integrity = None
    else:  # pragma: no cover - guarded by manifest/adoption contract
        raise ValueError(f"Sem instalador isolado suportado: {tool_id}")
    return {
        "tool_id": tool_id,
        "argv": argv,
        "cwd": str(target),
        "environment": environment,
        "target": str(target),
        "root": str(base),
        "integrity": integrity,
        "unpacked_bytes": item["source"].get("unpacked_bytes"),
        "integrity_verification": {
            "required": tool_id in {"rust-anything", "caveman"},
            "method": "npm pack SRI metadata and local tarball SHA-512, both compared before install; Rust Anything also checks unpacked size"
            if tool_id in {"rust-anything", "caveman"} else "git source pinned to full commit SHA",
            "before_install": True,
        },
        "unpacked_size_verification": {
            "required": tool_id == "rust-anything",
            "expected_bytes": item["source"].get("unpacked_bytes"),
            "before_install": True,
        },
        "install_argv_template": (
            [
                shutil.which("npm") or "npm", "install", "--prefix", str(target), "--ignore-scripts",
                "--no-audit", "--no-fund", "--save-exact", "<verified-tarball>",
            ] if tool_id in {"rust-anything", "caveman"} else None
        ),
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
    if tool_id in {"rust-anything", "caveman"}:
        env.update({
            "npm_config_userconfig": str(private_home / ".npmrc"),
            "npm_config_globalconfig": str(private_home / "global.npmrc"),
            "npm_config_registry": "https://registry.npmjs.org/",
            "npm_config_audit": "false",
            "npm_config_fund": "false",
            "npm_config_update_notifier": "false",
            "npm_config_ignore_scripts": "true",
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
    base = Path(plan["root"])
    target = Path(plan["target"])
    managed_npm_prefix = _is_managed_npm_install(tool_id, target)
    if target.is_symlink() or (target.exists() and (not target.is_dir() or (any(target.iterdir()) and not managed_npm_prefix))):
        return {**plan, "dry_run": False, "status": "target_not_empty", "stderr": "O destino existe e não está vazio; nenhuma instalação foi iniciada."}
    invoke = runner or subprocess.run

    def run_command(argv: Sequence[str], cwd: Path, env: Mapping[str, str]) -> Any:
        return invoke(
            list(argv),
            cwd=str(cwd),
            env=dict(env),
            shell=False,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )

    if tool_id in {"rust-anything", "caveman"}:
        base.mkdir(parents=True, exist_ok=True)
        try:
            with tempfile.TemporaryDirectory(prefix=f".{tool_id}-verified-", dir=str(base)) as scratch:
                staging = Path(scratch).resolve()
                pack_argv = list(plan["argv"])
                pack_argv[pack_argv.index("--pack-destination") + 1] = str(staging)
                packed = run_command(pack_argv, staging, plan["environment"])
                packed_code = int(getattr(packed, "returncode", 1))
                packed_stdout_raw = str(getattr(packed, "stdout", "") or "")
                packed_stdout = packed_stdout_raw[:MAX_OUTPUT_CHARS]
                packed_stderr = str(getattr(packed, "stderr", "") or "")[:MAX_OUTPUT_CHARS]
                if packed_code != 0:
                    return {**plan, "dry_run": False, "status": "pack_failed", "returncode": packed_code, "stdout": packed_stdout, "stderr": packed_stderr}
                if len(packed_stdout_raw) > MAX_PACK_METADATA_CHARS:
                    return {**plan, "dry_run": False, "status": "pack_metadata_too_large", "stderr": "A saída JSON de npm pack excedeu o limite de segurança."}
                try:
                    metadata = json.loads(packed_stdout_raw)
                    record = metadata[0] if isinstance(metadata, list) and metadata else metadata
                    filename = record.get("filename") if isinstance(record, Mapping) else None
                    reported_integrity = record.get("integrity") if isinstance(record, Mapping) else None
                except (json.JSONDecodeError, TypeError, IndexError):
                    return {**plan, "dry_run": False, "status": "pack_metadata_invalid", "stdout": packed_stdout, "stderr": packed_stderr}
                if (not isinstance(filename, str) or Path(filename).name != filename
                        or "\\" in filename or filename in {"", ".", ".."}):
                    return {**plan, "dry_run": False, "status": "pack_metadata_invalid", "stdout": packed_stdout, "stderr": "Nome do tarball inválido."}
                tarball = staging / filename
                if not tarball.is_file() or tarball.is_symlink():
                    return {**plan, "dry_run": False, "status": "pack_artifact_missing", "stdout": packed_stdout, "stderr": "npm pack não produziu um tarball regular no staging isolado."}
                actual_integrity = _sha512_sri(tarball)
                expected_integrity = plan["integrity"]
                if reported_integrity != expected_integrity or actual_integrity != expected_integrity:
                    return {
                        **plan,
                        "dry_run": False,
                        "status": "integrity_mismatch",
                        "expected_integrity": expected_integrity,
                        "reported_integrity": reported_integrity,
                        "actual_integrity": actual_integrity,
                        "stdout": packed_stdout,
                        "stderr": "Pacote obtido não corresponde ao SRI fixado; instalação bloqueada.",
                    }
                expected_unpacked_bytes = plan.get("unpacked_bytes")
                reported_unpacked_bytes = record.get("unpackedSize") if isinstance(record, Mapping) else None
                unpacked_size_verified = None
                if expected_unpacked_bytes is not None:
                    unpacked_size_verified = (
                        isinstance(reported_unpacked_bytes, int)
                        and not isinstance(reported_unpacked_bytes, bool)
                        and reported_unpacked_bytes == expected_unpacked_bytes
                    )
                    if not unpacked_size_verified:
                        return {
                            **plan,
                            "dry_run": False,
                            "status": "unpacked_size_mismatch",
                            "expected_unpacked_bytes": expected_unpacked_bytes,
                            "reported_unpacked_bytes": reported_unpacked_bytes,
                            "integrity_verified": True,
                            "stdout": packed_stdout,
                            "stderr": "Tamanho desempacotado diverge do valor fixado; instalação bloqueada.",
                        }
                target.mkdir(parents=True, exist_ok=True)
                verified_dir = target / "verified-packages"
                if verified_dir.is_symlink() or (verified_dir.exists() and not verified_dir.is_dir()):
                    return {**plan, "dry_run": False, "status": "verified_package_path_conflict", "stderr": "Destino persistente do tarball não é um diretório regular."}
                verified_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
                durable_tarball = verified_dir / filename
                if durable_tarball.is_symlink() or (durable_tarball.exists() and not durable_tarball.is_file()):
                    return {**plan, "dry_run": False, "status": "verified_package_path_conflict", "stderr": "Tarball persistente existente não é um arquivo regular."}
                if durable_tarball.exists():
                    if _sha512_sri(durable_tarball) != expected_integrity:
                        return {**plan, "dry_run": False, "status": "verified_package_conflict", "stderr": "Tarball persistente existente diverge do SRI fixado."}
                else:
                    fd, temporary_copy_name = tempfile.mkstemp(prefix=".verified-", dir=str(verified_dir))
                    temporary_copy = Path(temporary_copy_name)
                    try:
                        with os.fdopen(fd, "wb") as copied, tarball.open("rb") as source_stream:
                            shutil.copyfileobj(source_stream, copied)
                        os.chmod(temporary_copy, 0o600)
                        if _sha512_sri(temporary_copy) != expected_integrity:
                            return {**plan, "dry_run": False, "status": "verified_copy_mismatch", "stderr": "Cópia persistente do tarball divergiu do SRI; instalação bloqueada."}
                        os.replace(temporary_copy, durable_tarball)
                    finally:
                        temporary_copy.unlink(missing_ok=True)
                install_argv = [
                    shutil.which("npm") or "npm", "install", "--prefix", str(target), "--ignore-scripts",
                    "--no-audit", "--no-fund", "--save-exact", str(durable_tarball),
                ]
                installed = run_command(install_argv, target, plan["environment"])
                code = int(getattr(installed, "returncode", 1))
                return {
                    **plan,
                    "argv": install_argv,
                    "dry_run": False,
                    "status": "installed" if code == 0 else "install_failed",
                    "returncode": code,
                    "integrity_verified": True,
                    "unpacked_size_verified": unpacked_size_verified,
                    "stdout": str(getattr(installed, "stdout", "") or "")[:MAX_OUTPUT_CHARS],
                    "stderr": str(getattr(installed, "stderr", "") or "")[:MAX_OUTPUT_CHARS],
                }
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {**plan, "dry_run": False, "status": "install_error", "stderr": str(exc)[:MAX_OUTPUT_CHARS]}

    base.mkdir(parents=True, exist_ok=True)
    target.mkdir(parents=True, exist_ok=True)
    try:
        completed = run_command(plan["argv"], target, plan["environment"])
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


def _sha512_sri(path: Path) -> str:
    """Hash a packed package incrementally using npm's SRI representation."""
    digest = hashlib.sha512()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha512-" + base64.b64encode(digest.digest()).decode("ascii")


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
