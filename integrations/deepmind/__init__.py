# -*- coding: utf-8 -*-
"""
DeepMind Superhuman Reasoning & Aletheia Integration — SPEC-935-R442
====================================================================
Módulo de integração dos paradigmas de raciocínio científico avançado,
verificação formal e benchmarking do Google DeepMind.
"""

from integrations.deepmind.aletheia_scaffold import (
    AletheiaDecomposition,
    AletheiaHypothesisEngine,
    AletheiaLatexFormatter,
    AletheiaLemma,
)
from integrations.deepmind.formal_verifier import (
    FormalProofVerifier,
    FormalVerificationResult,
    VerificationStep,
)
from integrations.deepmind.imobench_harness import (
    GradingHeadDeepMind,
    IMOBenchmarkHarness,
    IMOEvalResult,
    IMOProblem,
)

__all__ = [
    "AletheiaHypothesisEngine",
    "AletheiaDecomposition",
    "AletheiaLemma",
    "AletheiaLatexFormatter",
    "FormalProofVerifier",
    "FormalVerificationResult",
    "VerificationStep",
    "IMOBenchmarkHarness",
    "GradingHeadDeepMind",
    "IMOProblem",
    "IMOEvalResult",
]
