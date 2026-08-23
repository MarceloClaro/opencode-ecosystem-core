# -*- coding: utf-8 -*-
"""
DeepMind Superhuman Reasoning & Aletheia Integration — SPEC-935-R442 / R443 / R444
===================================================================================
Módulo de integração dos paradigmas de raciocínio científico avançado:
- OpenCode AlphaProof (Proof-Tree Search & Táticas Formais)
- OpenCode Deep Think (Test-Time Compute & Trajetórias MCTS)
- Aletheia Scaffold & LaTeX Formatter
- Erdős & Hirzebruch Open Problems Solvers
- Lean 4 Formal Proof Bridge & Verifier
- E-Graph & Equality Saturation Engine (Egglog Paradigm)
- IMO Bench Harness & DeepMind Grading Head
- Formal Proof Verifier (SymPy + Z3)
"""

from integrations.deepmind.aletheia_scaffold import (
    AletheiaDecomposition,
    AletheiaHypothesisEngine,
    AletheiaLatexFormatter,
    AletheiaLemma,
)
from integrations.deepmind.alphaproof_engine import (
    OpenCodeAlphaProof,
    PrioritizedProofNode,
    ProofState,
)
from integrations.deepmind.deep_think_engine import (
    OpenCodeDeepThink,
    ReasoningTrajectory,
)
from integrations.deepmind.egraph_rewriter import (
    EClass,
    EGraph,
    ENode,
    EqualitySaturationEngine,
)
from integrations.deepmind.erdos_hirzebruch_solver import (
    ErdosProofResult,
    ErdosSeriesAnalyzer,
    HirzebruchEigenweightCalculator,
    HirzebruchResult,
    OpenProblemsResearchWorkflow,
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
from integrations.deepmind.lean4_verifier import (
    Lean4ProofVerifier,
    Lean4VerificationResult,
)

__all__ = [
    "AletheiaHypothesisEngine",
    "AletheiaDecomposition",
    "AletheiaLemma",
    "AletheiaLatexFormatter",
    "OpenCodeAlphaProof",
    "ProofState",
    "PrioritizedProofNode",
    "OpenCodeDeepThink",
    "ReasoningTrajectory",
    "ErdosSeriesAnalyzer",
    "ErdosProofResult",
    "HirzebruchEigenweightCalculator",
    "HirzebruchResult",
    "OpenProblemsResearchWorkflow",
    "FormalProofVerifier",
    "FormalVerificationResult",
    "VerificationStep",
    "IMOBenchmarkHarness",
    "GradingHeadDeepMind",
    "IMOProblem",
    "IMOEvalResult",
    "Lean4ProofVerifier",
    "Lean4VerificationResult",
    "EGraph",
    "ENode",
    "EClass",
    "EqualitySaturationEngine",
]
