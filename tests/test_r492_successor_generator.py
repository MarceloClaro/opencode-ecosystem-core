# -*- coding: utf-8 -*-
"""Testes do Successor Generator (R492) — recombinação estrutural.

Proposta do usuário (camada Successor Generator): novas capacidades emergem da
recombinação de capacidades existentes (Motor+Asas+Controle → Avião). O gerador
produz hipóteses de sucessores a partir do DNA estrutural (R491), com bank
curado (exemplos do usuário) + combinação combinatoria controlada.

Anti-overclaim: sucessores são HIPÓTESES (não implementações).
Hermético, stdlib.
"""

from __future__ import annotations

import pathlib
import re

import pytest

from scanners.successor_generator import SuccessorGenerator, SuccessorHypothesis, SuccessorsReport

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODULE_TEXT = (ROOT / "scanners" / "successor_generator.py").read_text(encoding="utf-8")
BANNED = [r"\bsuperhuman\b", r"\bverificad[oa]s?\b", r"\bqualis a1\b", r"\bsuperação\b"]

ECO_MODULES = {
    "noological_scanner": ["gap_detection"],
    "teleological_scanner": ["target_definition"],
    "reverse_scanner": ["capacity_decomposition"],
    "trajectory_mapper": ["dependency_mapping", "trajectory_mapping"],
    "cross_validation_engine": ["cross_validation"],
    "polymathic_convergence": ["polymathic_reasoning", "cross_reference"],
    "knowledge_composition": ["input_decomposition"],
    "auto_evolve": ["self_evolution"],
    "mci_blackboard": ["multi_agent_coordination"],
    "trust_engine": ["evaluation"],
    "metabus": ["shared_memory"],
}


@pytest.fixture(scope="module")
def gen() -> SuccessorGenerator:
    return SuccessorGenerator(modules=ECO_MODULES)


# ═══════════════════════════════════════════════════════════════════════
# CA1-CA3 — bank curado (exemplos do usuário)
# ═══════════════════════════════════════════════════════════════════════

class TestBank:
    def test_potential_discovery_engine(self, gen):
        rep = gen.scan()
        assert rep.by_id["potential-discovery-engine"] is not None
        h = rep.by_id["potential-discovery-engine"]
        assert set(h.requires) >= {"gap_detection", "trajectory_mapping", "self_evolution"}
        assert "Potential Discovery Engine" in h.name

    def test_scientific_discovery_engine(self, gen):
        rep = gen.scan()
        h = rep.by_id["scientific-discovery-engine"]
        assert set(h.requires) >= {"cross_validation", "polymathic_reasoning", "trajectory_mapping"}

    def test_cognitive_manifold_mapper(self, gen):
        rep = gen.scan()
        h = rep.by_id["cognitive-manifold-mapper"]
        assert set(h.requires) >= {"gap_detection", "trajectory_mapping", "cross_validation"}
        assert "Cognitive Manifold" in h.name

    def test_typed_objects(self):
        h = SuccessorHypothesis(id="x", name="X", requires=["a"], description="d")
        assert h.id == "x"


# ═══════════════════════════════════════════════════════════════════════
# CA4-CA6 — geração combinatoria controlada
# ═══════════════════════════════════════════════════════════════════════

class TestGeneration:
    def test_generates_combos(self, gen):
        rep = gen.scan()
        assert len(rep.generated) > 0
        for h in rep.generated:
            assert len(h.requires) >= 2
            # módulos distintos: capabilities de módulos diferentes
            mods = set()
            for cap in h.requires:
                mods.update(m for m, caps in ECO_MODULES.items() if cap in caps)
            assert len(mods) >= 2, h

    def test_generated_not_in_bank(self, gen):
        rep = gen.scan()
        bank_sets = {frozenset(h.requires) for h in rep.bank}
        for h in rep.generated:
            assert frozenset(h.requires) not in bank_sets
            assert h.novelty == 1

    def test_max_combos_respected(self, gen):
        rep = gen.scan(max_combos=7)
        assert len(rep.generated) <= 7

    def test_ranking_sorted(self, gen):
        rep = gen.scan()
        scores = [h.score for h in rep.ranking]
        assert scores == sorted(scores, reverse=True)

    def test_determinism(self, gen):
        a = gen.scan()
        b = gen.scan()
        assert [h.id for h in a.ranking] == [h.id for h in b.ranking]


# ═══════════════════════════════════════════════════════════════════════
# CA7-CA9 — qualidade
# ═══════════════════════════════════════════════════════════════════════

class TestQuality:
    def test_no_anti_overclaim_module(self):
        for pattern in BANNED:
            assert not re.search(pattern, MODULE_TEXT, re.IGNORECASE), pattern

    def test_no_anti_overclaim_report(self, gen):
        rep = gen.scan()
        for pattern in BANNED:
            assert not re.search(pattern, str(rep), re.IGNORECASE), pattern

    def test_algorithm_documented(self):
        assert "SUCCESSOR_BANK" in MODULE_TEXT
        assert "diversity" in MODULE_TEXT
        assert "novelty" in MODULE_TEXT
        assert "hipótese" in MODULE_TEXT.lower() or "hipotese" in MODULE_TEXT.lower()

    def test_empty_modules_no_crash(self):
        g = SuccessorGenerator(modules={})
        rep = g.scan()
        assert rep.generated == []   # sem capabilities, sem combinações
        assert len(rep.bank) == 3    # banco curado independe do DNA
        assert rep.ranking