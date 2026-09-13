# -*- coding: utf-8 -*-
"""Testes da Paisagem Acadêmica (R489).

Manifest ganha chave `academic` (4 fontes Apache-2.0 DeepMind+science-skills) e
o PolymathicConvergence passa a cruzar agents + academic nas lacunas
epistemológicas (cobertura zero observada na demo R486).

Anti-overclaim: 'superhuman' é NOME da fonte (id/título), nunca veredicto.
"""

from __future__ import annotations

import json
import pathlib
import re

import pytest

from scanners.polymathic_convergence import PolymathicConvergence

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODULE_TEXT = (ROOT / "scanners" / "polymathic_convergence.py").read_text(encoding="utf-8")
MANIFEST = json.loads((ROOT / "landscape" / "manifest.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def pc() -> PolymathicConvergence:
    return PolymathicConvergence()  # default: manifest real


# ═══════════════════════════════════════════════════════════════════════

class TestManifest:
    def test_academic_sources_present(self):
        ac = MANIFEST.get("academic", [])
        assert len(ac) >= 4
        ids = {a["id"] for a in ac}
        assert {"deepmind-superhuman", "deepmind-alphageometry",
                "deepmind-alphageometry2", "deepmind-science-skills"} <= ids

    def test_all_apache2_and_audited(self):
        for a in MANIFEST.get("academic", []):
            assert a["license"] == "Apache-2.0"
            assert a["source_repo"].startswith("https://github.com/google-deepmind/")

    def test_default_index_24(self, pc):
        assert pc.agents  # 20 agents carregados
        report = pc.scan({}, target_state=["x.y"])
        total = report.params.get("agents_indexed")
        assert total == 25  # 20 agents + 5 acadêmicas (4 DeepMind + acme R497)


class TestCross:
    def test_academic_match_deductive(self, pc):
        # lacuna de raciocínio formal => superhuman/alphageometry
        matches = pc.match_capability("raciocinio.prova geométrica", top_k=3)
        assert matches
        tops = [m.agent_id for m in matches]
        any_academic = any(m.source.startswith("academic:") for m in matches)
        assert any_academic
        assert any("alphageometry" in a for a in tops) or any("superhuman" in a for a in tops)

    def test_academic_match_literature(self, pc):
        matches = pc.match_capability("literature.pubmed", top_k=3)
        assert any(m.agent_id == "deepmind-science-skills" for m in matches)

    def test_source_tag_academic(self, pc):
        matches = pc.match_capability("geometria.prova", top_k=5)
        assert any(m.source.startswith("academic:") for m in matches)

    def test_scan_gap_meta_has_academic(self, pc):
        scan = {"dimensions": {
            "raciocinio": {"covered": [], "absent": ["Prova geométrica"]},
            "metodos": {"covered": [], "absent": ["Meta-análise"]},
        }}
        report = pc.scan(scan, target_state=["raciocinio.Prova geométrica"])
        gap = "raciocinio.Prova geométrica"
        assert report.evolution_gap == [gap]
        assert report.by_capability.get(gap, []), "lacuna epistemológica sem match"
        assert any(m.source.startswith("academic:") for m in report.by_capability[gap])


class TestAntiOverclaim:
    def test_no_superhuman_verdict(self, pc):
        scan = {"dimensions": {"raciocinio": {"covered": [], "absent": ["Prova geométrica"]}}}
        report = pc.scan(scan, target_state=["raciocinio.Prova geométrica"])
        # o termo pode aparecer no id da FONTE, nunca como capacidade/veredicto
        for match in report.matches:
            assert "superhuman" not in match.capability.lower()
            # descrição pode citar o nome do repo (fonte) — sem juízo
        assert "superhuman" in MODULE_TEXT or "superhuman" in str(MANIFEST.get("academic", [])[:1])

    def test_report_no_superhuman_judgement(self, pc):
        scan = {"dimensions": {"raciocinio": {"covered": [], "absent": ["Prova geométrica"]}}}
        report = pc.scan(scan, target_state=["raciocinio.Prova geométrica"])
        txt = str(report).lower()
        # nenhuma frase de veredicto usando o rótulo
        for forbidden in ("capacidade superhuman", "resultado superhuman", "nível superhuman"):
            assert forbidden not in txt


class TestRegression:
    def test_r486_fixture_style_still_works(self, tmp_path):
        import json as _json
        fixture = {"agents": [
            {"id": "01-web-research", "title": "Agente de Pesquisa Web",
             "industry": "Research/Web", "framework": "langgraph",
             "dependencies": ["tavily"], "env_required": [],
             "swift": "Sintetiza fontes.", "reference_url": "x", "license": "MIT"},
        ]}
        p = tmp_path / "m.json"
        p.write_text(_json.dumps(fixture), encoding="utf-8")
        pc2 = PolymathicConvergence(manifest_path=p)
        assert len(pc2.agents) == 1
        assert not pc2.warnings
        assert pc2.match_capability("web", top_k=3)[0].agent_id == "01-web-research"