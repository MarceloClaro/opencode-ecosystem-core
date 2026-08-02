# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-935-R268: agentes literários e scanners de pesquisa."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sdd.spec_engine import spec_registry


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "agents" / "catalog"

EXPECTED_AGENTS = {
    "literary-orchestrator-phd",
    "literary-narratology-architect-phd",
    "literary-style-voice-phd",
    "literary-character-psychology-phd",
    "literary-symbolic-imagery-phd",
    "literary-ethics-trauma-phd",
    "literary-innovation-editorial-phd",
    "literary-research-scholar-phd",
}

EXPECTED_RESEARCH_SCANNERS = {
    "literary_bibliography",
    "comparative_corpus",
    "theoretical_framework",
    "international_rigor",
}

RICH_RESEARCH_TEXT = """
Projeto de pesquisa literária comparada: analisar romance-arquivo, horror
documental e literatura ergódica em diálogo com Machado de Assis, Mary Shelley,
Borges, Poe, Cortázar, Italo Calvino, Mark Z. Danielewski e Svetlana Aleksiévitch.
Corpus primário: Molambudos, House of Leaves, Frankenstein e contos de arquivo.
Corpus secundário: artigos revisados por pares, livros acadêmicos, crítica
especializada, bases MLA International Bibliography, JSTOR, Project MUSE, SciELO
e Google Scholar. Referencial teórico: Genette sobre paratexto, Foucault sobre
arquivo e clínica, Ricoeur sobre memória, LaCapra sobre trauma, Hutcheon sobre
metaficção historiográfica, Aarseth sobre literatura ergódica e Eco sobre obra
aberta. Metodologia: comparação de motivos, matriz de corpus, critérios de
inclusão/exclusão, limitações, escopo, lacunas, evidências, citações, DOI/ISBN,
edições utilizadas e alerta anti-overclaim. A hipótese é interpretativa, não
validação canônica, e requer revisão externa.
"""

WEAK_RESEARCH_TEXT = """O livro é bom e inovador. Tem referências e muita teoria."""


def _frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    assert match, "arquivo de agente deve começar com frontmatter YAML"
    data = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def test_spec_r268_registered():
    spec = spec_registry.get("SPEC-935-R268")
    assert spec is not None
    assert spec.status in {"red", "green", "verified"}


def test_all_literary_agents_exist_and_have_valid_frontmatter():
    for agent in EXPECTED_AGENTS:
        path = CATALOG / f"{agent}.md"
        assert path.exists(), f"agente ausente: {agent}"
        text = path.read_text(encoding="utf-8")
        fm = _frontmatter(text)
        assert fm.get("name") == agent
        assert fm.get("mode") == "subagent"
        # R276: agentes literários usam fallback de modelo do runtime para evitar
        # rotas explícitas silenciosas observadas em R274/R275.
        assert "model" not in fm
        assert "description" in fm and len(fm["description"]) > 40
        assert "temperature" in fm
        lower = text.lower()
        assert "sdd" in lower
        assert "tdd" in lower
        assert "anti-overclaim" in lower or "overclaim" in lower
        assert "scanner" in lower


def test_literary_research_agent_has_research_protocol():
    path = CATALOG / "literary-research-scholar-phd.md"
    text = path.read_text(encoding="utf-8").lower()
    for term in ["corpus", "bibliografia", "fontes", "teoria", "lacunas", "evidências", "citações", "comparação"]:
        assert term in text


def test_opencode_config_contains_literary_agents_after_generation():
    from integrations.opencode_cli import build_config

    config = build_config()
    agents = config.get("agent", {})
    for agent in EXPECTED_AGENTS:
        assert agent in agents
        assert agents[agent]["mode"] == "subagent"


def test_research_scanner_suite_contract():
    from scanners.literary_research_scanners import LITERARY_RESEARCH_SCANNER_CLASSES

    assert len(LITERARY_RESEARCH_SCANNER_CLASSES) == 4
    assert {cls.scanner_id for cls in LITERARY_RESEARCH_SCANNER_CLASSES} == EXPECTED_RESEARCH_SCANNERS
    for scanner_cls in LITERARY_RESEARCH_SCANNER_CLASSES:
        result = scanner_cls().scan(RICH_RESEARCH_TEXT)
        assert result["scanner_id"] == scanner_cls.scanner_id
        assert 0.0 <= result["score"] <= 100.0
        assert isinstance(result["dimensions"], dict)
        assert len(result["dimensions"]) >= 3
        assert isinstance(result["evidence"], list)
        assert isinstance(result["warnings"], list)
        assert isinstance(result["recommendations"], list)
        json.dumps(result, ensure_ascii=False)


def test_research_scanner_suite_scores_rich_above_weak_and_empty_safe():
    from scanners.literary_research_scanners import run_literary_research_scanner_suite

    rich = run_literary_research_scanner_suite(RICH_RESEARCH_TEXT, metadata={"project": "Molambudos"})
    weak = run_literary_research_scanner_suite(WEAK_RESEARCH_TEXT)
    empty = run_literary_research_scanner_suite("")
    assert rich["domain"] == "literary_research"
    assert rich["scanner_count"] == 4
    assert rich["international_research_rigor_score"] > weak["international_research_rigor_score"]
    assert empty["international_research_rigor_score"] == 0.0
    assert "não substitui" in rich["overclaim_guard"].lower()
    assert rich["metadata"]["project"] == "Molambudos"


def test_research_scanners_exported_from_package_root():
    from scanners import LiteraryBibliographyScanner, run_literary_research_scanner_suite

    result = LiteraryBibliographyScanner().scan(RICH_RESEARCH_TEXT)
    assert result["scanner_id"] == "literary_bibliography"
    assert run_literary_research_scanner_suite(RICH_RESEARCH_TEXT)["scanner_count"] == 4
