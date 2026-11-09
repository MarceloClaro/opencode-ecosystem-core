#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Otimização hardware-aware para backends GJQ (SPEC-935-R1109).

Componentes:

- ``profile``: perfil declarado do backend, extraído do Target real;
- ``target``: reconstrução de um Target a partir do perfil;
- ``layout``: layout noise-aware e região física conectada;
- ``estimator``: proxy de sucesso por porta;
- ``optimizer``: candidatos, compactação e seleção;
- ``execution``: conexão, gates e submissão com ``transpile=False``;
- ``export``: QASM 2.0/3.0, JSON, Markdown e hashes;
- ``benchmarks``: circuitos sintéticos e E01–E18.
"""
from .benchmarks import all_circuits, list_circuits, load_circuit, select_circuits
from .estimator import estimate_success
from .execution import (
    BackendUnavailable,
    GJQExecutionError,
    MissingGJQKey,
    SubmissionBlocked,
    audit_counts,
    cached_account_present,
    connect_gjq,
    credential_present,
    execution_record,
    key_present,
    live_profile,
    submission_gate,
    submit_optimized,
    task_detail,
    task_result,
    task_status,
    wait_for_result,
)
from .export import (
    export_benchmark,
    export_execution,
    export_result,
    render_result_markdown,
)
from .layout import LayoutResult, circuit_interactions, noise_aware_layout
from .optimizer import (
    Candidate,
    GJQOptimizer,
    OptimizationResult,
    compact_to_used_physical,
    initial_layout_from_transpiled,
)
from .profile import HardwareProfile
from .target import build_target_from_profile

__all__ = [
    "HardwareProfile",
    "LayoutResult",
    "Candidate",
    "OptimizationResult",
    "GJQOptimizer",
    "build_target_from_profile",
    "noise_aware_layout",
    "circuit_interactions",
    "estimate_success",
    "compact_to_used_physical",
    "initial_layout_from_transpiled",
    "connect_gjq",
    "live_profile",
    "submission_gate",
    "submit_optimized",
    "task_status",
    "task_result",
    "task_detail",
    "wait_for_result",
    "audit_counts",
    "execution_record",
    "export_result",
    "export_benchmark",
    "export_execution",
    "render_result_markdown",
    "list_circuits",
    "select_circuits",
    "load_circuit",
    "all_circuits",
    "key_present",
    "cached_account_present",
    "credential_present",
    "MissingGJQKey",
    "BackendUnavailable",
    "SubmissionBlocked",
    "GJQExecutionError",
]
