"""SPEC-935-R1237: optional OpenReverseLab metadata and MCP-config adapter.

This module never imports or runs the upstream MCP project. It can inspect an
explicit local checkout using fixed, read-only Git commands and emit a disabled
OpenCode configuration candidate to stdout. It does not install dependencies or
write active OpenCode configuration.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 compatibility without a new dependency.
    tomllib = None  # type: ignore[assignment]
from typing import Any, Callable, Mapping, Sequence


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPOSITORY_ROOT / "federation" / "open-reverselab-adapter-r1237.json"
HISTORICAL_MANIFEST_PATH = REPOSITORY_ROOT / "federation" / "repository-curation-r1232.json"
SOURCE_COMMIT = "c42da86aadcbea4f2dd20822653f83da5f6aba54"
SOURCE_URL = "https://github.com/LING71671/open-reverselab"
MCP_RELATIVE = Path("tools/skills/mcp/ReverseLabToolsMCP")
ENTRYPOINT_RELATIVE = MCP_RELATIVE / "reverse_lab_tools_mcp.py"
LOCKFILE_RELATIVE = MCP_RELATIVE / "uv.lock"
LOCKFILE_BLOB_ID = "30c5bbb363442264d3b0581e33455a791944196b"
INSTALL_RECEIPT_SCHEMA = "open-reverselab-install.r1238.v1"
MAX_GIT_TIMEOUT_SECONDS = 8
MAX_INSTALL_TIMEOUT_SECONDS = 600
MAX_INSTALL_OUTPUT_CHARS = 16_384


class CheckoutValidationError(ValueError):
    """A local checkout failed a deterministic, read-only precondition."""

    def __init__(self, status: str, message: str):
        super().__init__(message)
        self.status = status


Runner = Callable[..., subprocess.CompletedProcess[str]]


def load_manifest() -> dict[str, Any]:
    """Load the Core-owned provenance record; do not consult the network."""
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("O manifesto OpenReverseLab deve ser um objeto JSON.")
    return data


def validate_manifest(data: Mapping[str, Any]) -> list[str]:
    """Return deterministic policy/provenance errors without probing a checkout."""
    errors: list[str] = []
    if data.get("schema_version") != "open-reverselab-adapter.r1237.v1":
        errors.append("schema_version inválido")
    if data.get("spec_id") != "SPEC-935-R1237":
        errors.append("spec_id inválido")

    supersedes = data.get("supersedes")
    if not isinstance(supersedes, Mapping) or (
        supersedes.get("historical_spec") != "SPEC-935-R1232"
        or supersedes.get("historical_status") != "blocked_legal_review"
        or supersedes.get("new_state") != "authorized_optional_adapter"
        or supersedes.get("historical_record_preserved") is not True
    ):
        errors.append("proveniência histórica R1232 não foi preservada")

    source = data.get("source")
    if not isinstance(source, Mapping):
        errors.append("source ausente ou inválido")
        source = {}
    if source.get("repository") != "LING71671/open-reverselab":
        errors.append("repository upstream diverge do pin")
    if source.get("url") != "https://github.com/LING71671/open-reverselab":
        errors.append("url upstream diverge do pin")
    if source.get("commit") != SOURCE_COMMIT:
        errors.append("commit upstream diverge do pin")

    root_license = source.get("root_license")
    if not isinstance(root_license, Mapping) or (
        root_license.get("file") != "LICENSE"
        or root_license.get("declared") != "Apache-2.0"
    ):
        errors.append("root_license deve preservar a declaração Apache-2.0 separadamente")
    nested_mcp = source.get("nested_mcp")
    if not isinstance(nested_mcp, Mapping) or (
        nested_mcp.get("path") != MCP_RELATIVE.as_posix()
        or nested_mcp.get("package") != "reverselab-tools-mcp"
        or nested_mcp.get("version") != "0.1.0"
        or nested_mcp.get("declared") != "GPL-3.0-only"
    ):
        errors.append("nested_mcp deve preservar separadamente GPL-3.0-only e versão 0.1.0")
    disclaimer = source.get("disclaimer")
    if not isinstance(disclaimer, Mapping) or (
        disclaimer.get("path") != "DISCLAIMER.md"
        or disclaimer.get("github_blob") != "025efb705062b5782b826d317388674bfe88a5ff"
        or disclaimer.get("legal_assessment") != "not_performed"
    ):
        errors.append("disclaimer sem proveniência observada ou avaliação jurídica indevida")

    authorization = data.get("authorization")
    if not isinstance(authorization, Mapping):
        errors.append("authorization ausente ou inválida")
        authorization = {}
    if authorization.get("scope") != "core_adapter_only":
        errors.append("authorization fora do escopo da integração no Core")
    if authorization.get("legal_review") != "not_performed":
        errors.append("authorization.legal_review deve permanecer not_performed")
        # Keep this token in the error for stable, actionable validation output.
        errors.append("legal_review não pode ser inferido da autorização do usuário")
    for key in ("installation_authorized", "activation_authorized", "target_analysis_authorized"):
        if authorization.get(key) is not False:
            errors.append(f"authorization.{key} deve permanecer false")

    if data.get("license_status") != "source_declared_unreviewed":
        errors.append("license_status não pode declarar aprovação jurídica")
    if data.get("adoption") != "optional_external_mcp_adapter":
        errors.append("adoption inválido")
    if data.get("integration_status") != "implemented_disabled":
        errors.append("integration_status deve manter o adaptador desabilitado")

    expected_runtime = {
        "installed": False,
        "executed": False,
        "enabled": False,
        "mcp_enabled": False,
        "content_imported": False,
    }
    if data.get("runtime") != expected_runtime:
        runtime = data.get("runtime")
        errors.append("runtime deve manter installed/executed/enabled/mcp_enabled/content_imported false")
        if isinstance(runtime, Mapping) and runtime.get("mcp_enabled") is not False:
            errors.append("runtime.mcp_enabled deve permanecer false")

    default_config = data.get("default_config")
    if not isinstance(default_config, Mapping) or (
        default_config.get("disabled") is not True
        or default_config.get("writes_active_opencode_config") is not False
        or default_config.get("command_mode") != "uv_run_no_sync"
        or default_config.get("activation_requires_environment_review") is not True
    ):
        errors.append("default_config deve permanecer desabilitada e sem escrita ativa")
    expected_scope = {"cloned": False, "downloaded": False, "installed": False, "target_analysis": False}
    if data.get("scope") != expected_scope:
        errors.append("scope não pode alegar clone, download, instalação ou análise de alvos")
    return errors


def status() -> dict[str, Any]:
    """Report policy plus the fixed managed prefix; never use network or run upstream."""
    manifest = load_manifest()
    errors = validate_manifest(manifest)
    installation = managed_installation_status()
    runtime = dict(manifest.get("runtime", {}))
    runtime["installed"] = installation.get("status") == "installed"
    return {
        "spec_id": manifest.get("spec_id"),
        "status": "metadata_only" if not errors else "invalid_manifest",
        "manifest_valid": not errors,
        "adoption": manifest.get("adoption"),
        "integration_status": manifest.get("integration_status"),
        "license_status": manifest.get("license_status"),
        "runtime": runtime,
        "installation": installation,
        "errors": errors,
    }


def default_install_root() -> Path:
    """Return the one managed checkout path; no user config is modified."""
    return Path.home() / ".local" / "share" / "opencode-core" / "external-tools" / "open-reverselab"


def installation_paths(checkout_path: Path | str | None = None) -> dict[str, str]:
    """Resolve fixed sibling paths for checkout, venv, cache, private HOME and receipt."""
    checkout = Path(checkout_path) if checkout_path is not None else default_install_root()
    checkout = Path(os.path.expanduser(os.fspath(checkout)))
    if not checkout.is_absolute() or ".." in checkout.parts:
        raise ValueError("O caminho gerenciado deve ser absoluto e não conter '..'.")
    resolved_for_scope = checkout.resolve(strict=False)
    if resolved_for_scope == REPOSITORY_ROOT or resolved_for_scope.is_relative_to(REPOSITORY_ROOT):
        raise ValueError("O prefixo de instalação não pode ficar dentro do repositório Core.")
    parent = checkout.parent
    stem = checkout.name
    return {
        "checkout": str(checkout),
        "environment": str(parent / f"{stem}-mcp-venv"),
        "cache": str(parent / f"{stem}-uv-cache"),
        "private_home": str(parent / f"{stem}-home"),
        "receipt": str(parent / f"{stem}.installation-r1238.json"),
    }


def _installation_environment(paths: Mapping[str, str]) -> dict[str, str]:
    """Construct a minimal environment; do not inherit account/API credentials."""
    private_home = paths["private_home"]
    return {
        "PATH": os.defpath,
        "HOME": private_home,
        "XDG_CONFIG_HOME": str(Path(private_home) / ".config"),
        "XDG_CACHE_HOME": paths["cache"],
        "UV_CACHE_DIR": paths["cache"],
        "UV_PROJECT_ENVIRONMENT": paths["environment"],
        "UV_NO_CONFIG": "1",
        "UV_NO_PROGRESS": "1",
        "UV_PYTHON_DOWNLOADS": "never",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_OPTIONAL_LOCKS": "0",
        "LANG": "C",
        "LC_ALL": "C",
    }


def install_plan() -> dict[str, Any]:
    """Describe the pinned isolated installation without creating files or processes."""
    paths = installation_paths()
    git = shutil.which("git") or "git"
    uv = shutil.which("uv") or "uv"
    stage = "<staging-checkout>"
    commands = {
        "git_clone": [git, "clone", "--no-checkout", "--no-tags", "--filter=blob:none", "--", SOURCE_URL, stage],
        "git_checkout": [git, "-C", stage, "checkout", "--detach", SOURCE_COMMIT],
        "uv_sync": [
            uv,
            "sync",
            "--locked",
            "--no-install-project",
            "--no-build",
            "--project",
            str(Path(stage) / MCP_RELATIVE),
        ],
    }
    return {
        "spec_id": "SPEC-935-R1238",
        "status": "dry_run",
        "dry_run": True,
        "source": {
            "repository": "LING71671/open-reverselab",
            "url": SOURCE_URL,
            "commit": SOURCE_COMMIT,
            "lockfile": LOCKFILE_RELATIVE.as_posix(),
            "lockfile_git_blob": LOCKFILE_BLOB_ID,
            "root_license_declared": "Apache-2.0",
            "nested_mcp_license_declared": "GPL-3.0-only",
        },
        "paths": paths,
        "commands": commands,
        "environment": _installation_environment(paths),
        "policy": {
            "locked_dependencies_only": True,
            "install_project_package": False,
            "build_source_distributions": False,
            "write_active_opencode_config": False,
            "start_mcp": False,
            "analyze_targets": False,
            "legal_review": "not_performed",
        },
        "mcp_enabled": False,
    }


def verify_pinned_lockfile(
    root: Path | str,
    *,
    runner: Runner | None = None,
) -> dict[str, Any]:
    """Verify the lockfile bytes and Git tree blob match the immutable R1238 pin."""
    checkout = Path(root)
    try:
        lockfile = _regular_checkout_file(checkout, LOCKFILE_RELATIVE)
        git_blob = _git_blob_id(checkout, LOCKFILE_RELATIVE, runner)
        local_blob = _local_git_blob_id(lockfile, max_bytes=2 * 1024 * 1024)
        valid = git_blob == LOCKFILE_BLOB_ID and local_blob == LOCKFILE_BLOB_ID
        return {
            "valid": valid,
            "status": "ready" if valid else "lockfile_blob_mismatch",
            "path": LOCKFILE_RELATIVE.as_posix(),
            "expected_git_blob": LOCKFILE_BLOB_ID,
            "git_blob": git_blob,
            "local_blob": local_blob,
        }
    except CheckoutValidationError as error:
        return {
            "valid": False,
            "status": error.status,
            "error": str(error),
            "path": LOCKFILE_RELATIVE.as_posix(),
            "expected_git_blob": LOCKFILE_BLOB_ID,
        }


def create_install_receipt(
    paths: Mapping[str, str],
    *,
    installed_at: str | None = None,
) -> dict[str, Any]:
    """Build a provenance receipt; callers still must observe successful installation."""
    timestamp = installed_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", timestamp):
        raise ValueError("installed_at deve ser UTC no formato YYYY-MM-DDTHH:MM:SSZ.")
    return {
        "schema_version": INSTALL_RECEIPT_SCHEMA,
        "spec_id": "SPEC-935-R1238",
        "source_repository": "LING71671/open-reverselab",
        "source_url": SOURCE_URL,
        "source_commit": SOURCE_COMMIT,
        "source_lockfile": {
            "path": LOCKFILE_RELATIVE.as_posix(),
            "git_blob": LOCKFILE_BLOB_ID,
        },
        "checkout": paths["checkout"],
        "environment": paths["environment"],
        "installed_at": timestamp,
        "uv_sync": {
            "status": "success",
            "locked": True,
            "no_install_project": True,
            "no_build": True,
            "returncode": 0,
        },
        "authorization": {
            "scope": "checkout_and_locked_dependencies_only",
            "installation_authorized": True,
            "activation_authorized": False,
            "target_analysis_authorized": False,
            "legal_review": "not_performed",
        },
        "runtime": {
            "installed": True,
            "executed": False,
            "upstream_mcp_executed": False,
            "enabled": False,
            "mcp_enabled": False,
            "target_analysis": False,
        },
    }


def _receipt_is_valid(data: Any, paths: Mapping[str, str]) -> bool:
    if not isinstance(data, Mapping):
        return False
    source_lock = data.get("source_lockfile")
    uv_sync = data.get("uv_sync")
    authorization = data.get("authorization")
    runtime = data.get("runtime")
    return bool(
        data.get("schema_version") == INSTALL_RECEIPT_SCHEMA
        and data.get("spec_id") == "SPEC-935-R1238"
        and data.get("source_repository") == "LING71671/open-reverselab"
        and data.get("source_url") == SOURCE_URL
        and data.get("source_commit") == SOURCE_COMMIT
        and isinstance(source_lock, Mapping)
        and source_lock.get("path") == LOCKFILE_RELATIVE.as_posix()
        and source_lock.get("git_blob") == LOCKFILE_BLOB_ID
        and data.get("checkout") == paths["checkout"]
        and data.get("environment") == paths["environment"]
        and isinstance(data.get("installed_at"), str)
        and re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", data["installed_at"]) is not None
        and isinstance(uv_sync, Mapping)
        and uv_sync == {
            "status": "success",
            "locked": True,
            "no_install_project": True,
            "no_build": True,
            "returncode": 0,
        }
        and isinstance(authorization, Mapping)
        and authorization.get("scope") == "checkout_and_locked_dependencies_only"
        and authorization.get("installation_authorized") is True
        and authorization.get("activation_authorized") is False
        and authorization.get("target_analysis_authorized") is False
        and authorization.get("legal_review") == "not_performed"
        and isinstance(runtime, Mapping)
        and runtime.get("installed") is True
        and runtime.get("executed") is False
        and runtime.get("upstream_mcp_executed") is False
        and runtime.get("enabled") is False
        and runtime.get("mcp_enabled") is False
        and runtime.get("target_analysis") is False
    )


def managed_installation_status(checkout_path: Path | str | None = None) -> dict[str, Any]:
    """Observe only the managed local receipt and required paths; never invoke tools."""
    paths = installation_paths(checkout_path)
    checkout = Path(paths["checkout"])
    environment = Path(paths["environment"])
    receipt = Path(paths["receipt"])
    python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    existing = [path for path in (checkout, environment, receipt) if path.exists() or path.is_symlink()]
    runtime = {
        "installed": False,
        "executed": False,
        "upstream_mcp_executed": False,
        "enabled": False,
        "mcp_enabled": False,
        "target_analysis": False,
    }
    if not existing:
        return {"status": "not_installed_in_managed_prefix", "paths": paths, "runtime": runtime}
    if len(existing) != 3:
        return {"status": "partial_installation", "paths": paths, "runtime": runtime}
    if any(path.is_symlink() for path in existing) or not checkout.is_dir() or not environment.is_dir() or not receipt.is_file():
        return {"status": "invalid_managed_paths", "paths": paths, "runtime": runtime}
    if python.is_symlink() or not python.is_file():
        return {"status": "environment_incomplete", "paths": paths, "runtime": runtime}
    try:
        data = json.loads(receipt.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"status": "invalid_receipt", "paths": paths, "runtime": runtime}
    if not _receipt_is_valid(data, paths):
        return {"status": "invalid_receipt", "paths": paths, "runtime": runtime}
    return {
        "status": "installed",
        "paths": paths,
        "source_commit": SOURCE_COMMIT,
        "source_lockfile_git_blob": LOCKFILE_BLOB_ID,
        "receipt": str(receipt),
        "runtime": {**runtime, "installed": True},
    }


def _assert_no_symlink_components(path: Path) -> None:
    cursor = Path(path.anchor)
    for part in path.parts[1:]:
        cursor /= part
        try:
            mode = cursor.lstat().st_mode
        except FileNotFoundError:
            continue
        except OSError as error:
            raise CheckoutValidationError("managed_path_unreadable", "Não foi possível validar o prefixo gerenciado.") from error
        if cursor.is_symlink():
            raise CheckoutValidationError("symlink_path", f"Symlink não aceito no prefixo gerenciado: {cursor}.")
        if cursor != path and not cursor.is_dir():
            raise CheckoutValidationError("managed_path_conflict", f"Componente não é diretório: {cursor}.")


def _write_install_receipt(path: Path, data: Mapping[str, Any]) -> None:
    """Write a private receipt atomically without touching the checkout or OpenCode config."""
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, sort_keys=True, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        # Hard-link publication is atomic and fails if another file already owns
        # the destination; never replace an operator-created receipt.
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def install_isolated(
    *,
    yes: bool = False,
    timeout: int = MAX_INSTALL_TIMEOUT_SECONDS,
    runner: Runner | None = None,
) -> dict[str, Any]:
    """Install pinned source/dependencies only on explicit confirmation; never start MCP."""
    plan = install_plan()
    if isinstance(timeout, bool) or not isinstance(timeout, int) or timeout <= 0 or timeout > MAX_INSTALL_TIMEOUT_SECONDS:
        raise ValueError(f"timeout deve estar entre 1 e {MAX_INSTALL_TIMEOUT_SECONDS} segundos.")
    if not yes:
        return plan

    paths = plan["paths"]
    checkout = Path(paths["checkout"])
    environment = Path(paths["environment"])
    cache = Path(paths["cache"])
    private_home = Path(paths["private_home"])
    receipt = Path(paths["receipt"])
    try:
        _assert_no_symlink_components(checkout.parent)
        for managed in (checkout, environment, cache, private_home, receipt):
            _assert_no_symlink_components(managed)
        existing = [path for path in (checkout, environment, receipt) if path.exists() or path.is_symlink()]
        if existing:
            current = managed_installation_status(checkout)
            if current.get("status") == "installed":
                # The receipt and path markers make this an idempotent local no-op.
                return {
                    **plan,
                    "status": "already_installed",
                    "dry_run": False,
                    "runtime": current["runtime"],
                    "installation": current,
                }
            status_code = "target_conflict" if checkout.exists() or checkout.is_symlink() else "partial_installation"
            return {
                **plan,
                "status": status_code,
                "dry_run": False,
                "error": "Destino existente/parcial ou recibo inválido; nenhuma sobrescrita foi tentada.",
                "runtime": {"installed": False, "executed": False, "mcp_enabled": False},
            }

        checkout.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        _assert_no_symlink_components(checkout.parent)
        for private_directory in (cache, private_home):
            if private_directory.exists() and not private_directory.is_dir():
                raise CheckoutValidationError("managed_path_conflict", f"Caminho privado não é diretório: {private_directory}.")
            private_directory.mkdir(mode=0o700, exist_ok=True)
        config_home = Path(paths["private_home"]) / ".config"
        _assert_no_symlink_components(config_home)
        if config_home.exists() and not config_home.is_dir():
            raise CheckoutValidationError("managed_path_conflict", "XDG_CONFIG_HOME privado não é diretório.")
        config_home.mkdir(mode=0o700, exist_ok=True)

        invoke = runner or subprocess.run
        environment_vars = dict(plan["environment"])

        def run_fixed(argv: Sequence[str], *, cwd: Path, env: Mapping[str, str]) -> subprocess.CompletedProcess[str]:
            try:
                result = invoke(
                    list(argv),
                    cwd=str(cwd),
                    env=dict(env),
                    timeout=timeout,
                    check=False,
                    capture_output=True,
                    text=True,
                    shell=False,
                )
            except (OSError, subprocess.TimeoutExpired) as error:
                raise CheckoutValidationError("installer_command_failed", f"Comando de instalação falhou: {type(error).__name__}.") from error
            if not isinstance(result, subprocess.CompletedProcess):
                # Test doubles and alternate runners may return compatible objects.
                return result
            return result

        git = shutil.which("git") or "git"
        uv = shutil.which("uv") or "uv"
        git_env = dict(environment_vars)
        with tempfile.TemporaryDirectory(prefix=".open-reverselab-stage-", dir=str(checkout.parent)) as staging_parent:
            staging = Path(staging_parent) / "checkout"
            clone_argv = [git, "clone", "--no-checkout", "--no-tags", "--filter=blob:none", "--", SOURCE_URL, str(staging)]
            cloned = run_fixed(clone_argv, cwd=checkout.parent, env=git_env)
            clone_code = int(getattr(cloned, "returncode", 1))
            if clone_code != 0:
                return {**plan, "status": "git_clone_failed", "dry_run": False, "returncode": clone_code,
                        "stderr": str(getattr(cloned, "stderr", "") or "")[:MAX_INSTALL_OUTPUT_CHARS],
                        "runtime": {"installed": False, "executed": False, "mcp_enabled": False}}

            checkout_argv = [git, "-C", str(staging), "checkout", "--detach", SOURCE_COMMIT]
            checked_out = run_fixed(checkout_argv, cwd=staging, env=git_env)
            checkout_code = int(getattr(checked_out, "returncode", 1))
            if checkout_code != 0:
                return {**plan, "status": "git_checkout_failed", "dry_run": False, "returncode": checkout_code,
                        "stderr": str(getattr(checked_out, "stderr", "") or "")[:MAX_INSTALL_OUTPUT_CHARS],
                        "runtime": {"installed": False, "executed": False, "mcp_enabled": False}}

            inspected = inspect_checkout(staging, runner=runner)
            if inspected.get("status") != "ready":
                return {**plan, "status": "checkout_validation_failed", "dry_run": False,
                        "inspection": inspected, "runtime": {"installed": False, "executed": False, "mcp_enabled": False}}
            lock = verify_pinned_lockfile(staging, runner=runner)
            if not lock.get("valid"):
                return {**plan, "status": "lockfile_validation_failed", "dry_run": False,
                        "lockfile": lock, "runtime": {"installed": False, "executed": False, "mcp_enabled": False}}

            sync_argv = [
                uv, "sync", "--locked", "--no-install-project", "--no-build",
                "--project", str(staging / MCP_RELATIVE),
            ]
            synced = run_fixed(sync_argv, cwd=staging, env=environment_vars)
            sync_code = int(getattr(synced, "returncode", 1))
            if sync_code != 0:
                return {**plan, "status": "dependency_sync_failed", "dry_run": False,
                        "returncode": sync_code,
                        "stderr": str(getattr(synced, "stderr", "") or "")[:MAX_INSTALL_OUTPUT_CHARS],
                        "runtime": {"installed": False, "executed": False, "mcp_enabled": False}}

            python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            if python.is_symlink() or not python.is_file():
                return {**plan, "status": "environment_validation_failed", "dry_run": False,
                        "error": "uv sync retornou sucesso, mas o Python do venv gerenciado não está presente.",
                        "runtime": {"installed": False, "executed": False, "mcp_enabled": False}}

            # Revalidate staged sources after dependency sync, then publish atomically.
            inspected_after_sync = inspect_checkout(staging, runner=runner)
            lock_after_sync = verify_pinned_lockfile(staging, runner=runner)
            if inspected_after_sync.get("status") != "ready" or not lock_after_sync.get("valid"):
                return {**plan, "status": "post_sync_validation_failed", "dry_run": False,
                        "inspection": inspected_after_sync, "lockfile": lock_after_sync,
                        "runtime": {"installed": False, "executed": False, "mcp_enabled": False}}
            if checkout.exists() or checkout.is_symlink():
                return {**plan, "status": "target_race_conflict", "dry_run": False,
                        "runtime": {"installed": False, "executed": False, "mcp_enabled": False}}
            os.replace(staging, checkout)

        receipt_data = create_install_receipt(paths)
        if not _receipt_is_valid(receipt_data, paths):
            return {**plan, "status": "receipt_validation_failed", "dry_run": False,
                    "runtime": {"installed": False, "executed": False, "mcp_enabled": False}}
        _write_install_receipt(receipt, receipt_data)
        return {
            **plan,
            "status": "installed",
            "dry_run": False,
            "returncode": 0,
            "runtime": receipt_data["runtime"],
            "installation": managed_installation_status(checkout),
            "receipt": str(receipt),
            "upstream_mcp_executed": False,
            "active_opencode_config_written": False,
        }
    except (CheckoutValidationError, OSError, ValueError, subprocess.TimeoutExpired) as error:
        return {
            **plan,
            "status": getattr(error, "status", "install_error"),
            "dry_run": False,
            "error": str(error)[:MAX_INSTALL_OUTPUT_CHARS],
            "runtime": {"installed": False, "executed": False, "mcp_enabled": False},
        }


def _absolute_checkout(path: str | os.PathLike[str]) -> Path:
    candidate = Path(os.path.expanduser(os.fspath(path)))
    if not candidate.is_absolute():
        raise CheckoutValidationError("path_not_absolute", "Informe o caminho absoluto do checkout local.")
    if ".." in candidate.parts:
        raise CheckoutValidationError("path_traversal", "Componentes '..' não são aceitos no caminho do checkout.")
    cursor = Path(candidate.anchor)
    for component in candidate.parts[1:]:
        cursor = cursor / component
        try:
            cursor.lstat()
        except OSError as error:
            raise CheckoutValidationError("checkout_not_found", "O caminho local informado não existe.") from error
        if cursor.is_symlink():
            raise CheckoutValidationError("symlink_path", "O caminho do checkout contém symlink.")
        if cursor != candidate and not cursor.is_dir():
            raise CheckoutValidationError("invalid_checkout_path", "Um componente do caminho não é diretório.")
        if cursor == candidate and not cursor.is_dir():
            raise CheckoutValidationError("invalid_checkout_path", "O checkout informado não é diretório.")
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as error:
        raise CheckoutValidationError("checkout_not_found", "O checkout local não pôde ser resolvido.") from error
    if resolved != candidate:
        raise CheckoutValidationError("symlink_path", "O caminho resolvido diverge por symlink.")
    return resolved


def _regular_checkout_file(root: Path, relative: Path) -> Path:
    current = root
    for index, part in enumerate(relative.parts):
        current = current / part
        try:
            current.lstat()
        except OSError as error:
            raise CheckoutValidationError("required_file_missing", f"Arquivo requerido ausente: {relative.as_posix()}") from error
        if current.is_symlink():
            raise CheckoutValidationError("symlink_path", f"Symlink não aceito no caminho {relative.as_posix()}.")
        if index < len(relative.parts) - 1 and not current.is_dir():
            raise CheckoutValidationError("required_file_missing", f"Diretório requerido ausente: {relative.as_posix()}")
    if not current.is_file():
        raise CheckoutValidationError("required_file_missing", f"Arquivo regular requerido: {relative.as_posix()}")
    if not current.resolve(strict=True).is_relative_to(root):
        raise CheckoutValidationError("path_escape", f"Caminho requerido escapa do checkout: {relative.as_posix()}.")
    return current


def _git_environment(root: Path) -> dict[str, str]:
    """Remove inherited Git controls and user-global config from read-only probes."""
    return {
        "PATH": os.defpath,
        "HOME": str(root),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_OPTIONAL_LOCKS": "0",
        "GIT_NO_LAZY_FETCH": "1",
        "GIT_TERMINAL_PROMPT": "0",
        "LC_ALL": "C",
        "LANG": "C",
    }


def _git_probe(root: Path, args: Sequence[str], runner: Runner | None) -> subprocess.CompletedProcess[str]:
    command = [
        "git",
        "-c", "core.fsmonitor=false",
        "-c", "core.untrackedCache=false",
        "-C", str(root),
        *args,
    ]
    execute = runner or subprocess.run
    try:
        result = execute(
            command,
            cwd=str(root),
            timeout=MAX_GIT_TIMEOUT_SECONDS,
            check=False,
            capture_output=True,
            text=True,
            shell=False,
            env=_git_environment(root),
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise CheckoutValidationError("git_probe_failed", f"Consulta Git local falhou: {type(error).__name__}.") from error
    if result.returncode != 0:
        raise CheckoutValidationError("git_probe_failed", "Consulta Git local retornou erro.")
    return result


def _read_project_metadata(project_file: Path) -> Mapping[str, Any]:
    text = project_file.read_text(encoding="utf-8")
    if tomllib is not None:
        parsed = tomllib.loads(text)
        project = parsed.get("project")
        return project if isinstance(project, Mapping) else {}

    # The source contract uses three simple quoted TOML strings. On Python 3.10,
    # parse only those fields under [project] rather than adding a dependency.
    project: dict[str, str] = {}
    in_project = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("[") and line.endswith("]"):
            if in_project:
                break
            in_project = line == "[project]"
            continue
        if not in_project or "=" not in line:
            continue
        key, value = (part.strip() for part in line.split("=", 1))
        if key in {"name", "version", "license"}:
            if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
                project[key] = value[1:-1]
    return project


def _git_blob_id(root: Path, relative: Path, runner: Runner | None) -> str:
    result = _git_probe(root, ("rev-parse", f"HEAD:{relative.as_posix()}"), runner)
    blob_id = result.stdout.strip().lower()
    if not re.fullmatch(r"[0-9a-f]{40}", blob_id):
        raise CheckoutValidationError("source_blob_unavailable", f"Blob pin ausente para {relative.as_posix()}.")
    return blob_id


def _local_git_blob_id(path: Path, *, max_bytes: int) -> str:
    try:
        size = path.stat().st_size
        if size > max_bytes:
            raise CheckoutValidationError("source_file_too_large", f"Arquivo excede limite: {path.name}.")
        content = path.read_bytes()
    except CheckoutValidationError:
        raise
    except OSError as error:
        raise CheckoutValidationError("source_file_unreadable", f"Não foi possível ler {path.name}.") from error
    object_header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(object_header + content).hexdigest()


def _inspect_checkout(path: str | os.PathLike[str], *, runner: Runner | None = None) -> dict[str, Any]:
    """Internal validating path; never imports or runs the checkout."""
    manifest = load_manifest()
    errors = validate_manifest(manifest)
    if errors:
        raise CheckoutValidationError("invalid_manifest", "; ".join(errors))
    root = _absolute_checkout(path)
    git_marker = root / ".git"
    if git_marker.is_symlink() or not (git_marker.is_dir() or git_marker.is_file()):
        raise CheckoutValidationError("not_git_root", "O checkout precisa ter metadado Git regular, não symlink.")

    top_level = _git_probe(root, ("rev-parse", "--show-toplevel"), runner).stdout.strip()
    try:
        top_path = Path(top_level).resolve(strict=True)
    except OSError as error:
        raise CheckoutValidationError("not_git_root", "Git não identificou a raiz local do repositório.") from error
    if top_path != root:
        raise CheckoutValidationError("not_git_root", "O caminho informado não é a raiz do checkout Git.")

    commit = _git_probe(root, ("rev-parse", "HEAD"), runner).stdout.strip().lower()
    if commit != SOURCE_COMMIT:
        raise CheckoutValidationError("commit_mismatch", "O checkout não corresponde ao commit fixado.")
    porcelain = _git_probe(root, ("status", "--porcelain=v1", "--untracked-files=all"), runner).stdout
    if porcelain.strip():
        raise CheckoutValidationError("dirty_checkout", "O checkout contém alterações ou arquivos não rastreados.")

    root_license = _regular_checkout_file(root, Path("LICENSE"))
    disclaimer = _regular_checkout_file(root, Path("DISCLAIMER.md"))
    project_file = _regular_checkout_file(root, MCP_RELATIVE / "pyproject.toml")
    entrypoint = _regular_checkout_file(root, ENTRYPOINT_RELATIVE)
    license_text = root_license.read_text(encoding="utf-8", errors="replace")[:1024 * 1024]
    if "Apache License" not in license_text or "Version 2.0" not in license_text:
        raise CheckoutValidationError("root_license_mismatch", "A declaração LICENSE raiz não corresponde ao registro observado.")
    try:
        project = _read_project_metadata(project_file)
    except (OSError, ValueError) as error:
        raise CheckoutValidationError("mcp_metadata_invalid", "pyproject.toml do MCP não pôde ser validado.") from error
    if not isinstance(project, Mapping) or (
        project.get("name") != "reverselab-tools-mcp"
        or project.get("version") != "0.1.0"
        or project.get("license") != "GPL-3.0-only"
    ):
        raise CheckoutValidationError("mcp_license_mismatch", "Nome, versão ou licença declarada do MCP diverge do pin observado.")

    tracked_sources = (
        (Path("LICENSE"), root_license, 1024 * 1024),
        (Path("DISCLAIMER.md"), disclaimer, 1024 * 1024),
        (MCP_RELATIVE / "pyproject.toml", project_file, 256 * 1024),
        (ENTRYPOINT_RELATIVE, entrypoint, 8 * 1024 * 1024),
    )
    for relative, local_path, max_bytes in tracked_sources:
        pinned_blob = _git_blob_id(root, relative, runner)
        if _local_git_blob_id(local_path, max_bytes=max_bytes) != pinned_blob:
            raise CheckoutValidationError("source_file_mismatch", f"Conteúdo local diverge do commit pinado: {relative.as_posix()}.")

    return {
        "status": "ready",
        "root": str(root),
        "commit": commit,
        "root_license": "Apache-2.0",
        "license": project["license"],
        "project_name": project["name"],
        "project_version": project["version"],
        "mcp_project": str(project_file.parent),
        "entrypoint": str(entrypoint),
        "disclaimer_present": disclaimer.is_file(),
        "pinned_source_files_verified": True,
        "code_imported": False,
        "code_executed": False,
        "mcp_enabled": False,
    }


def inspect_checkout(path: str | os.PathLike[str], *, runner: Runner | None = None) -> dict[str, Any]:
    """Inspect a user-supplied checkout and return structured failure states."""
    try:
        return _inspect_checkout(path, runner=runner)
    except CheckoutValidationError as error:
        return {
            "status": error.status,
            "error": str(error),
            "code_imported": False,
            "code_executed": False,
            "mcp_enabled": False,
        }


def mcp_config(path: str | os.PathLike[str], *, runner: Runner | None = None) -> dict[str, Any]:
    """Emit an OpenCode v2 config fragment with the external server disabled."""
    inspected = inspect_checkout(path, runner=runner)
    if inspected.get("status") != "ready":
        raise CheckoutValidationError(str(inspected.get("status", "checkout_invalid")), str(inspected.get("error", "Checkout inválido.")))
    paths = installation_paths()
    managed = Path(inspected["root"]) == Path(paths["checkout"])
    installed = managed and managed_installation_status().get("status") == "installed"
    if installed:
        lock = verify_pinned_lockfile(inspected["root"], runner=runner)
        if not lock.get("valid"):
            raise CheckoutValidationError("lockfile_validation_failed", "O lockfile do checkout gerenciado diverge do pin R1238.")
        python = Path(paths["environment"]) / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        command = [str(python), inspected["entrypoint"]]
    else:
        command = [
            "uv", "run", "--no-sync", "--project", inspected["mcp_project"],
            "python", inspected["entrypoint"],
        ]
    server = {
        "type": "local",
        "command": command,
        "cwd": inspected["root"],
        "disabled": True,
    }
    return {
        "status": "candidate_disabled",
        "provenance": {
            "commit": inspected["commit"],
            "nested_mcp_license_declared": inspected["license"],
            "legal_review": "not_performed",
        },
        "runtime": {
            "installed": bool(installed),
            "executed": False,
            "enabled": False,
            "mcp_enabled": False,
            "content_imported": False,
        },
        "requirements": [
            "OpenCode MCP schema v2",
            "uv and MCP dependencies must already be available",
            "enabling the server requires a separate explicit user decision",
            "review inherited environment exposure before activation",
        ],
        "config": {"mcp": {"servers": {"reverse-lab-tools": server}}},
    }


def _emit(data: Mapping[str, Any]) -> None:
    print(json.dumps(data, ensure_ascii=False, sort_keys=True))


def main(argv: Sequence[str] | None = None, *, runner: Runner | None = None) -> int:
    parser = argparse.ArgumentParser(description="Adaptador OpenReverseLab com instalação isolada e ativação desabilitada")
    subparsers = parser.add_subparsers(dest="operation", required=True)
    subparsers.add_parser("status", help="valida apenas o manifesto local")
    inspect_parser = subparsers.add_parser("inspect", help="inspeciona checkout local fixado sem executar seu código")
    inspect_parser.add_argument("--path", required=True, help="caminho absoluto do checkout local")
    config_parser = subparsers.add_parser("config", help="emite fragmento MCP desabilitado em stdout")
    config_parser.add_argument("--path", required=True, help="caminho absoluto do checkout local")
    install_parser = subparsers.add_parser("install", help="instala commit e dependências isoladas; exige --yes para executar")
    install_parser.add_argument("--yes", action="store_true", help="confirmar instalação no prefixo gerenciado")
    install_parser.add_argument("--timeout", type=int, default=MAX_INSTALL_TIMEOUT_SECONDS)
    args = parser.parse_args(argv)
    try:
        if args.operation == "status":
            result = status()
        elif args.operation == "inspect":
            result = inspect_checkout(args.path, runner=runner)
        elif args.operation == "install":
            result = install_isolated(yes=args.yes, timeout=args.timeout, runner=runner)
        else:
            result = mcp_config(args.path, runner=runner)
        _emit(result)
        return 0 if result.get("status") in {"metadata_only", "ready", "candidate_disabled", "dry_run", "installed", "already_installed"} else 2
    except CheckoutValidationError as error:
        _emit({"status": error.status, "error": str(error), "runtime": {"executed": False, "mcp_enabled": False}})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
