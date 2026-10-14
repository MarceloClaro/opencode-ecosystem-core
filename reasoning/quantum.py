"""Simulação clássica local de circuitos predefinidos — SPEC-935-R890.

Statevector Python de 2 a 20 qubits. Não despacha para QPU, Qiskit ou MPS.
As métricas descrevem a medição simulada, sem responder perguntas em texto.
"""
from __future__ import annotations

import cmath
import hashlib
import json
import math
import random
import warnings
from collections import Counter
from itertools import accumulate

DEFAULT_SEEDS = [42, 123, 777, 2026, 31415]
MAX_PURE_PYTHON_QUBITS = 20
MAX_SHOTS = 10_000
MAX_SEEDS = 10
MAX_SEED = (1 << 63) - 1


def _integer(value, minimum: int, maximum: int, field: str) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f"{field} deve ser inteiro entre {minimum} e {maximum}.")
    return value


def _seed(value) -> int:
    """Seed inteira não negativa de 63 bits; validar antes de construir estado."""
    return _integer(value, 0, MAX_SEED, "seed")


def validate_configuration(n_qubits=3, seeds=None, shots=1024) -> dict:
    """Valida todo o orçamento antes de alocar estados ou executar circuitos."""
    _integer(n_qubits, 2, MAX_PURE_PYTHON_QUBITS, "n_qubits")
    _integer(shots, 1, MAX_SHOTS, "shots")
    if seeds is None:
        seeds = list(DEFAULT_SEEDS)
    if type(seeds) is not list or not 1 <= len(seeds) <= MAX_SEEDS:
        raise ValueError(f"seeds deve conter entre 1 e {MAX_SEEDS} inteiros.")
    return {"n_qubits": n_qubits, "shots": shots, "seeds": [_seed(value) for value in seeds]}


class QuantumSimulator:
    """Statevector em hardware clássico, com orçamento e seeds explícitos."""

    def __init__(self, n_qubits: int = 2, seed: int | None = None):
        self.n = _integer(n_qubits, 2, MAX_PURE_PYTHON_QUBITS, "n_qubits")
        self.seed = _seed(DEFAULT_SEEDS[0] if seed is None else seed)
        self._rng = random.Random(self.seed)
        self.state: list[complex] = [0j] * (1 << self.n)
        self.state[0] = 1 + 0j
        self.gate_log: list[str] = []

    def _qubit(self, value) -> int:
        return _integer(value, 0, self.n - 1, "índice de qubit")

    def _pair(self, control, target):
        self._qubit(control)
        self._qubit(target)
        if control == target:
            raise ValueError("Controle e alvo devem ser qubits distintos.")

    @staticmethod
    def _angle(value):
        if type(value) not in (int, float):
            raise ValueError("O ângulo deve ser numérico finito.")
        try:
            if math.isfinite(value):
                return value
        except OverflowError:
            pass
        raise ValueError("O ângulo deve ser numérico finito.")

    def _apply_1q(self, qubit, matrix, label):
        self._qubit(qubit)
        stride = 1 << qubit
        new_state = self.state[:]
        for i in range(1 << self.n):
            if i & stride == 0:
                j = i | stride
                a, b = self.state[i], self.state[j]
                new_state[i] = matrix[0][0] * a + matrix[0][1] * b
                new_state[j] = matrix[1][0] * a + matrix[1][1] * b
        self.state = new_state
        self.gate_log.append(f"{label}(q{qubit})")
        return self

    def h(self, q):
        value = 1 / math.sqrt(2)
        return self._apply_1q(q, ((value, value), (value, -value)), "H")

    def x(self, q):
        return self._apply_1q(q, ((0, 1), (1, 0)), "X")

    def y(self, q):
        return self._apply_1q(q, ((0, -1j), (1j, 0)), "Y")

    def z(self, q):
        return self._apply_1q(q, ((1, 0), (0, -1)), "Z")

    def s(self, q):
        return self._apply_1q(q, ((1, 0), (0, 1j)), "S")

    def t(self, q):
        return self._apply_1q(q, ((1, 0), (0, cmath.exp(1j * math.pi / 4))), "T")

    def rx(self, q, theta):
        theta = self._angle(theta)
        c, s = math.cos(theta / 2), math.sin(theta / 2)
        return self._apply_1q(q, ((c, -1j * s), (-1j * s, c)), f"RX{theta:.3f}")

    def ry(self, q, theta):
        theta = self._angle(theta)
        c, s = math.cos(theta / 2), math.sin(theta / 2)
        return self._apply_1q(q, ((c, -s), (s, c)), f"RY{theta:.3f}")

    def rz(self, q, theta):
        theta = self._angle(theta)
        return self._apply_1q(q, ((cmath.exp(-1j * theta / 2), 0),
                                  (0, cmath.exp(1j * theta / 2))), f"RZ{theta:.3f}")

    def cnot(self, control, target):
        self._pair(control, target)
        control_mask, target_mask = 1 << control, 1 << target
        new_state = self.state[:]
        for i in range(1 << self.n):
            if i & control_mask and not i & target_mask:
                j = i | target_mask
                new_state[i], new_state[j] = self.state[j], self.state[i]
        self.state = new_state
        self.gate_log.append(f"CNOT(q{control},q{target})")
        return self

    def cz(self, control, target):
        self._pair(control, target)
        control_mask, target_mask = 1 << control, 1 << target
        for i in range(1 << self.n):
            if i & control_mask and i & target_mask:
                self.state[i] *= -1
        self.gate_log.append(f"CZ(q{control},q{target})")
        return self

    def probabilities(self) -> dict[str, float]:
        return {format(i, f"0{self.n}b"): abs(amplitude) ** 2
                for i, amplitude in enumerate(self.state) if abs(amplitude) ** 2 > 1e-12}

    def measure(self, shots: int = 1024) -> dict[str, int]:
        _integer(shots, 1, MAX_SHOTS, "shots")
        probabilities = self.probabilities()
        outcomes = list(probabilities)
        cumulative = list(accumulate(probabilities.values()))
        if not cumulative or not math.isfinite(cumulative[-1]) or cumulative[-1] <= 0:
            raise ValueError("O estado não define distribuição finita positiva.")
        counts = Counter(self._rng.choices(outcomes, cum_weights=cumulative, k=shots))
        return dict(sorted(counts.items()))

    def measurement_entropy(self) -> float:
        """Shannon das probabilidades de medição; não é entropia de emaranhamento."""
        return -sum(value * math.log2(value) for value in self.probabilities().values() if value > 0)

    def entanglement_entropy(self) -> float:
        """Alias depreciado; conserva Shannon de medição, sem medir emaranhamento."""
        warnings.warn("Use measurement_entropy: esta API calcula Shannon da medição, não emaranhamento.",
                      DeprecationWarning, stacklevel=2)
        return self.measurement_entropy()


def bell_state(seed: int | None = None) -> QuantumSimulator:
    return QuantumSimulator(2, seed).h(0).cnot(0, 1)


def ghz_state(n_qubits: int = 3, seed: int | None = None) -> QuantumSimulator:
    sim = QuantumSimulator(n_qubits, seed).h(0)
    for q in range(1, n_qubits):
        sim.cnot(0, q)
    return sim


def uniform_superposition(n_qubits: int = 3, seed: int | None = None) -> QuantumSimulator:
    sim = QuantumSimulator(n_qubits, seed)
    for q in range(n_qubits):
        sim.h(q)
    return sim


def run_experiment_suite(n_qubits=3, seeds=None, shots=1024) -> dict:
    """Bell/GHZ/superposição predefinidos; mede amostragem da própria simulação."""
    config = validate_configuration(n_qubits, seeds, shots)
    seeds = config["seeds"]
    report = {"schema": "r890.quantum_suite.v1", "execution_kind": "classical_simulation",
              "backend": "python_statevector", "quantum_hardware_used": False,
              "query_evaluated": False, "configuration": config, "n_qubits": n_qubits,
              "seeds": seeds, "shots": shots, "experiments": {}, "calibrated": False,
              "confidence_promoted": False, "externally_validated": False,
              "limits": {"max_qubits": MAX_PURE_PYTHON_QUBITS, "max_shots": MAX_SHOTS, "max_seeds": MAX_SEEDS,
                         "min_seed": 0, "max_seed": MAX_SEED},
              "limitations": ["Suíte predefinida: não interpreta nem responde uma consulta textual.",
                              "As métricas comparam amostras à distribuição do próprio simulador; não validam o backend ou hardware.",
                              "measurement_entropy é Shannon de medição; support_mass não é fidelidade de estado.",
                              "A confiança legada zero representa consulta não avaliada; não é uma probabilidade calibrada.",
                              "O limite de qubits não garante latência constante: o statevector tem custo exponencial."]}
    for name, builder in (("bell", bell_state), ("ghz", lambda seed: ghz_state(n_qubits, seed)),
                          ("superposition", lambda seed: uniform_superposition(n_qubits, seed))):
        runs = []
        for seed in seeds:
            sim = builder(seed)
            counts = sim.measure(shots)
            probabilities = sim.probabilities()
            support_mass = sum(counts.get(key, 0) for key in probabilities) / shots
            distance = sum(abs(counts.get(key, 0) / shots - probabilities.get(key, 0))
                           for key in probabilities.keys() | counts.keys()) / 2
            runs.append({"seed": seed, "counts": counts,
                         "measurement_entropy": round(sim.measurement_entropy(), 12),
                         "support_mass": round(support_mass, 12),
                         "total_variation_distance": round(distance, 12)})
        report["experiments"][name] = {
            "n_qubits": sim.n, "runs": runs, "ranking_metric": "total_variation_distance",
            "best_seed": min(runs, key=lambda row: row["total_variation_distance"])["seed"],
            "worst_seed": max(runs, key=lambda row: row["total_variation_distance"])["seed"],
        }
    report["report_sha256"] = hashlib.sha256(json.dumps(
        report, ensure_ascii=False, sort_keys=True, allow_nan=False).encode()).hexdigest()
    return report
