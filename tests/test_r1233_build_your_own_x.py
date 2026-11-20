"""Contratos offline da integração de referência Build Your Own X (R1233)."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "federation/build-your-own-x.json"
SKILL_PATH = ROOT / ".opencode/skills/build-your-own-x/SKILL.md"
REPO = "codecrafters-io/build-your-own-x"
COMMIT = "94e4be4102452119008fe47199f3cb915abe0c50"


def _manifest():
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_source_manifest_pins_repository_commit_and_license_boundary():
    manifest = _manifest()
    source = manifest["source"]
    assert manifest["schema_version"] == "r1233.v1"
    assert manifest["repository"] == REPO
    assert source["url"] == f"https://github.com/{REPO}"
    assert source["commit"] == COMMIT
    assert re.fullmatch(r"[0-9a-f]{40}", source["commit"])
    assert source["commit_signature_verified"] is True
    assert manifest["license"]["readme_declaration"] == "CC0-1.0"
    assert manifest["license"]["github_api_license"] is None
    assert manifest["license"]["legal_review"] == "not_performed"
    assert manifest["license"]["downstream_links"] == "independent_unreviewed"


def test_manifest_forbids_install_execution_and_mcp_enablement():
    manifest = _manifest()
    assert manifest["adoption"] == "reference_only"
    runtime = manifest["runtime"]
    assert runtime == {
        "installed": False,
        "executed": False,
        "enabled": False,
        "mcp_enabled": False,
    }
    assert manifest["content_imported"] is False
    assert manifest["chatgpt_connector_changed"] is False


def test_skill_is_discoverable_and_uses_pinned_upstream_reference():
    text = SKILL_PATH.read_text(encoding="utf-8")
    assert SKILL_PATH.is_file()
    assert text.startswith("---\n")
    assert "name: Build Your Own X" in text
    assert "description:" in text
    assert f"https://github.com/{REPO}" in text
    assert COMMIT in text
    for section in ("## Fluxo", "## Saída", "## Limites"):
        assert section in text


def test_skill_preserves_downstream_license_and_execution_boundaries():
    text = SKILL_PATH.read_text(encoding="utf-8").casefold()
    assert "licença" in text
    assert "cada tutorial" in text or "fontes vinculadas" in text
    assert "não execute" in text or "não executar" in text
    assert "não clone" in text or "não clonar" in text
    assert "não copie" in text or "não copiar" in text
    assert "não habilita" in text and "tunnel" in text
