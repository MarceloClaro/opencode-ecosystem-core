# -*- coding: utf-8 -*-
"""Testes R262 — Suíte PhD Amazon KDP no catálogo do OpenCode Ecosystem Core."""

from __future__ import annotations

import re
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CATALOG_DIR = PROJECT_ROOT / "agents" / "catalog"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


EXPECTED_KDP_AGENTS = {
    "kdp-orchestrator-phd": "amazon kdp",
    "kdp-interior-layout-phd": "miolo",
    "kdp-cover-engineer-phd": "capa",
    "kdp-ebook-epub-phd": "epub",
    "kdp-preflight-auditor-phd": "preflight",
    "kdp-metadata-isbn-phd": "isbn",
    "kdp-final-qa-phd": "qa final",
}


def _frontmatter(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    assert match, f"{path.name} sem frontmatter YAML"
    return match.group(1)


def test_kdp_agent_files_exist_and_declare_contract():
    for agent_id, keyword in EXPECTED_KDP_AGENTS.items():
        path = CATALOG_DIR / f"{agent_id}.md"
        assert path.exists(), f"Agente KDP ausente: {path}"
        text = path.read_text(encoding="utf-8")
        fm = _frontmatter(path)
        for field in ("name:", "description:", "model:", "tools:"):
            assert field in fm, f"{agent_id} não declara {field}"
        assert keyword.lower() in text.lower(), f"{agent_id} não cobre {keyword}"
        assert "Amazon KDP" in text, f"{agent_id} sem instruções explícitas de Amazon KDP"
        assert "não prometa aprovação" in text.lower(), f"{agent_id} sem regra anti-overclaim KDP"
        assert "SDD" in text and "TDD" in text, f"{agent_id} sem protocolo SDD/TDD"


def test_kdp_agents_load_with_amazon_kdp_capabilities():
    from marceloclaro.catalog_loader import load_catalog_definitions

    definitions = {
        Path(definition["source_file"]).stem: definition
        for definition in load_catalog_definitions()
    }
    for agent_id in EXPECTED_KDP_AGENTS:
        assert agent_id in definitions, f"{agent_id} não carregou pelo catalog_loader"
        capabilities = set(definitions[agent_id]["capabilities"])
        assert "amazon_kdp" in capabilities, f"{agent_id} sem capability amazon_kdp: {capabilities}"
        assert "book_formatting" in capabilities, f"{agent_id} sem capability book_formatting: {capabilities}"


def test_kdp_agents_are_registered_in_opencode_config_with_model():
    from integrations.opencode_cli import build_config

    agents = build_config()["agent"]
    for agent_id in EXPECTED_KDP_AGENTS:
        assert agent_id in agents, f"{agent_id} ausente do opencode.json gerado"
        generated = agents[agent_id]
        assert generated["mode"] == "subagent"
        assert "agents/catalog/" in generated["prompt"]
        assert generated.get("model"), f"{agent_id} sem model propagado para opencode.json"
        permission = generated.get("permission", {})
        assert permission.get("edit") != "allow", f"{agent_id} recebeu edit irrestrito"
        assert permission.get("bash") != "allow", f"{agent_id} recebeu bash irrestrito"
