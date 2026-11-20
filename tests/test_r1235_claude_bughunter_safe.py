"""Contratos offline da integração limitada Claude-BugHunter (R1235)."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "federation/claude-bughunter.json"
SKILL_PATH = ROOT / ".opencode/skills/claude-bughunter-safe/SKILL.md"
REPOSITORY = "elementalsouls/Claude-BugHunter"
OBSERVED_COMMIT = "0e70a021e59d6875004e7a563f8511aca2ba3bc1"


def _manifest():
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_manifest_pins_observed_snapshot_and_separates_license_claims():
    manifest = _manifest()
    source = manifest["source"]
    assert manifest["schema_version"] == "r1235.v1"
    assert manifest["repository"] == REPOSITORY
    assert source["url"] == f"https://github.com/{REPOSITORY}"
    assert source["commit"] == OBSERVED_COMMIT
    assert re.fullmatch(r"[0-9a-f]{40}", source["commit"])
    assert source["observed_via"] == "github_commits_atom_feed"
    assert source["signature_status"] == "not_observed"
    assert source["branch_head_status"] == "not_verified"
    assert manifest["license"] == {
        "code": "MIT",
        "content": "CC-BY-4.0",
        "third_party_material": "independent_unreviewed",
        "legal_review": "not_performed",
    }
    assert manifest["evidence"]["license_code"].endswith("/LICENSE")
    assert manifest["evidence"]["license_content"].endswith("/LICENSE-CONTENT")
    assert manifest["evidence"]["notice"].endswith("/NOTICE")


def test_manifest_forbids_upstream_import_install_execution_and_mcp():
    manifest = _manifest()
    assert manifest["adoption"] == "reference_only"
    assert manifest["content_imported"] is False
    assert manifest["upstream_skills_imported"] == 0
    assert manifest["upstream_commands_imported"] == 0
    assert manifest["runtime"] == {
        "installed": False,
        "executed": False,
        "enabled": False,
        "mcp_enabled": False,
    }
    assert manifest["active_target_testing_authorized"] is False


def test_skill_requires_explicit_authority_and_bounded_scope():
    text = SKILL_PATH.read_text(encoding="utf-8").casefold()
    assert SKILL_PATH.is_file()
    assert f"https://github.com/{REPOSITORY}" in text
    assert OBSERVED_COMMIT in text
    assert "autorização escrita" in text
    assert "escopo" in text
    assert "ativos próprios" in text or "ativos que a pessoa controla" in text
    assert "sem autorização" in text or "na ausência de autorização" in text
    assert "revisão de código" in text
    assert "alvos" in text


def test_skill_limits_assistance_to_defensive_non_intrusive_work():
    text = SKILL_PATH.read_text(encoding="utf-8").casefold()
    assert "recomendações de correção" in text
    assert "não executa testes" in text or "não realize testes" in text
    assert "não fornece payloads" in text or "não inclua payloads" in text
    assert "pós-exploração" in text
    assert "negação de serviço" in text or "dos" in text
    assert "burp mcp" in text
    assert "não instale" in text or "não instalar" in text
