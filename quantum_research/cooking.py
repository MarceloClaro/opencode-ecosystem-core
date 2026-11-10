"""R1143–R1145 — otimização de processo culinário com QAOA (sintético).

Não existe literatura estabelecida de "cozimento quântico". Este módulo trata
o termo como **otimização de decisões de processo** (temperatura, tempo,
cobertura, pré-aquecimento) em um QUBO sintético, com solver clássico exato,
baseline aleatório e QAOA sob orçamento explícito. Não é ciência de alimentos,
não usa dados sensoriais reais e não executa hardware.

Fontes de método: QAOA (Farhi et al.) e revisão de VQA (Cerezo 2021).
Baseline aplicado: ML para cozimento de grãos (DOI 10.1002/fsp.2026.33.4.586).
"""
from __future__ import annotations

import itertools
import time

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QAOAAnsatz
from qiskit.quantum_info import SparsePauliOp, Statevector
from scipy.optimize import minimize

LIMITS = (
    "QUBO sintético de 4 decisões; não é estudo de alimentos, não usa dados "
    "sensoriais e não prova vantagem quântica. QAOA é simulada por statevector, "
    "sem ruído ou shots. Qualquer aplicação culinária exige dados reais, "
    "baseline clássico e validação sensorial."
)
SCALE_LIMITS = (
    "Profundidades p>3 em 4 variáveis não demonstram escala, vantagem ou "
    "tolerância a ruído; o solver clássico exato enumera 16 estados."
)
VARIABLES = (
    "temperatura_alta",
    "tempo_longo",
    "coberto",
    "preaquecido",
)
LINEAR = (-0.6, -0.4, 0.3, 0.2)
QUADRATIC = {(0, 1): -1.2, (1, 2): -0.7, (0, 3): -0.5, (2, 3): 0.3}


class BudgetExceeded(RuntimeError):
    """Orçamento de avaliações do QAOA esgotado."""


def energy(bits) -> float:
    bits = tuple(int(bit) for bit in bits)
    if len(bits) != len(VARIABLES) or any(bit not in (0, 1) for bit in bits):
        raise ValueError("bits devem ser quatro valores 0/1")
    value = sum(coefficient * bit for coefficient, bit in zip(LINEAR, bits))
    for (left, right), coefficient in QUADRATIC.items():
        value += coefficient * bits[left] * bits[right]
    return float(value)


def exact_solver() -> dict:
    """Enumeração exata de todos os 2^4 estados do QUBO."""
    started = time.perf_counter()
    candidates = [
        (energy(bits), bits) for bits in itertools.product((0, 1), repeat=len(VARIABLES))
    ]
    candidates.sort()
    best_energy, best_bits = candidates[0]
    return {
        "method": "enumeração exata (brute force)",
        "states": len(candidates),
        "energy": float(best_energy),
        "bits": list(best_bits),
        "seconds": float(time.perf_counter() - started),
    }


def brute_force() -> dict:
    exact = exact_solver()
    return {"energy": exact["energy"], "bits": tuple(exact["bits"])}


def random_baseline() -> float:
    values = [energy(bits) for bits in itertools.product((0, 1), repeat=len(VARIABLES))]
    return float(np.mean(values))


def _label(index: int, n_qubits: int = 4) -> str:
    chars = ["I"] * n_qubits
    chars[n_qubits - 1 - index] = "Z"
    return "".join(chars)


def cost_operator() -> SparsePauliOp:
    n = len(VARIABLES)
    terms: dict[str, float] = {"I" * n: 0.0}
    for index, coefficient in enumerate(LINEAR):
        terms["I" * n] += coefficient / 2
        terms[_label(index, n)] = terms.get(_label(index, n), 0.0) - coefficient / 2
    for (left, right), coefficient in QUADRATIC.items():
        base = coefficient / 4
        terms["I" * n] += base
        terms[_label(left, n)] = terms.get(_label(left, n), 0.0) - base
        terms[_label(right, n)] = terms.get(_label(right, n), 0.0) - base
        chars = ["I"] * n
        chars[n - 1 - left] = "Z"
        chars[n - 1 - right] = "Z"
        label = "".join(chars)
        terms[label] = terms.get(label, 0.0) + base
    return SparsePauliOp.from_list([
        (label, coefficient) for label, coefficient in terms.items() if abs(coefficient) > 1e-15
    ])


def qaoa_expectation(parameters, ansatz, hamiltonian) -> float:
    bound = ansatz.assign_parameters(dict(zip(ansatz.parameters, parameters)))
    state = Statevector.from_instruction(bound)
    return float(np.real(state.expectation_value(hamiltonian)))


def _optimize_depth(
    hamiltonian,
    reps,
    *,
    rng,
    maxiter,
    restarts,
    max_evaluations=None,
):
    ansatz = QAOAAnsatz(cost_operator=hamiltonian, reps=int(reps))
    counter = {"value": 0}
    status = "ok"

    def objective(parameters):
        if max_evaluations is not None and counter["value"] >= int(max_evaluations):
            raise BudgetExceeded
        counter["value"] += 1
        return qaoa_expectation(parameters, ansatz, hamiltonian)

    best = None
    for _ in range(int(restarts)):
        initial = rng.uniform(0, np.pi, len(ansatz.parameters))
        try:
            result = minimize(
                objective,
                initial,
                method="COBYLA",
                options={"maxiter": int(maxiter), "tol": 1e-8},
            )
        except BudgetExceeded:
            status = "budget_exhausted"
            break
        if best is None or result.fun < best.fun:
            best = result
    if best is None:
        return {
            "ansatz": ansatz,
            "result": None,
            "ranked": None,
            "bits": None,
            "evaluations": counter["value"],
            "status": status,
        }
    bound = ansatz.assign_parameters(dict(zip(ansatz.parameters, best.x)))
    probabilities = Statevector.from_instruction(bound).probabilities_dict()
    ranked = sorted(
        ((float(prob), state) for state, prob in probabilities.items()),
        reverse=True,
    )
    bits = tuple(int(bit) for bit in reversed(ranked[0][1]))
    return {
        "ansatz": ansatz,
        "result": best,
        "ranked": ranked,
        "bits": bits,
        "evaluations": counter["value"],
        "status": status,
    }


def qaoa_audit(
    *,
    maxiter: int = 200,
    seed: int = 7,
    depths=(1, 2, 3),
    restarts: int = 4,
    max_evaluations_per_depth: int | None = 2000,
) -> dict:
    depth_list = [int(value) for value in depths]
    if not depth_list or any(value < 1 for value in depth_list):
        raise ValueError("depths deve conter inteiros >= 1")
    if max_evaluations_per_depth is not None and int(max_evaluations_per_depth) < 1:
        raise ValueError("max_evaluations_per_depth deve ser >= 1 ou None")
    hamiltonian = cost_operator()
    rng = np.random.default_rng(seed)
    exact = exact_solver()
    random_mean = random_baseline()
    denominator = random_mean - exact["energy"]
    rows = []
    completed = []
    best = None
    for reps in depth_list:
        outcome = _optimize_depth(
            hamiltonian,
            reps,
            rng=rng,
            maxiter=maxiter,
            restarts=restarts,
            max_evaluations=max_evaluations_per_depth,
        )
        row = {
            "reps": reps,
            "status": outcome["status"],
            "evaluations": outcome["evaluations"],
            "parameters": int(len(outcome["ansatz"].parameters)),
        }
        if outcome["result"] is None:
            row.update({
                "energy": None,
                "bits": [],
                "probability": None,
                "approximation_ratio": None,
            })
        else:
            ratio = (
                (random_mean - float(outcome["result"].fun)) / denominator
                if abs(denominator) > 1e-12
                else 0.0
            )
            row.update({
                "energy": float(outcome["result"].fun),
                "bits": list(outcome["bits"]),
                "probability": outcome["ranked"][0][0],
                "approximation_ratio": float(max(0.0, min(1.0, ratio))),
            })
            completed.append(reps)
            if best is None or row["energy"] < best["energy"]:
                best = row
        rows.append(row)
    return {
        "schema_version": 1,
        "variables": list(VARIABLES),
        "linear": list(LINEAR),
        "quadratic": {f"{a}-{b}": value for (a, b), value in QUADRATIC.items()},
        "exact_energy": exact["energy"],
        "exact_bits": exact["bits"],
        "exact_solver": exact,
        "depths": rows,
        "completed_depths": completed,
        "qaoa_energy": best["energy"] if best else None,
        "qaoa_bits": best["bits"] if best else None,
        "qaoa_probability": best["probability"] if best else None,
        "qaoa_reps": best["reps"] if best else None,
        "random_mean_energy": random_mean,
        "approximation_ratio": best["approximation_ratio"] if best else None,
        "gap": (best["energy"] - exact["energy"]) if best else None,
        "budget": {
            "max_evaluations_per_depth": max_evaluations_per_depth,
            "total_evaluations": int(sum(row["evaluations"] for row in rows)),
        },
        "synthetic": True,
        "hardware_executed": False,
        "rates_measured": False,
        "limits": LIMITS,
        "scale_limits": SCALE_LIMITS,
    }
