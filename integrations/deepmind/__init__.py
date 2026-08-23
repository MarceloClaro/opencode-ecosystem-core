# -*- coding: utf-8 -*-
"""
DeepMind Superhuman Reasoning, Aletheia & AlphaGeometry — SPEC-935-R442–R445
=============================================================================
Módulo de integração dos paradigmas de raciocínio científico avançado:
- OpenCode AlphaGeometry & Wu's Method Geometry Engine
- Bidirectional Auto-Formalizer & Cross-Validation Engine
- OpenCode AlphaProof (Proof-Tree Search & Táticas Formais)
- OpenCode Deep Think (Test-Time Compute & Trajetórias MCTS)
- Lean 4 Formal Proof Bridge & Verifier
- E-Graph & Equality Saturation Engine (Egglog Paradigm)
- Aletheia Scaffold & LaTeX Formatter
- Erdős & Hirzebruch Open Problems Solvers
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
from integrations.deepmind.autoformalizer import (
    AutoFormalizerEngine,
    CrossValidationResult,
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
from integrations.deepmind.geometry_engine import (
    GeometricDeductiveDatabase,
    GeometricProofResult,
    GeometryPoint,
    OpenCodeAlphaGeometry,
    TikzGeometryRenderer,
    WuGeometryProver,
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
    "GeometryPoint",
    "GeometricProofResult",
    "GeometricDeductiveDatabase",
    "WuGeometryProver",
    "TikzGeometryRenderer",
    "OpenCodeAlphaGeometry",
    "AutoFormalizerEngine",
    "CrossValidationResult",
]
