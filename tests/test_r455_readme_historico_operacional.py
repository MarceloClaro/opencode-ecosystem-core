"""Contratos documentais da SPEC-935-R455."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
ARCH = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")


def _section(text: str, heading: str, next_heading: str | None = None) -> str:
    start = text.index(heading)
    end = text.index(next_heading, start) if next_heading else len(text)
    return text[start:end]


def test_readme_preserves_historical_map_as_snapshot() -> None:
    historical = _section(
        README,
        "### Mapa da Arquitetura Completa (v3.9.0)",
        "### Diagrama Operacional Atual",
    )

    assert "snapshot histórico" in historical.lower() or "snapshot documental" in historical.lower()
    assert "não é um inventário do checkout" in historical.lower()
    assert "MiraDeckPipeline" in historical
    assert "mira-presenter" in historical


def test_readme_adds_current_operational_diagram() -> None:
    current = _section(
        README,
        "### Diagrama Operacional Atual",
        "## Apresentações MIRA",
    )

    assert "```mermaid" in current
    assert "AttentionRouter" in current
    assert "SpecRegistry" in current
    assert "SpecVerifier" in current
    assert "TDDRunner" in current


def test_current_diagram_matches_runtime_components() -> None:
    current = _section(
        README,
        "### Diagrama Operacional Atual",
        "## Apresentações MIRA",
    )

    for marker in (
        "CLI marceloclaro",
        "MarceloClaroOrchestrator",
        "AttentionRouter",
        "SpecRegistry",
        "SpecVerifier",
        "TDDRunner",
        "MetaBus",
        "Blackboard",
        "6 MCPs configurados",
        "209 agentes configurados",
        "mira-presenter",
    ):
        assert marker in current, marker


def test_readme_distinguishes_summary_from_runtime_inventory() -> None:
    summary = _section(README, "## Arquitetura resumida", "## Apresentações MIRA")

    assert "visão resumida" in summary.lower() or "arquitetura resumida" in summary.lower()
    assert "snapshot histórico" in summary.lower() or "snapshot documental" in summary.lower()
    assert "diagrama operacional atual" in summary.lower()


def test_architecture_doc_remains_consistent_with_readme() -> None:
    current = _section(
        README,
        "### Diagrama Operacional Atual",
        "## Apresentações MIRA",
    )

    for marker in (
        "MarceloClaroOrchestrator",
        "SpecRegistry",
        "SpecVerifier",
        "MetaBus",
        "Blackboard",
        "mira-presenter",
    ):
        assert marker in current
        assert marker in ARCH


def test_readme_restores_multiarea_richness() -> None:
    for marker in (
        "Fluxos multiárea do checkout atual",
        "Pipeline acadêmico agentivo",
        "Prova, formalização e raciocínio",
        "Jurídico",
        "Clínico",
        "Scientific RAG",
        "Universidade Sintética",
        "LiteRT-LM",
        "Colibri / OLMoE",
        "MerkleIntegrityGuard",
        "quality_report.py",
    ):
        assert marker in README, marker
    assert README.count("```mermaid") >= 6


def test_docs_remain_conservative() -> None:
    current = _section(
        README,
        "### Diagrama Operacional Atual",
        "## Apresentações MIRA",
    ).lower()

    for forbidden in ("certificação externa", "superhuman", "garantia absoluta"):
        assert forbidden not in current
    assert "serviços externos" in README.lower()
    assert "doctor" in README.lower()
