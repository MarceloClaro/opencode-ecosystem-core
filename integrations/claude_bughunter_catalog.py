"""Catálogo defensivo fechado para o snapshot inerte Claude-BugHunter (R1239).

O módulo lê somente manifestos do Core. Não abre o snapshot upstream nem seu
índice de skills/comandos; a única rota exposta é a skill defensiva original.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any


PACKAGE_MANIFEST = "federation/claude-bughunter-package-r1236.json"
BURP_MANIFEST = "federation/claude-bughunter-mcp-r1239.json"
REPOSITORY = "elementalsouls/Claude-BugHunter"
COMMIT = "0e70a021e59d6875004e7a563f8511aca2ba3bc1"
ARCHIVE_SHA256 = "17d47b16d6db7214ebeb80565cd471f558f876efaff5a2fee1f6f718f498e371"
SNAPSHOT_ROOT = "external/claude-bughunter-snapshot"
SAFE_SKILL = {
    "id": "claude-bughunter-safe",
    "kind": "first_party_skill",
    "path": ".opencode/skills/claude-bughunter-safe/SKILL.md",
    "policy": "defensive_review_only",
    "invocation": "explicit",
    "executed": False,
}
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def _read_object(path: Path, *, limit: int = 1024 * 1024) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ValueError("manifesto ausente ou não regular")
    if path.stat().st_size > limit:
        raise ValueError("manifesto excede o limite de tamanho")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("manifesto ilegível ou JSON inválido") from exc
    if not isinstance(value, dict):
        raise ValueError("manifesto deve ser um objeto JSON")
    return value


def _validate_package(manifest: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    if manifest.get("schema_version") != "r1236.v1" or manifest.get("spec_id") != "SPEC-935-R1236":
        raise ValueError("schema ou spec do pacote Claude-BugHunter divergente")
    if manifest.get("repository") != REPOSITORY:
        raise ValueError("repositório do pacote Claude-BugHunter divergente")

    source = manifest.get("source")
    snapshot = manifest.get("snapshot")
    activation = manifest.get("activation")
    runtime = manifest.get("runtime")
    license_data = manifest.get("license")
    if not all(isinstance(item, dict) for item in (source, snapshot, activation, runtime, license_data)):
        raise ValueError("seções obrigatórias ausentes no manifesto do pacote")
    if source.get("commit") != COMMIT or source.get("archive_sha256") != ARCHIVE_SHA256:
        raise ValueError("proveniência ou hash do pacote Claude-BugHunter divergente")
    if (source.get("url") != f"https://github.com/{REPOSITORY}"
            or source.get("commit_url") != f"https://github.com/{REPOSITORY}/commit/{COMMIT}"
            or source.get("archive_url") != f"https://codeload.github.com/{REPOSITORY}/zip/{COMMIT}"
            or source.get("observed_via") != "github_commits_atom_feed"
            or source.get("archive_bytes") != 2_145_462
            or source.get("archive_crc_check") != "passed"):
        raise ValueError("localizadores ou recibo do arquivo-fonte divergentes")
    if not _SHA256.fullmatch(str(source.get("archive_sha256", ""))):
        raise ValueError("hash SHA-256 do arquivo-fonte inválido")
    if source.get("signature_status") != "not_observed" or source.get("branch_head_status") != "not_verified":
        raise ValueError("estado de verificação de origem inesperado")
    if snapshot.get("root") != SNAPSHOT_ROOT:
        raise ValueError("raiz do snapshot divergente")

    rows = snapshot.get("files")
    expected = {
        "file_count": 341,
        "total_bytes": 4_402_146,
        "skills_count": 83,
        "commands_count": 15,
    }
    if not isinstance(rows, list) or len(rows) != expected["file_count"]:
        raise ValueError("inventário do snapshot ausente ou com contagem divergente")
    paths: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("entrada inválida no inventário do snapshot")
        name = row.get("path")
        digest = row.get("sha256")
        size = row.get("bytes")
        if (not isinstance(name, str) or not name or name.startswith("/") or "\\" in name
                or ".." in Path(name).parts or not _SHA256.fullmatch(str(digest or ""))
                or type(size) is not int or size < 0):
            raise ValueError("caminho, tamanho ou hash inválido no inventário")
        paths.append(name)
    if paths != sorted(paths) or len(paths) != len(set(paths)):
        raise ValueError("inventário do snapshot não é canônico")
    for key, value in expected.items():
        if snapshot.get(key) != value:
            raise ValueError(f"contagem do snapshot divergente: {key}")
    if sum(row["bytes"] for row in rows) != expected["total_bytes"]:
        raise ValueError("tamanho agregado do snapshot divergente")
    if license_data != {
        "code": "MIT",
        "content": "CC-BY-4.0",
        "third_party_material": "independent_unreviewed",
        "legal_review": "not_performed",
    }:
        raise ValueError("declarações de licença do pacote divergentes")
    evidence = manifest.get("evidence")
    if not isinstance(evidence, dict) or any(
        evidence.get(field) != expected_path
        for field, expected_path in (
            ("license_code", "LICENSE"),
            ("license_content", "LICENSE-CONTENT"),
            ("notice", "NOTICE"),
        )
    ):
        raise ValueError("referências de licença/NOTICE divergentes")
    if manifest.get("adoption") != "inert_snapshot":
        raise ValueError("pacote não está marcado como snapshot inerte")
    if activation != {
        "registered_skill_count": 0,
        "registered_command_count": 0,
        "scripts_executable": False,
        "burp_mcp_registered": False,
    }:
        raise ValueError("ativação upstream detectada ou estado de ativação inválido")
    if runtime != {"installed": False, "executed": False, "enabled": False, "mcp_enabled": False}:
        raise ValueError("runtime upstream não está inerte")
    if manifest.get("active_target_testing_authorized") is not False:
        raise ValueError("manifesto não mantém testes a alvos bloqueados")

    snapshot_path = repo_root / SNAPSHOT_ROOT
    skill_path = repo_root / SAFE_SKILL["path"]
    if snapshot_path.is_symlink() or not snapshot_path.is_dir():
        raise ValueError("raiz do snapshot ausente, insegura ou não diretório")
    if skill_path.is_symlink() or not skill_path.is_file():
        raise ValueError("skill defensiva local ausente ou insegura")
    return {
        "repository": REPOSITORY,
        "commit": COMMIT,
        "archive_sha256": ARCHIVE_SHA256,
        "snapshot_root": SNAPSHOT_ROOT,
        "snapshot_file_count": expected["file_count"],
        "snapshot_bytes": expected["total_bytes"],
        "upstream_skill_count": expected["skills_count"],
        "upstream_command_count": expected["commands_count"],
        "license": license_data,
        "runtime_hash_verification": "not_performed_by_catalog",
    }


def _validate_burp(manifest: dict[str, Any]) -> dict[str, Any]:
    if manifest.get("schema_version") != "r1239.burp.v1" or manifest.get("spec_id") != "SPEC-935-R1239":
        raise ValueError("schema ou spec do estado Burp MCP divergente")
    if manifest.get("provider") != "portswigger-official" or manifest.get("authorization_granted") is not True:
        raise ValueError("provedor Burp MCP ou autorização divergente")
    if manifest.get("transport") != "stdio_proxy_to_local_sse" or manifest.get("endpoint") != "http://127.0.0.1:9876":
        raise ValueError("transporte/endpoint Burp MCP divergente")
    if manifest.get("status") != "blocked_missing_local_runtime":
        raise ValueError("estado de prontidão Burp MCP inesperado")
    observed = manifest.get("observed_prerequisites")
    if observed != {
        "java_executable_found": False,
        "proxy_jar_found_in_search_roots": False,
        "burp_directories_found_under_home": False,
    }:
        raise ValueError("pré-requisitos locais Burp MCP não correspondem à observação")
    for field in (
        "enabled", "opencode_server_configured", "burp_started", "mcp_connected",
        "http_requests_sent", "config_editing_authorized", "target_testing_authorized",
    ):
        if manifest.get(field) is not False:
            raise ValueError(f"estado Burp MCP não fail-closed: {field}")
    return {
        "provider": "portswigger-official",
        "authorization_granted": True,
        "status": "blocked_missing_local_runtime",
        "endpoint": "http://127.0.0.1:9876",
        "transport": "stdio_proxy_to_local_sse",
        "enabled": False,
        "opencode_server_configured": False,
        "observed_prerequisites": observed,
        "burp_started": False,
        "mcp_connected": False,
        "http_requests_sent": False,
        "target_testing_authorized": False,
    }


def load_catalog(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Valida proveniência e emite somente uma rota defensiva first-party."""
    root = Path(repo_root or Path(__file__).resolve().parents[1]).resolve()
    package_manifest = _read_object(root / PACKAGE_MANIFEST)
    burp_manifest = _read_object(root / BURP_MANIFEST)
    package = _validate_package(package_manifest, root)
    burp = _validate_burp(burp_manifest)
    from integrations.burp_wsl2_plan import load_plan
    wsl2_transport_plan = load_plan(root)
    return {
        "schema_version": "r1239.v1",
        "spec_id": "SPEC-935-R1239",
        "orchestrator": "marceloclaro",
        "status": "reference_only",
        "package": package,
        "entries": [dict(SAFE_SKILL)],
        "burp_mcp": burp,
        "wsl2_transport_plan": wsl2_transport_plan,
        "executed": False,
        "execution_verified": False,
    }


__all__ = ["load_catalog"]
