# -*- coding: utf-8 -*-
"""Testes da Convergência Polimática (R486).

Progressão: ERRO → AUSÊNCIA → OPORTUNIDADE → REVERSO (R483) → TRAJETÓRIAS (R485)
→ CONVERGÊNCIA POLIMÁTICA (R486).

Cruza cada g ∈ Δ com o landscape/manifest.json (R482, 20 agentes externos MIT)
por sobreposição léxica ponderada: quem já resolveu parte disso fora do domínio.

Hermético: sem rede, sem credenciais, sem código de terceiros.
"""

from __future__ import annotations

import json
import pathlib
import re

import pytest

from scanners.polymathic_convergence import (
    ConvergenceReport,
    PolymathicConvergence,
    PolymathicMatch,
)

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODULE_TEXT = (ROOT / "scanners" / "polymathic_convergence.py").read_text(encoding="utf-8")
BANNED = [r"\bsuperhuman\b", r"\bverificad[oa]s?\b", r"\bqualis a1\b", r"\bsuperação\b"]

# Fixture de manifest controlada (2 agentes)
FIXTURE_MANIFEST = {
    "collection": "teste",
    "license": "MIT",
    "agents": [
        {
            "id": "01-web-research",
            "title": "Agente de Pesquisa Web",
            "industry": "Research/Web",
            "framework": "langgraph",
            "dependencies": ["tavily"],
            "env_required": [],
            "swift": "Sintetiza múltiplas fontes da internet.",
            "reference_url": "https://example.invalid/01",
            "license": "MIT",
        },
        {
            "id": "02-meta-analysis",
            "title": "Agente de Meta-análise Estatística",
            "industry": "Healthcare/Research",
            "framework": "scikit-learn",
            "dependencies": ["statsmodels"],
            "env_required": [],
            "swift": "Calcula effect sizes e forest plots.",
            "reference_url": "https://example.invalid/02",
            "license": "MIT",
        },
        {
            "id": "03-web-scraper",
            "title": "Web Scraper Rápido",
            "industry": "Web",
            "framework": "langgraph",
            "dependencies": ["requests"],
            "env_required": [],
            "swift": "Coleta páginas da internet.",
            "reference_url": "https://example.invalid/03",
            "license": "MIT",
        },
    ],
}


@pytest.fixture(scope="module")
def fixture_manifest(tmp_path_factory) -> pathlib.Path:
    p = tmp_path_factory.mktemp("manifests") / "manifest.json"
    p.write_text(json.dumps(FIXTURE_MANIFEST), encoding="utf-8")
    return p


@pytest.fixture(scope="module")
def conv(fixture_manifest) -> PolymathicConvergence:
    return PolymathicConvergence(manifest_path=fixture_manifest)


@pytest.fixture(scope="module")
def synthetic_scan() -> dict:
    return {
        "dimensions": {
            "metodos": {
                "covered": ["Quantitativo experimental", "Revisão sistemática"],
                "absent": ["Meta-análise"],
            },
            "raciocinio": {
                "covered": ["Dedutivo"],
                "absent": ["Probabilístico"],
            },
            "dados": {
                "covered": [],
                "absent": ["Metadados (revisões)"],
            },
            "temporalidade": {
                "covered": [],
                "absent": ["Longitudinal (longo prazo)"],
            },
        }
    }


# ═══════════════════════════════════════════════════════════════════════
# CA1-CA3 — Match e scoring em fixture
# ═══════════════════════════════════════════════════════════════════════

class TestMatching:
    def test_finds_correct_agent(self, conv):
        matches = conv.match_capability("metodos.meta-análise", top_k=3)
        assert matches
        assert matches[0].agent_id == "02-meta-analysis"
        # apenas o campo title casa ("meta"+"análise") => score = 2.0/7.5
        assert matches[0].score == pytest.approx(2.0 / 7.5, abs=1e-3)

    def test_score_between_0_1(self, conv):
        for top in (1, 3):
            for m in conv.match_capability("raciocinio.probabilístico", top_k=top):
                assert 0.0 <= m.score <= 1.0

    def test_top_k_respected_and_deterministic(self, conv):
        # "web" casa com 01 (title+industry) e 03 (title+industry), empate 0.5333
        m1 = conv.match_capability("web", top_k=1)
        m3 = conv.match_capability("web", top_k=3)
        assert len(m1) == 1
        assert len(m3) == 2
        # desempate determinístico: agent_id asc (01 antes de 03)
        assert [m.agent_id for m in m3] == ["01-web-research", "03-web-scraper"]

    def test_field_weights_influence(self, conv):
        # "web" está no title (peso 2) E no industry (peso 2) do 01
        m = conv.match_capability("web", top_k=3)
        top = m[0]
        assert top.agent_id == "01-web-research"
        # campos title+industry casam => score = (2+2) / (2+2+1.5+1+1) = 0.5333
        assert top.score == pytest.approx(4.0 / 7.5, abs=1e-3)

    def test_match_has_overlap_terms(self, conv):
        m = conv.match_capability("metodos.meta-análise", top_k=1)[0]
        assert "meta" in m.overlap_terms or "meta-análise" in m.overlap_terms


# ═══════════════════════════════════════════════════════════════════════
# CA4/CA5 — Integração e manifest real
# ═══════════════════════════════════════════════════════════════════════

class TestIntegration:
    def test_convergence_per_gap(self, conv, synthetic_scan):
        report = conv.scan(synthetic_scan, target_state=["metodos.Meta-análise"])
        assert isinstance(report, ConvergenceReport)
        assert report.evolution_gap
        for gap in report.evolution_gap:
            assert gap in report.by_capability
            for match in report.by_capability[gap]:
                assert match.capability == gap
                assert isinstance(match, PolymathicMatch)

    def test_convergence_meta_analysis_gap(self, conv, synthetic_scan):
        report = conv.scan(synthetic_scan, target_state=["metodos.Meta-análise"])
        matches = report.by_capability.get("metodos.Meta-análise", [])
        assert matches
        assert matches[0].agent_id == "02-meta-analysis"

    def test_real_manifest_loads(self):
        pc = PolymathicConvergence()  # default: landscape/manifest.json
        assert len(pc.agents) == 20
        assert not pc.warnings

    def test_real_manifest_cross(self, synthetic_scan):
        pc = PolymathicConvergence()
        report = pc.scan(synthetic_scan, target_state=["metodos.Meta-análise"])
        assert report.params["source"].endswith("landscape/manifest.json")
        # pelo menos uma lacuna tem match (dataset real cobre pesquisa/meta)
        assert any(report.by_capability.values())


# ═══════════════════════════════════════════════════════════════════════
# CA6-CA10 — Qualidade
# ═══════════════════════════════════════════════════════════════════════

class TestQuality:
    def test_missing_manifest_fail_soft(self, tmp_path):
        pc = PolymathicConvergence(manifest_path=tmp_path / "nao-existe.json")
        assert pc.agents == []
        assert pc.warnings
        report = pc.scan({}, target_state=["x.y"])
        assert report.matches == []

    def test_determinism(self, conv, synthetic_scan):
        a = conv.scan(synthetic_scan, target_state=["metodos.Meta-análise"])
        b = conv.scan(synthetic_scan, target_state=["metodos.Meta-análise"])
        assert a.matches == b.matches
        assert a.by_capability == b.by_capability

    def test_no_targets(self, conv):
        report = conv.scan({}, target_state=[])
        assert report.matches == []
        assert report.evolution_gap == []

    def test_no_anti_overclaim_module(self):
        for pattern in BANNED:
            assert not re.search(pattern, MODULE_TEXT, re.IGNORECASE), pattern

    def test_no_anti_overclaim_report(self, conv, synthetic_scan):
        report = conv.scan(synthetic_scan, target_state=["metodos.Meta-análise"])
        for pattern in BANNED:
            assert not re.search(pattern, str(report), re.IGNORECASE), pattern

    def test_algorithm_documented(self):
        assert "score" in MODULE_TEXT
        assert "peso" in MODULE_TEXT
        assert "title" in MODULE_TEXT
        assert "manifest.json" in MODULE_TEXT