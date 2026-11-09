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
from .comparison import (
    build_baseline_candidate,
    case_payload,
    export_comparison,
    render_comparison_markdown,
)
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
from .loop import (
    export_loop,
    render_loop_report,
    run_sdd_gate,
    run_tdd_gate,
    score_comparison,
    simulation_gate,
)
from .mitigation import (
    ReadoutModel,
    calibration_circuit,
    calibration_circuits,
    confusion_from_calibration_counts,
    correlation,
    ideal_bell_subspace,
    measurement_order,
    mitigate_counts_for_circuit,
    mitigate_probabilities,
    mitigate_subspace,
    readout_confusion_matrix,
    states_for,
    subspace_matrix_from_calibration,
    tvd_vs_ideal,
)
from .optimizer import (
    Candidate,
    GJQOptimizer,
    OptimizationResult,
    compact_to_used_physical,
    initial_layout_from_transpiled,
)
from .profile import HardwareProfile
from .simulation import simulate_case, simulate_plan
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
    "ReadoutModel",
    "simulate_case",
    "simulate_plan",
    "simulation_gate",
    "run_sdd_gate",
    "run_tdd_gate",
    "score_comparison",
    "render_loop_report",
    "export_loop",
    "readout_confusion_matrix",
    "confusion_from_calibration_counts",
    "subspace_matrix_from_calibration",
    "mitigate_probabilities",
    "mitigate_subspace",
    "mitigate_counts_for_circuit",
    "calibration_circuit",
    "calibration_circuits",
    "measurement_order",
    "states_for",
    "correlation",
    "tvd_vs_ideal",
    "ideal_bell_subspace",
    "estimate_success",
    "build_baseline_candidate",
    "case_payload",
    "export_comparison",
    "render_comparison_markdown",
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
