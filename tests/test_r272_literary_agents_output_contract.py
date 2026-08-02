# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-935-R272: contrato de saída dos agentes literários."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
CATALOG = ROOT / "agents" / "catalog"

LITERARY_AGENTS = {
    "literary-orchestrator-phd",
    "literary-narratology-architect-phd",
    "literary-style-voice-phd",
    "literary-character-psychology-phd",
    "literary-symbolic-imagery-phd",
    "literary-ethics-trauma-phd",
    "literary-innovation-editorial-phd",
    "literary-research-scholar-phd",
}

REQUIRED_OUTPUT_TERMS = {
    "contrato de saída obrigatório",
    "nunca pode ser vazia",
    "veredito",
    "strengths",
    "risks",
    "recommendations",
    "safe_claim",
    "limites",
    "dados insuficientes",
}

SCANNER_TERMS = {
    "narrativearchitecturescanner",
    "stylevoicescanner",
    "characterpsychologyscanner",
    "symbolicimageryscanner",
    "ethicalrepresentationscanner",
    "literaryinnovationscanner",
    "literarybibliographyscanner",
    "comparativecorpusscanner",
    "theoreticalframeworkscanner",
    "internationalrigorscanner",
    "run_literary_scanner_suite",
    "run_literary_research_scanner_suite",
}


def _agent_path(agent_id: str) -> Path:
    return CATALOG / f"{agent_id}.md"


def _frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    assert match, "arquivo de agente deve começar com frontmatter YAML"
    data: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def test_r272_all_literary_agents_have_non_empty_output_contract():
    for agent_id in LITERARY_AGENTS:
        text = _agent_path(agent_id).read_text(encoding="utf-8")
        lower = text.lower()
        for term in REQUIRED_OUTPUT_TERMS:
            assert term in lower, f"{agent_id} não contém termo obrigatório: {term}"


def test_r272_literary_agents_have_fallback_model_and_frontmatter():
    for agent_id in LITERARY_AGENTS:
        fm = _frontmatter(_agent_path(agent_id).read_text(encoding="utf-8"))
        assert fm.get("name") == agent_id
        assert fm.get("mode") == "subagent"
        # R276: sem model explícito; usar fallback do runtime.
        assert "model" not in fm
        assert "description" in fm and len(fm["description"]) > 40
        assert "temperature" in fm


def test_r272_agents_reference_scanners_and_anti_overclaim_limits():
    for agent_id in LITERARY_AGENTS:
        lower = _agent_path(agent_id).read_text(encoding="utf-8").lower()
        assert any(term in lower for term in SCANNER_TERMS), f"{agent_id} não referencia scanner compatível"
        for term in ["anti-overclaim", "crítica humana", "corpus comparativo", "validação externa"]:
            assert term in lower, f"{agent_id} não explicita limite anti-overclaim: {term}"


def test_r272_orchestrator_detects_empty_subagent_outputs():
    lower = _agent_path("literary-orchestrator-phd").read_text(encoding="utf-8").lower()
    for term in ["retorno vazio", "subagente", "fallback", "consolidar", "não declare parecer multiagente"]:
        assert term in lower


def test_r272_research_agent_separates_internal_and_external_evidence():
    lower = _agent_path("literary-research-scholar-phd").read_text(encoding="utf-8").lower()
    for term in [
        "sem busca externa real",
        "evidência interna",
        "validação externa",
        "peer review",
        "doi",
        "isbn",
    ]:
        assert term in lower


def test_r272_opencode_config_contains_updated_literary_agents():
    from integrations.opencode_cli import build_config

    config = build_config()
    agents = config.get("agent", {})
    for agent_id in LITERARY_AGENTS:
        agent = agents[agent_id]
        assert "model" not in agent
        assert agent["prompt"] == f"{{file:./agents/catalog/{agent_id}.md}}"
    json.dumps(config, ensure_ascii=False)
