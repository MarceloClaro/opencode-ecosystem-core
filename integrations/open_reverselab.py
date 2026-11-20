"""SPEC-935-R1237: optional OpenReverseLab metadata and MCP-config adapter.

This module never imports or runs the upstream MCP project. It can inspect an
explicit local checkout using fixed, read-only Git commands and emit a disabled
OpenCode configuration candidate to stdout. It does not install dependencies or
write active OpenCode configuration.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 compatibility without a new dependency.
    tomllib = None  # type: ignore[assignment]
from typing import Any, Callable, Mapping, Sequence


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPOSITORY_ROOT / "federation" / "open-reverselab-adapter-r1237.json"
HISTORICAL_MANIFEST_PATH = REPOSITORY_ROOT / "federation" / "repository-curation-r1232.json"
SOURCE_COMMIT = "c42da86aadcbea4f2dd20822653f83da5f6aba54"
MCP_RELATIVE = Path("tools/skills/mcp/ReverseLabToolsMCP")
ENTRYPOINT_RELATIVE = MCP_RELATIVE / "reverse_lab_tools_mcp.py"
MAX_GIT_TIMEOUT_SECONDS = 8


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
    """Report the Core manifest only; never inspect paths or start a process."""
    manifest = load_manifest()
    errors = validate_manifest(manifest)
    return {
        "spec_id": manifest.get("spec_id"),
        "status": "metadata_only" if not errors else "invalid_manifest",
        "manifest_valid": not errors,
        "adoption": manifest.get("adoption"),
        "integration_status": manifest.get("integration_status"),
        "license_status": manifest.get("license_status"),
        "runtime": manifest.get("runtime"),
        "errors": errors,
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
    server = {
        "type": "local",
        "command": [
            "uv", "run", "--no-sync", "--project", inspected["mcp_project"],
            "python", inspected["entrypoint"],
        ],
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
            "installed": False,
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
    parser = argparse.ArgumentParser(description="Adaptador OpenReverseLab somente leitura do Core")
    subparsers = parser.add_subparsers(dest="operation", required=True)
    subparsers.add_parser("status", help="valida apenas o manifesto local")
    inspect_parser = subparsers.add_parser("inspect", help="inspeciona checkout local fixado sem executar seu código")
    inspect_parser.add_argument("--path", required=True, help="caminho absoluto do checkout local")
    config_parser = subparsers.add_parser("config", help="emite fragmento MCP desabilitado em stdout")
    config_parser.add_argument("--path", required=True, help="caminho absoluto do checkout local")
    args = parser.parse_args(argv)
    try:
        if args.operation == "status":
            result = status()
        elif args.operation == "inspect":
            result = inspect_checkout(args.path, runner=runner)
        else:
            result = mcp_config(args.path, runner=runner)
        _emit(result)
        return 0 if result.get("status") in {"metadata_only", "ready", "candidate_disabled"} else 2
    except CheckoutValidationError as error:
        _emit({"status": error.status, "error": str(error), "runtime": {"executed": False, "mcp_enabled": False}})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
