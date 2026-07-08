# -*- coding: utf-8 -*-
"""
Scientific Reasoning Benchmark Suite.

Benchmarks para avaliar capacidade de raciocínio científico do ecossistema.
Cobre: causal inference, experimental design, power analysis,
statistical interpretation, bias detection e readiness superhuman.

Diferencial vs SuperHuman: SuperHuman só testa matemática (IMO).
Aqui testamos método científico completo.
"""

from benchmarks.scientific_reasoning.runner import BenchmarkResult, run_all_benchmarks
from benchmarks.scientific_reasoning.superhuman_suite import (
    classify_superhuman_tier,
    run_superhuman_suite,
)

__all__ = [
    "BenchmarkResult",
    "run_all_benchmarks",
    "classify_superhuman_tier",
    "run_superhuman_suite",
]
