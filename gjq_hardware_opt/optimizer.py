#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Otimizador hardware-aware para backends GJQ (R1109).

O otimizador compara candidatos de layout/roteamento no Target real, compacta
o circuito para os índices físicos usados e estima um proxy de sucesso por
porta. Ele não submete jobs; a submissão fica em ``execution.py``.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from qiskit import QuantumCircuit, transpile

from quantum_efficiency.metrics import circuit_metrics

from .estimator import estimate_success
from .layout import LayoutResult, noise_aware_layout
from .profile import HardwareProfile
from .target import build_target_from_profile

STRATEGIES = ("balanced", "min_error", "min_depth", "min_two_qubit", "noise_aware")


def compact_to_used_physical(circuit: QuantumCircuit) -> QuantumCircuit:
    """Remove qubits ociosos preservando os índices físicos usados.

    O circuito do Qiskit usa índices de qubit como índices físicos depois da
    transpilação. Compactar para ``max(usado)+1`` mantém essa correspondência.
    """
    used = sorted(
        {
            circuit.find_bit(qubit).index
            for instruction in circuit.data
            for qubit in instruction.qubits
        }
    )
    if not used:
        return circuit.copy()
    width = max(used) + 1
    compact = QuantumCircuit(width, circuit.num_clbits)
    for instruction in circuit.data:
        qargs = [compact.qubits[circuit.find_bit(q).index] for q in instruction.qubits]
        cargs = [compact.clbits[circuit.find_bit(c).index] for c in instruction.clbits]
        compact.append(instruction.operation, qargs, cargs)
    return compact


def initial_layout_from_transpiled(
    transpiled: QuantumCircuit,
    original: QuantumCircuit,
) -> list[int]:
    """Extrai o layout lógico -> físico do circuito transpilado."""
    layout = getattr(transpiled, "layout", None)
    if layout is None or layout.initial_layout is None:
        return list(range(original.num_qubits))
    try:
        physical_bits = layout.initial_layout.get_physical_bits()
    except Exception:
        return list(range(original.num_qubits))
    logical_to_physical: dict[int, int] = {}
    for physical, virtual in physical_bits.items():
        if virtual in original.qubits:
            logical_to_physical[original.find_bit(virtual).index] = int(physical)
    return [logical_to_physical.get(q, q) for q in range(original.num_qubits)]


@dataclass
class Candidate:
    layout_kind: str
    optimization_level: int
    layout_method: str | None
    routing_method: str
    seed: int
    initial_layout: list[int]
    circuit: QuantumCircuit | None
    metrics: dict[str, Any]
    estimate: dict[str, Any]
    transpile_seconds: float
    used_physical: list[int]
    status: str = "pass"
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "layout_kind": self.layout_kind,
            "optimization_level": self.optimization_level,
            "layout_method": self.layout_method,
            "routing_method": self.routing_method,
            "seed": self.seed,
            "initial_layout": list(self.initial_layout),
            "metrics": self.metrics,
            "estimate": self.estimate,
            "transpile_seconds": self.transpile_seconds,
            "used_physical": list(self.used_physical),
            "status": self.status,
            "error": self.error,
        }


@dataclass
class OptimizationResult:
    profile: HardwareProfile
    strategy: str
    seed: int
    baseline: Candidate
    chosen: Candidate
    candidates: list[Candidate]
    failures: list[dict[str, Any]]
    selection: dict[str, Any]
    layout: LayoutResult
    limits: str = (
        "Simulação de compilação e proxy de erro; não é execução física, "
        "não mede fidelidade de estado e não prova vantagem quântica."
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "profile_name": self.profile.name,
            "profile_kind": self.profile.profile_kind,
            "calibration_source": self.profile.calibration_source,
            "backend_name": self.profile.backend_name,
            "num_qubits": self.profile.num_qubits,
            "target_fingerprint": self.profile.target_fingerprint,
            "strategy": self.strategy,
            "seed": self.seed,
            "layout": self.layout.to_dict(),
            "baseline": self.baseline.to_dict(),
            "chosen": self.chosen.to_dict(),
            "candidates": [candidate.to_dict() for candidate in self.candidates],
            "failures": self.failures,
            "selection": self.selection,
            "hardware_executed": False,
            "network": False,
            "limits": self.limits,
        }


class GJQOptimizer:
    """Compara candidatos de transpilação no Target de um backend GJQ."""

    def __init__(
        self,
        profile: HardwareProfile,
        *,
        target=None,
        strategy: str = "balanced",
        seed: int = 42,
        quick: bool = False,
    ) -> None:
        if strategy not in STRATEGIES:
            raise ValueError(f"estratégia inválida: {strategy!r}; use {STRATEGIES}")
        self.profile = profile
        self.target = target if target is not None else build_target_from_profile(profile)
        self.strategy = strategy
        self.seed = int(seed)
        self.quick = bool(quick)
        self.baseline_layout = list(profile.operational_qubits) or list(
            range(profile.num_qubits)
        )

    def _levels(self) -> tuple[int, ...]:
        return (1, 3) if self.quick else (1, 2, 3)

    def _seeds(self) -> tuple[int, ...]:
        return (self.seed,) if self.quick else (self.seed, self.seed + 1)

    def _transpile(
        self,
        circuit: QuantumCircuit,
        *,
        layout_kind: str,
        optimization_level: int,
        layout_method: str | None,
        routing_method: str,
        seed: int,
        initial_layout: list[int] | None,
    ) -> Candidate:
        kwargs: dict[str, Any] = {
            "target": self.target,
            "optimization_level": int(optimization_level),
            "routing_method": str(routing_method),
            "seed_transpiler": int(seed),
        }
        if initial_layout is not None:
            kwargs["initial_layout"] = list(initial_layout)
        elif layout_method is not None:
            kwargs["layout_method"] = str(layout_method)
        started = time.perf_counter()
        try:
            transpiled = transpile(circuit, **kwargs)
        except Exception as exc:
            return Candidate(
                layout_kind=layout_kind,
                optimization_level=int(optimization_level),
                layout_method=layout_method,
                routing_method=routing_method,
                seed=int(seed),
                initial_layout=list(initial_layout or []),
                circuit=None,
                metrics={},
                estimate={},
                transpile_seconds=time.perf_counter() - started,
                used_physical=[],
                status="fail",
                error=f"{type(exc).__name__}: {exc}",
            )
        elapsed = time.perf_counter() - started
        resolved_layout = (
            list(initial_layout)
            if initial_layout is not None
            else initial_layout_from_transpiled(transpiled, circuit)
        )
        compact = compact_to_used_physical(transpiled)
        used_physical = sorted(
            {
                compact.find_bit(qubit).index
                for instruction in compact.data
                for qubit in instruction.qubits
            }
        )
        metrics = circuit_metrics(compact)
        estimate = estimate_success(compact, self.profile)
        return Candidate(
            layout_kind=layout_kind,
            optimization_level=int(optimization_level),
            layout_method=layout_method,
            routing_method=routing_method,
            seed=int(seed),
            initial_layout=[int(p) for p in resolved_layout],
            circuit=compact,
            metrics=metrics,
            estimate=estimate,
            transpile_seconds=elapsed,
            used_physical=used_physical,
            status="pass",
        )

    def _specs(self, layout: LayoutResult) -> list[dict[str, Any]]:
        specs: list[dict[str, Any]] = []
        for level in self._levels():
            for seed in self._seeds():
                specs.append(
                    dict(
                        layout_kind="noise_aware",
                        optimization_level=level,
                        layout_method=None,
                        routing_method="sabre",
                        seed=seed,
                        initial_layout=layout.layout,
                    )
                )
        for level in self._levels():
            for seed in self._seeds():
                specs.append(
                    dict(
                        layout_kind="sabre",
                        optimization_level=level,
                        layout_method="sabre",
                        routing_method="sabre",
                        seed=seed,
                        initial_layout=None,
                    )
                )
                specs.append(
                    dict(
                        layout_kind="dense",
                        optimization_level=level,
                        layout_method="dense",
                        routing_method="sabre",
                        seed=seed,
                        initial_layout=None,
                    )
                )
        return specs

    def _selection_key(self, candidate: Candidate) -> tuple:
        error = float(candidate.estimate.get("error_budget_proxy", 1.0))
        metrics = candidate.metrics
        depth = int(metrics.get("depth", 10**9))
        twoq = int(metrics.get("num_2q", 10**9))
        size = int(metrics.get("size", 10**9))
        priority = {"noise_aware": 0, "sabre": 1, "dense": 2}.get(candidate.layout_kind, 9)
        if self.strategy == "min_error":
            return (error, twoq, depth, size, priority, candidate.optimization_level, candidate.seed)
        if self.strategy == "min_depth":
            return (depth, error, twoq, size, priority, candidate.optimization_level, candidate.seed)
        if self.strategy == "min_two_qubit":
            return (twoq, error, depth, size, priority, candidate.optimization_level, candidate.seed)
        return (error, depth, twoq, size, priority, candidate.optimization_level, candidate.seed)

    def optimize(self, circuit: QuantumCircuit) -> OptimizationResult:
        if not isinstance(circuit, QuantumCircuit):
            raise TypeError("circuit deve ser um QuantumCircuit")
        if circuit.num_qubits > self.profile.num_qubits:
            raise ValueError(
                f"circuito usa {circuit.num_qubits} qubits, mas o perfil tem "
                f"{self.profile.num_qubits}"
            )
        layout = noise_aware_layout(circuit, self.profile, seed=self.seed)
        baseline = self._transpile(
            circuit,
            layout_kind="trivial",
            optimization_level=1,
            layout_method=None,
            routing_method="basic",
            seed=self.seed,
            initial_layout=self.baseline_layout[: circuit.num_qubits],
        )
        if baseline.status != "pass":
            raise RuntimeError(f"baseline falhou: {baseline.error}")

        candidates: list[Candidate] = []
        failures: list[dict[str, Any]] = []
        for spec in self._specs(layout):
            candidate = self._transpile(circuit, **spec)
            if candidate.status == "pass":
                candidates.append(candidate)
            else:
                failures.append(candidate.to_dict())
        if not candidates:
            raise RuntimeError("nenhum candidato hardware-aware passou")

        pool = candidates
        fallback_used = False
        if self.strategy == "noise_aware":
            filtered = [c for c in candidates if c.layout_kind == "noise_aware"]
            if filtered:
                pool = filtered
            else:
                fallback_used = True
        chosen = min(pool, key=self._selection_key)
        baseline_error = float(baseline.estimate.get("error_budget_proxy", 0.0))
        chosen_error = float(chosen.estimate.get("error_budget_proxy", 0.0))
        baseline_success = float(baseline.estimate.get("success_proxy", 0.0))
        chosen_success = float(chosen.estimate.get("success_proxy", 0.0))
        improvement = {
            "error_budget_abs": baseline_error - chosen_error,
            "error_budget_rel": (
                (baseline_error - chosen_error) / baseline_error
                if baseline_error > 0
                else 0.0
            ),
            "success_proxy_ratio": (
                chosen_success / baseline_success if baseline_success > 0 else None
            ),
            "depth_abs": int(baseline.metrics.get("depth", 0)) - int(chosen.metrics.get("depth", 0)),
            "num_2q_abs": int(baseline.metrics.get("num_2q", 0)) - int(chosen.metrics.get("num_2q", 0)),
            "size_abs": int(baseline.metrics.get("size", 0)) - int(chosen.metrics.get("size", 0)),
        }
        selection = {
            "strategy": self.strategy,
            "key": list(self._selection_key(chosen)),
            "layout_kind": chosen.layout_kind,
            "optimization_level": chosen.optimization_level,
            "seed": chosen.seed,
            "candidate_count": len(candidates),
            "failure_count": len(failures),
            "fallback_used": fallback_used,
            "improvement": improvement,
            "note": (
                "O baseline não participa da seleção; ele é apenas comparação. "
                "O proxy de erro não é fidelidade de estado."
            ),
        }
        return OptimizationResult(
            profile=self.profile,
            strategy=self.strategy,
            seed=self.seed,
            baseline=baseline,
            chosen=chosen,
            candidates=candidates,
            failures=failures,
            selection=selection,
            layout=layout,
        )
