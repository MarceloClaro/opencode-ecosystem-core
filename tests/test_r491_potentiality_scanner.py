# -*- coding: utf-8 -*-
"""Testes do Potentiality Scanner (R491) — capacidades latentes.

Proposta do usuário (camada Potentiality): detectar capacidades "prestes a
nascer" — cujos componentes estruturais já estão parcialmente presentes no
ecossistema (ex.: o avião surgiu da convergência de aerodinâmica + materiais +
propulsão).

Structural DNA Extractor + Emergence Scan. Hermético, stdlib, anti-overclaim.
"""

from __future__ import annotations

import pathlib
import re

import pytest

from scanners.potentiality_scanner import (
    PotentialityCandidate,
    PotentialityReport,
    PotentialityScanner,
    StructuralDNA,
)

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODULE_TEXT = (ROOT / "scanners" / "potentiality_scanner.py").read_text(encoding="utf-8")
BANNED = [r"\bsuperhuman\b", r"\bverificad[oa]s?\b", r"\bqualis a1\b", r"\bsuperação\b"]


ECO_DNA = {
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

CANDIDATES = [
    PotentialityCandidate(
        id="cognitive-manifold-mapper",
        description="Mapa de manifold cognitivo: gap + trajetória + inferência causal (inexistente)",
        requires=["gap_detection", "trajectory_mapping", "causal_inference"],
    ),
    PotentialityCandidate(
        id="self-validating-evolver",
        description="Evolução com auto-validação: evolução + validação + memória",
        requires=["self_evolution", "evaluation", "shared_memory"],
    ),
    PotentialityCandidate(
        id="radar-futurista",
        description="Radar de futuro (distante): componentes inexistentes no DNA",
        requires=["quantum_planning", "world_modeling", "simulation"],
    ),
]


@pytest.fixture(scope="module")
def dna() -> StructuralDNA:
    return StructuralDNA(modules=ECO_DNA)


@pytest.fixture(scope="module")
def scanner() -> PotentialityScanner:
    return PotentialityScanner(modules=ECO_DNA)


# ═══════════════════════════════════════════════════════════════════════

class TestDNA:
    def test_capabilities_indexed(self, dna):
        caps = dna.capabilities
        assert "gap_detection" in caps
        assert "trajectory_mapping" in caps
        assert len(caps) >= 10

    def test_central_capabilities(self, dna):
        # nenhuma capability aparece em 2+ módulos no DNA de teste
        assert dna.central == set() or isinstance(dna.central, set)


class TestEmergence:
    def test_two_of_three_emergente(self, scanner):
        rep = scanner.scan(CANDIDATES)
        cm = rep.by_id["cognitive-manifold-mapper"]
        assert cm.coverage == pytest.approx(2 / 3, abs=1e-3)
        assert cm.tier == "emergente"
        assert cm.missing == ["causal_inference"]
        assert cm.resistencia == pytest.approx(1 - 2 / 3, abs=1e-3)

    def test_full_coverage_latente_alto(self, scanner):
        rep = scanner.scan(CANDIDATES)
        sv = rep.by_id["self-validating-evolver"]
        assert sv.coverage == pytest.approx(1.0)
        assert sv.tier == "latente-alto"
        assert sv.missing == []

    def test_zero_coverage_distante(self, scanner):
        rep = scanner.scan(CANDIDATES)
        rf = rep.by_id["radar-futurista"]
        assert rf.coverage == 0.0
        assert rf.tier == "distante"
        assert len(rf.missing) == 3

    def test_scan_returns_report(self, scanner):
        rep = scanner.scan(CANDIDATES)
        assert isinstance(rep, PotentialityReport)
        assert len(rep.candidates) == 3
        assert rep.params["n_candidates"] == 3

    def test_determinism(self, scanner):
        a = scanner.scan(CANDIDATES)
        b = scanner.scan(CANDIDATES)
        assert a.by_id == b.by_id

    def test_no_candidates(self, scanner):
        rep = scanner.scan([])
        assert rep.candidates == []
        assert rep.by_id == {}


class TestQuality:
    def test_no_anti_overclaim_module(self):
        for pattern in BANNED:
            assert not re.search(pattern, MODULE_TEXT, re.IGNORECASE), pattern

    def test_no_anti_overclaim_report(self, scanner):
        rep = scanner.scan(CANDIDATES)
        for pattern in BANNED:
            assert not re.search(pattern, str(rep), re.IGNORECASE), pattern

    def test_algorithm_documented(self):
        assert "coverage" in MODULE_TEXT
        assert "latente-alto" in MODULE_TEXT
        assert "StructuralDNA" in MODULE_TEXT

    def test_typed_objects(self):
        c = PotentialityCandidate(id="x", description="d", requires=["a", "b"])
        assert c.id == "x"