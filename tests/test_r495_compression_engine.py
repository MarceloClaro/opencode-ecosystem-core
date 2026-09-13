# -*- coding: utf-8 -*-
"""Testes do Structural Compression Engine (R495).

Proposta do usuário: ferramenta que comprime textos gigantes preservando a
estrutura cognitiva essencial. Pipeline: fragmentação → SNS por parte →
vetores cognitivos → reconstrução global → teste delta.
Métricas: CR (Compression Ratio), CPS (Cognitive Preservation Score), FLI,
DG = CPS × CR. Hermético, stdlib, anti-overclaim.
"""

from __future__ import annotations

import pathlib
import re

import pytest

from scanners.compression_engine import SCEReport, StructuralCompressionEngine

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODULE_TEXT = (ROOT / "scanners" / "compression_engine.py").read_text(encoding="utf-8")
BANNED = [r"\bsuperhuman\b", r"\bverificad[oa]s?\b", r"\bqualis a1\b", r"\bsuperação\b"]

CORPUS = (
    "A metacognição supervisiona os agentes do ecossistema e coordena as "
    "decisões de roteamento. A metacognição supervisiona os agentes do "
    "ecossistema e coordena as decisões de roteamento. A metacognição "
    "supervisiona os agentes do ecossistema e coordena as decisões de "
    "roteamento. O feedback e a memória compartilhada alimentam a "
    "metacognição em tempo real. O feedback e a memória compartilhada "
    "alimentam a metacognição em tempo real."
)

UNIQUE_CORPUS = (
    "A metacognição supervisiona os agentes do ecossistema. "
    "O feedback alimenta o roteamento. A memória compartilhada persiste "
    "os estados entre ciclos."
)


# ═══════════════════════════════════════════════════════════════════════
# CA1-CA3 — métricas
# ═══════════════════════════════════════════════════════════════════════

class TestMetrics:
    def test_cr(self):
        sce = StructuralCompressionEngine()
        rep = sce.compress(CORPUS)
        assert rep.cr >= 1.0
        assert rep.cr == pytest.approx(
            rep.tokens_original / rep.tokens_final, abs=1e-4)

    def test_cps(self):
        sce = StructuralCompressionEngine()
        rep = sce.compress(CORPUS)
        assert 0.0 <= rep.cps <= 1.0

    def test_fli_and_dg(self):
        sce = StructuralCompressionEngine()
        rep = sce.compress(CORPUS)
        assert rep.fli == pytest.approx(1 - rep.cps, abs=1e-4)
        assert rep.dg == pytest.approx(rep.cps * rep.cr, abs=1e-4)


# ═══════════════════════════════════════════════════════════════════════
# CA4-CA6 — fragmentação, SNS por parte, reconstrução
# ═══════════════════════════════════════════════════════════════════════

class TestPipeline:
    def test_fragment_respects_sentence_boundaries(self):
        sce = StructuralCompressionEngine()
        parts = sce.fragment(CORPUS, chunk_chars=80)
        for part in parts:
            assert len(part) <= 80 + 60  # tolerância de fronteira de frase
            assert part.strip()
        joined = " ".join(parts)
        assert joined.replace(" ", "") == CORPUS.replace(" ", "") \
            or set(joined.split()) == set(CORPUS.split())

    def test_sns_per_part_preserves_structure(self):
        sce = StructuralCompressionEngine()
        rep = sce.compress(CORPUS)
        assert rep.parts_processed == len(sce.fragment(CORPUS))
        assert rep.n_elements_original >= rep.n_elements_final

    def test_final_text_contains_essential_functions(self):
        sce = StructuralCompressionEngine()
        rep = sce.compress(CORPUS)
        final = rep.compressed_text
        for keyword in ("metacognição", "agentes", "feedback"):
            assert keyword.lower() in final.lower() or \
                keyword.lower() in " ".join(rep.functions_preserved).lower()


# ═══════════════════════════════════════════════════════════════════════
# CA7-CA10 — qualidade
# ═══════════════════════════════════════════════════════════════════════

class TestQuality:
    def test_no_anti_overclaim_module(self):
        for pattern in BANNED:
            assert not re.search(pattern, MODULE_TEXT, re.IGNORECASE), pattern

    def test_algorithm_documented(self):
        for term in ("CR", "CPS", "FLI", "DG", "fragment", "vetor"):
            assert term.lower() in MODULE_TEXT.lower(), term

    def test_safe_level_with_repetition(self):
        sce = StructuralCompressionEngine()
        rep = sce.compress(CORPUS)
        assert rep.level in ("seguro", "moderado")
        assert rep.cr > 1.0
        assert rep.fli < 0.40

    def test_determinism_and_empty(self):
        sce = StructuralCompressionEngine()
        a = sce.compress(CORPUS)
        b = sce.compress(CORPUS)
        assert a.compressed_text == b.compressed_text
        empty = sce.compress("")
        assert empty.compressed_text == ""
        assert empty.tokens_final == 0


# ═══════════════════════════════════════════════════════════════════════
# CA11-CA12 — compressão efetiva e delta
# ═══════════════════════════════════════════════════════════════════════

class TestEffective:
    def test_repetition_compresses(self):
        sce = StructuralCompressionEngine()
        rep = sce.compress(CORPUS)
        assert rep.cr > 1.0
        assert rep.cps >= 0.5

    def test_delta_report(self):
        sce = StructuralCompressionEngine()
        rep = sce.compress(CORPUS)
        assert rep.tokens_original > 0
        assert rep.tokens_saved == rep.tokens_original - rep.tokens_final
        assert rep.tokens_saved > 0  # corpus com repetição gera economia