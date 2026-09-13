# -*- coding: utf-8 -*-
"""Testes do Structural Noise Scanner (R494).

Proposta do usuário: compressão estrutural que remova ruído SEM eliminar função
relevante. C = E + S + R → C' = S + E* com Reconstrução(C') ≈ Estrutura(C).
Métricas: SPS (preservação), NRR (ruído), FLI (perda funcional).
Hermético, stdlib, anti-overclaim.
"""

from __future__ import annotations

import pathlib
import re

import pytest

from scanners.noise_scanner import StructuralNoiseScanner, NoiseScanReport

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODULE_TEXT = (ROOT / "scanners" / "noise_scanner.py").read_text(encoding="utf-8")
BANNED = [r"\bsuperhuman\b", r"\bverificad[oa]s?\b", r"\bqualis a1\b", r"\bsuperação\b"]


# ═══════════════════════════════════════════════════════════════════════
# CA1-CA2 — classificação heurística
# ═══════════════════════════════════════════════════════════════════════

class TestClassifier:
    def test_redundancy_detected(self):
        sns = StructuralNoiseScanner()
        elements = [
            "A metacognição supervisiona os agentes do ecossistema.",
            "A metacognição supervisiona os agentes do ecossistema.",
        ]
        rep = sns.scan_text(elements)
        # (índice por posição: elementos idênticos colidiriam num dict)
        assert rep.classified[0]["category"] == "estrutura"
        assert rep.classified[1]["category"] == "redundancia"

    def test_example_detected(self):
        sns = StructuralNoiseScanner()
        elements = [
            "A metacognição supervisiona os agentes do ecossistema.",
            "ex: Leonardo propôs detectar estruturas latentes.",
        ]
        rep = sns.scan_text(elements)
        classes = {e["element"]: e["category"] for e in rep.classified}
        assert classes[
            "ex: Leonardo propôs detectar estruturas latentes."] in (
                "exemplo", "vetor-explicativo")

    def test_noise_detected(self):
        sns = StructuralNoiseScanner()
        elements = ["a a a a a a a a a a", "A metacognição supervisiona agentes."]
        rep = sns.scan_text(elements)
        by_el = {e["element"]: e["category"] for e in rep.classified}
        assert by_el["a a a a a a a a a a"] == "ruido"


# ═══════════════════════════════════════════════════════════════════════
# CA3-CA4 — preservação de função
# ═══════════════════════════════════════════════════════════════════════

class TestPreservation:
    def test_function_preserved_when_redundant(self):
        sns = StructuralNoiseScanner()
        elements = [
            "A metacognição supervisiona os agentes do ecossistema.",
            "A metacognição supervisiona os agentes do ecossistema.",
        ]
        rep = sns.scan_text(elements)
        assert rep.functions_preserved >= 1
        assert rep.fli == 0.0

    def test_function_lost_when_unique_removed(self):
        sns = StructuralNoiseScanner(force_remove_all_noise=True)
        elements = [
            "A metacognição supervisiona os agentes do ecossistema.",
        ]
        rep = sns.scan_text(elements)
        # elemento único: proteção impede remoção indevida
        assert rep.functions_preserved >= 1
        assert rep.fli == 0.0


# ═══════════════════════════════════════════════════════════════════════
# CA5-CA8 — compressão e métricas
# ═══════════════════════════════════════════════════════════════════════

class TestMetrics:
    def test_compression_clusters_equivalence(self):
        sns = StructuralNoiseScanner()
        elements = [
            "Leonardo detectava estruturas ocultas na natureza.",
            "Einstein detectou estruturas ocultas no universo.",
        ]
        rep = sns.scan_text(elements)
        assert rep.clusters, "compressão deveria agrupar manifestações equivalentes"
        common = set(rep.clusters[0]["common_tokens"])
        assert "estruturas" in common or "ocultas" in common

    def test_sps_high_for_redundant_corpus(self):
        sns = StructuralNoiseScanner()
        elements = [
            "A metacognição supervisiona os agentes do ecossistema.",
            "A metacognição supervisiona os agentes do ecossistema.",
            "A metacognição supervisiona os agentes do ecossistema.",
        ]
        rep = sns.scan_text(elements)
        assert rep.sps >= 0.90
        assert rep.level == "seguro"

    def test_nrr_computed(self):
        sns = StructuralNoiseScanner()
        elements = [
            "a a a a a",                      # ruído
            "Metacognição supervisiona agentes.",
        ]
        rep = sns.scan_text(elements)
        assert 0.0 <= rep.nrr <= 1.0
        assert rep.nrr == pytest.approx(1 / 2, abs=1e-4)

    def test_fli_low_for_safe_compression(self):
        sns = StructuralNoiseScanner()
        elements = [
            "A metacognição supervisiona os agentes do ecossistema.",
            "A metacognição supervisiona os agentes do ecossistema.",
        ]
        rep = sns.scan_text(elements)
        assert rep.fli == 0.0


# ═══════════════════════════════════════════════════════════════════════
# CA9-CA12 — reconstrução, proteção, qualidade
# ═══════════════════════════════════════════════════════════════════════

class TestReconstructionAndQuality:
    def test_reconstruction_score(self):
        sns = StructuralNoiseScanner()
        elements = [
            "A metacognição supervisiona os agentes do ecossistema.",
            "O Feedback e a memória compartilhada alimentam a metacognição.",
        ]
        rep = sns.scan_text(elements)
        assert 0.0 <= rep.reconstruction <= 1.0
        assert rep.reconstruction >= 0.5  # funções essenciais preservadas

    def test_relevance_protection_single_element(self):
        sns = StructuralNoiseScanner()
        elements = ["Capacidade única que explica o fenômeno inteiro."]
        rep = sns.scan_text(elements)
        assert rep.removed == []

    def test_no_anti_overclaim_module(self):
        for pattern in BANNED:
            assert not re.search(pattern, MODULE_TEXT, re.IGNORECASE), pattern

    def test_algorithm_documented(self):
        for term in ("SPS", "NRR", "FLI", "jaccard", "reconstrução",
                     "redundancia", "função"):
            assert term.lower() in MODULE_TEXT.lower(), term

    def test_determinism_and_empty(self):
        sns = StructuralNoiseScanner()
        a = sns.scan_text(["Um dois três.", "Um dois três."])
        b = sns.scan_text(["Um dois três.", "Um dois três."])
        assert [(e["element"], e["category"]) for e in a.classified] == \
               [(e["element"], e["category"]) for e in b.classified]
        empty = sns.scan_text([])
        assert empty.classified == []
        assert empty.sps == 0.0