# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-935-R367 — benchmark cultural medido."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CORPUS = ROOT / "validacao_externa" / "cultural_episteme" / "benchmark_corpus_r367.json"
REPORT_JSON = ROOT / "validacao_externa" / "cultural_episteme" / "benchmark_r367_report.json"
REPORT_MD = ROOT / "validacao_externa" / "cultural_episteme" / "benchmark_r367_report.md"


def _load_corpus():
    with open(CORPUS, encoding="utf-8") as f:
        return json.load(f)


def _run():
    from scripts.benchmark_r367_cultural import run_benchmark
    return run_benchmark(str(CORPUS))


# ═══════════════════════════════════════════════════════════════════════
# 1. Corpus
# ═══════════════════════════════════════════════════════════════════════

class TestCorpus:
    def test_schema_e_tamanho_minimo(self):
        corpus = _load_corpus()
        assert corpus["schema_version"] == "1.0.0"
        assert corpus["claim"] == "internal-fixture-benchmark"
        cases = corpus["cases"]
        assert len(cases) >= 18
        by_module = {}
        for case in cases:
            assert case["module"] in {"terminology", "voice", "backtranslation"}
            assert isinstance(case["expected_codes"], list)
            by_module.setdefault(case["module"], []).append(case)
        for module, items in by_module.items():
            assert len(items) >= 4, module

    def test_case_ids_unicos(self):
        cases = _load_corpus()["cases"]
        ids = [c["case_id"] for c in cases]
        assert len(ids) == len(set(ids))

    def test_tem_negativos_e_limitacoes_conhecidas(self):
        cases = _load_corpus()["cases"]
        negatives = [c for c in cases if c["expected_codes"] == []]
        known_limits = [c for c in cases if c.get("known_limitation")]
        assert len(negatives) >= 3
        assert len(known_limits) >= 2


# ═══════════════════════════════════════════════════════════════════════
# 2. Runner e métricas
# ═══════════════════════════════════════════════════════════════════════

class TestRunner:
    def test_deterministico(self):
        r1, r2 = _run(), _run()
        r1.pop("generated_at"), r2.pop("generated_at")
        assert r1 == r2

    def test_enquadramento_honesto(self):
        report = _run()
        assert report["measured"] is True
        assert report["claim"] == "internal-fixture-benchmark"
        assert "não" in report["disclaimer"].lower()
        assert "validação externa" in report["disclaimer"].lower()
        assert report["corpus_size"] >= 18

    def test_metricas_no_intervalo(self):
        report = _run()
        for code, metrics in report["per_code"].items():
            for key in ("precision", "recall", "f1"):
                value = metrics[key]
                assert value is None or 0.0 <= value <= 1.0, (code, key, value)

    def test_recall_global_menor_que_um(self):
        """O corpus inclui limitações conhecidas: o benchmark deve mostrá-las."""
        report = _run()
        assert report["micro"]["recall"] < 1.0

    def test_sem_promessas_proibidas(self):
        report_text = json.dumps(_run(), ensure_ascii=False).lower()
        for forbidden in ("98%", "garantimos", "superhuman"):
            assert forbidden not in report_text


# ═══════════════════════════════════════════════════════════════════════
# 3. Relatórios versionados correspondem ao código atual
# ═══════════════════════════════════════════════════════════════════════

class TestRelatorioVersionado:
    def test_json_versionado_atualizado(self):
        report = _run()
        with open(REPORT_JSON, encoding="utf-8") as f:
            saved = json.load(f)
        report.pop("generated_at")
        saved.pop("generated_at")
        assert saved == report

    def test_md_existe_com_disclaimer(self):
        text = REPORT_MD.read_text(encoding="utf-8").lower()
        assert "não constitui" in text or "nao constitui" in text
        assert "corpus interno" in text
