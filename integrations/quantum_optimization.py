"""QUBO/QAOA harness with an explicitly gated GJQ hardware adapter.

The core model, exact baseline, Ising conversion, and QAOA IR are dependency-
free. Qiskit and gjq-client are imported only for a confirmed remote call.
"""
from __future__ import annotations

from contextlib import redirect_stdout
from dataclasses import dataclass
import hashlib
import io
import itertools
import json
import math
import os
from typing import Any, Callable


MAX_QAOA_VARIABLES = 20
MAX_EXACT_VARIABLES = 16
MAX_QAOA_DEPTH = 4
MAX_REMOTE_EVALUATIONS = 8
MAX_REMOTE_SHOTS = 2048
MAX_REMOTE_TOTAL_SHOTS = MAX_REMOTE_EVALUATIONS * MAX_REMOTE_SHOTS


class QuantumContractError(ValueError):
    """Invalid or over-budget request with a stable public error message."""


@dataclass(frozen=True)
class Qubo:
    name: str
    num_variables: int
    constant: float
    linear: tuple[float, ...]
    quadratic: tuple[tuple[int, int, float], ...]
    problem_sha256: str

    def energy(self, assignment: Any) -> float:
        if not isinstance(assignment, (list, tuple)) or len(assignment) != self.num_variables:
            raise QuantumContractError("assignment deve conter um bit por variável.")
        bits: list[int] = []
        for bit in assignment:
            if isinstance(bit, bool) or not isinstance(bit, int) or bit not in (0, 1):
                raise QuantumContractError("assignment aceita somente inteiros 0 ou 1.")
            bits.append(bit)
        value = self.constant + sum(coefficient * bits[i]
                                    for i, coefficient in enumerate(self.linear))
        value += sum(coefficient * bits[i] * bits[j]
                     for i, j, coefficient in self.quadratic)
        return float(value)


def _finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise QuantumContractError(f"{field} deve ser numérico.")
    number = float(value)
    if not math.isfinite(number):
        raise QuantumContractError(f"{field} deve ser finito.")
    return number


def parse_qubo(payload: Any) -> Qubo:
    """Validates and canonicalizes the strict JSON QUBO schema v1."""
    required = {"schema_version", "name", "num_variables", "constant", "linear", "quadratic"}
    if not isinstance(payload, dict) or set(payload) != required:
        raise QuantumContractError("payload deve seguir exatamente o schema QUBO v1.")
    if type(payload["schema_version"]) is not int or payload["schema_version"] != 1:
        raise QuantumContractError("schema_version deve ser o inteiro 1.")
    name = payload["name"]
    if not isinstance(name, str) or not name.strip() or len(name) > 120:
        raise QuantumContractError("name deve ser texto não vazio de até 120 caracteres.")
    n = payload["num_variables"]
    if isinstance(n, bool) or not isinstance(n, int) or not 1 <= n <= MAX_QAOA_VARIABLES:
        raise QuantumContractError(f"num_variables deve estar em 1..{MAX_QAOA_VARIABLES}.")
    constant = _finite_number(payload["constant"], "constant")
    raw_linear = payload["linear"]
    if not isinstance(raw_linear, list) or len(raw_linear) != n:
        raise QuantumContractError("linear deve ter exatamente num_variables coeficientes.")
    linear = tuple(_finite_number(value, f"linear[{index}]")
                   for index, value in enumerate(raw_linear))

    raw_quadratic = payload["quadratic"]
    if not isinstance(raw_quadratic, list) or len(raw_quadratic) > n * (n - 1) // 2:
        raise QuantumContractError("quadratic deve ser uma lista dentro do limite de pares.")
    pairs: dict[tuple[int, int], float] = {}
    for index, term in enumerate(raw_quadratic):
        if not isinstance(term, (list, tuple)) or len(term) != 3:
            raise QuantumContractError(f"quadratic[{index}] deve ser [i,j,coefficient].")
        first, second, raw_coefficient = term
        if (isinstance(first, bool) or not isinstance(first, int)
                or isinstance(second, bool) or not isinstance(second, int)):
            raise QuantumContractError(f"quadratic[{index}] indices devem ser inteiros.")
        if not (0 <= first < n and 0 <= second < n) or first == second:
            raise QuantumContractError(f"quadratic[{index}] indices fora do domínio ou iguais.")
        pair = tuple(sorted((first, second)))
        if pair in pairs:
            raise QuantumContractError(f"quadratic contém par duplicado {pair}.")
        pairs[pair] = _finite_number(raw_coefficient, f"quadratic[{index}].coefficient")

    quadratic = tuple((i, j, pairs[(i, j)]) for i, j in sorted(pairs))
    canonical = {
        "schema_version": 1,
        "name": name.strip(),
        "num_variables": n,
        "constant": constant,
        "linear": list(linear),
        "quadratic": [[i, j, coefficient] for i, j, coefficient in quadratic],
    }
    digest = hashlib.sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    ).hexdigest()
    return Qubo(canonical["name"], n, constant, linear, quadratic, digest)


def exact_classical_baseline(qubo: Qubo) -> dict[str, Any]:
    """Exhaustive classical baseline for small QUBOs; exact only for this model."""
    if qubo.num_variables > MAX_EXACT_VARIABLES:
        raise QuantumContractError(
            f"exact baseline limitado a {MAX_EXACT_VARIABLES} variáveis."
        )
    best_assignment: tuple[int, ...] | None = None
    best_energy = math.inf
    for assignment in itertools.product((0, 1), repeat=qubo.num_variables):
        energy = qubo.energy(assignment)
        if energy < best_energy - 1e-12:
            best_energy = energy
            best_assignment = assignment
    assert best_assignment is not None
    return {
        "backend": "classical-exact-baseline",
        "quantum": False,
        "optimality": "exact_for_model",
        "objective": round(best_energy, 12),
        "assignment": list(best_assignment),
        "evaluated_assignments": 1 << qubo.num_variables,
        "problem_sha256": qubo.problem_sha256,
    }


def qubo_to_ising(qubo: Qubo) -> dict[str, Any]:
    """Convert x=(1-Z)/2 while retaining the constant energy offset."""
    constant = qubo.constant + sum(value / 2.0 for value in qubo.linear)
    fields = [-value / 2.0 for value in qubo.linear]
    couplers: list[tuple[int, int, float]] = []
    for i, j, coefficient in qubo.quadratic:
        quarter = coefficient / 4.0
        constant += quarter
        fields[i] -= quarter
        fields[j] -= quarter
        couplers.append((i, j, quarter))
    return {
        "constant": round(constant, 12),
        "fields": [[i, round(value, 12)] for i, value in enumerate(fields) if value != 0.0],
        "couplers": [[i, j, round(value, 12)] for i, j, value in couplers if value != 0.0],
        "encoding": "x=(1-Z)/2",
        "problem_sha256": qubo.problem_sha256,
    }


def build_qaoa_ir(qubo: Qubo, depth: int = 1) -> dict[str, Any]:
    """Return a provider-neutral, auditable QAOA circuit description."""
    if isinstance(depth, bool) or not isinstance(depth, int) or not 1 <= depth <= MAX_QAOA_DEPTH:
        raise QuantumContractError(f"depth deve estar em 1..{MAX_QAOA_DEPTH}.")
    ising = qubo_to_ising(qubo)
    fields = {index: coefficient for index, coefficient in ising["fields"]}
    couplers = [(row[0], row[1], row[2]) for row in ising["couplers"]]
    operations: list[dict[str, Any]] = [
        {"gate": "H", "qubits": [index]} for index in range(qubo.num_variables)
    ]
    for layer in range(depth):
        gamma = f"gamma_{layer}"
        beta = f"beta_{layer}"
        for index in range(qubo.num_variables):
            coefficient = fields.get(index, 0.0)
            if coefficient:
                operations.append({
                    "gate": "RZ", "qubits": [index], "parameter": gamma,
                    "scale": round(2.0 * coefficient, 12),
                })
        for first, second, coefficient in couplers:
            operations.append({
                "gate": "RZZ", "qubits": [first, second], "parameter": gamma,
                "scale": round(2.0 * coefficient, 12),
            })
        for index in range(qubo.num_variables):
            operations.append({
                "gate": "RX", "qubits": [index], "parameter": beta, "scale": 2.0,
            })
    operations.append({"gate": "MEASURE_ALL", "qubits": list(range(qubo.num_variables))})
    return {
        "algorithm": "QAOA",
        "depth": depth,
        "num_qubits": qubo.num_variables,
        "parameter_order": [*[f"gamma_{i}" for i in range(depth)],
                            *[f"beta_{i}" for i in range(depth)]],
        "measurement_order": list(range(qubo.num_variables)),
        "operations": operations,
        "problem_sha256": qubo.problem_sha256,
        "global_phase_ignored": True,
        "optimality": "not_proven",
    }


def energy_from_counts(qubo: Qubo, counts: Any) -> dict[str, Any]:
    """Compute sample mean from Qiskit/GJQ bitstrings (q0 at right)."""
    if not isinstance(counts, dict) or not counts:
        raise QuantumContractError("counts deve ser um mapa não vazio de bitstrings.")
    weighted_energy = 0.0
    total = 0
    for key, raw_count in counts.items():
        if not isinstance(key, str) or len(key) != qubo.num_variables or any(bit not in "01" for bit in key):
            raise QuantumContractError("bitstring de counts tem largura ou símbolos inválidos.")
        if isinstance(raw_count, bool) or not isinstance(raw_count, int) or raw_count < 1:
            raise QuantumContractError("cada contagem deve ser inteiro positivo.")
        assignment = [int(bit) for bit in reversed(key)]
        weighted_energy += qubo.energy(assignment) * raw_count
        total += raw_count
    return {
        "mean_energy": weighted_energy / total,
        "samples": total,
        "counts": counts,
        "problem_sha256": qubo.problem_sha256,
    }


def _angle(value: Any) -> float:
    number = float(value) % (2.0 * math.pi)
    return number


def bounded_angle_search(
    evaluate: Callable[[list[float]], float], *, depth: int,
    max_evaluations: int, seed: int = 42,
) -> dict[str, Any]:
    """Deterministic coordinate search; evaluation count is a strict hard cap."""
    if isinstance(depth, bool) or not isinstance(depth, int) or not 1 <= depth <= MAX_QAOA_DEPTH:
        raise QuantumContractError(f"depth deve estar em 1..{MAX_QAOA_DEPTH}.")
    if (isinstance(max_evaluations, bool) or not isinstance(max_evaluations, int)
            or not 1 <= max_evaluations <= 64):
        raise QuantumContractError("max_evaluations deve estar em 1..64.")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise QuantumContractError("seed deve ser inteiro.")
    # Seed is part of the recorded deterministic protocol; initial points are fixed.
    initial = [_angle(0.5 + (seed % 17) / 100.0) for _ in range(depth)]
    initial += [_angle(0.25 + (seed % 13) / 100.0) for _ in range(depth)]

    def evaluate_finite(angles: list[float]) -> float:
        value = _finite_number(evaluate(list(angles)), "objective")
        return value

    current = list(initial)
    current_value = evaluate_finite(current)
    initial_value = current_value
    best = list(current)
    best_value = current_value
    evaluations = 1
    history = [{"evaluation": 1, "angles": list(current), "objective": current_value}]
    step = 0.25
    while evaluations < max_evaluations and step >= 0.05:
        improved = False
        for index in range(len(current)):
            for direction in (1.0, -1.0):
                if evaluations >= max_evaluations:
                    break
                candidate = list(current)
                candidate[index] = _angle(candidate[index] + direction * step)
                value = evaluate_finite(candidate)
                evaluations += 1
                history.append({"evaluation": evaluations, "angles": list(candidate), "objective": value})
                if value < best_value - 1e-12:
                    best, best_value = list(candidate), value
                    current, current_value = list(candidate), value
                    improved = True
            if evaluations >= max_evaluations:
                break
        if not improved:
            step *= 0.5
    return {
        "method": "bounded-coordinate-search",
        "best_angles": best,
        "best_objective": best_value,
        "initial_objective": initial_value,
        "evaluations": evaluations,
        "history": history,
        "converged": step < 0.05,
        "optimality": "not_proven",
        "seed": seed,
    }


def is_confirmed_hardware_type(backend_type: Any) -> bool:
    if not isinstance(backend_type, str):
        return False
    value = backend_type.strip().casefold()
    if not value or "simulator" in value or "simulation" in value or value in {"mps", "fas", "sas"}:
        return False
    return (
        "superconduct" in value
        or "quantum hardware" in value
        or value in {"hardware", "quantum processor"}
    )


def quantum_catalog() -> dict[str, Any]:
    """Static source map; this operation never queries a network or credentials."""
    frameworks = [
        {
            "name": "GJQ/Tiangong",
            "role": "quantum provider SDK and cloud hardware/simulator interface",
            "qiskit": True,
            "pennylane": True,
            "cirq": False,
            "hardware_execution_supported_by_docs": True,
            "runtime_checked": False,
            "license_observed": "Apache-2.0 (gjq_client repository)",
            "sources": [
                "https://tiangongqs.com/docs/en/framework/index.html",
                "https://tiangongqs.com/docs/en/framework/backends.html",
                "https://tiangongqs.com/docs/en/framework/jobs.html",
                "https://tiangongqs.com/docs/en/framework/pennylane.html",
                "https://github.com/guoji-quantum/gjq_client",
            ],
            "limitations": [
                "backend list and queue are dynamic; only provider-reported metadata can identify hardware",
                "docs show gjq-client 0.2.0 while repository README/changelog describe 0.2.2; resolve PyPI compatibility before live use",
                "SDK documents local account caching after first authentication",
            ],
        },
        {
            "name": "Qiskit",
            "role": "primary circuit, transpilation and Sampler path for GJQ",
            "gjq_integration_documented": True,
            "selected_for_harness": True,
            "source": "https://github.com/Qiskit/qiskit",
        },
        {
            "name": "PennyLane",
            "role": "optional differentiable variational circuit path; gradients may submit multiple jobs",
            "gjq_integration_documented": True,
            "selected_for_harness": False,
            "source": "https://github.com/PennyLaneAI/pennylane",
        },
        {
            "name": "Cirq",
            "role": "separate quantum SDK/provider ecosystem",
            "gjq_adapter_documented": False,
            "google_engine_public_access": False,
            "source": "https://quantumai.google/cirq/google/engine",
        },
        {
            "name": "XQuad",
            "role": "external QUBO/Ising toolchain and solver adapters",
            "dependency_selected": False,
            "license": "AGPL-3.0-or-later",
            "pre_v1_api": True,
            "gjq_backend_listed": False,
            "source": "https://github.com/QuipNetwork/xquad",
        },
        {
            "name": "Transformers",
            "role": "classical text/vision/audio/multimodal model framework",
            "quantum_runtime": False,
            "selected_for_harness": False,
            "source": "https://github.com/huggingface/transformers",
        },
    ]
    return {
        "status": "success",
        "app": "quantum-optimization",
        "technique": "static-documentation-catalog",
        "result": {"frameworks": frameworks, "network": False, "hardware_executed": False},
        "evidence": {"method": "official-docs-and-repository-metadata", "as_of": "2026-11-20"},
        "limitations": [
            "Static documentation map; no SDK installed, account authenticated, backend queried, or QPU job submitted.",
            "No claim of quantum advantage, optimality of QAOA, or monetary cost ceiling.",
        ],
    }


def qaoa_plan(
    payload: Any, *, depth: int = 1, shots: int = 1024,
    max_evaluations: int = 8,
) -> dict[str, Any]:
    qubo = parse_qubo(payload)
    if isinstance(shots, bool) or not isinstance(shots, int) or not 1 <= shots <= MAX_REMOTE_SHOTS:
        raise QuantumContractError(f"shots deve estar em 1..{MAX_REMOTE_SHOTS}.")
    if (isinstance(max_evaluations, bool) or not isinstance(max_evaluations, int)
            or not 1 <= max_evaluations <= MAX_REMOTE_EVALUATIONS):
        raise QuantumContractError(f"max_evaluations deve estar em 1..{MAX_REMOTE_EVALUATIONS}.")
    ir = build_qaoa_ir(qubo, depth)
    baseline = None
    if qubo.num_variables <= MAX_EXACT_VARIABLES:
        baseline = exact_classical_baseline(qubo)
    return {
        "status": "success",
        "app": "quantum-optimization",
        "technique": "QAOA-plan-only",
        "result": {
            "problem_sha256": qubo.problem_sha256,
            "qubo": {"name": qubo.name, "num_variables": qubo.num_variables,
                     "num_quadratic_terms": len(qubo.quadratic)},
            "ising": qubo_to_ising(qubo),
            "circuit_ir": ir,
            "classical_baseline": baseline,
            "shots_per_evaluation": shots,
            "maximum_evaluations": max_evaluations,
            "maximum_jobs": max_evaluations,
            "maximum_shots": shots * max_evaluations,
            "remote_submission": False,
            "optimality": "not_proven",
        },
        "evidence": {"method": "local-deterministic-plan", "network": False},
        "limitations": [
            "Planning is not circuit execution or evidence from quantum hardware.",
            "The exact baseline is classical and limited to 16 variables.",
            "QAOA angle search is heuristic and does not prove a global optimum.",
        ],
    }


def build_qiskit_circuit(qubo: Qubo, depth: int, sdk: Any = None):
    if sdk is None:
        sdk = load_gjq_sdk()
    circuit = sdk.QuantumCircuit(qubo.num_variables)
    gammas = sdk.ParameterVector("gamma", depth)
    betas = sdk.ParameterVector("beta", depth)
    ir = build_qaoa_ir(qubo, depth)
    for operation in ir["operations"]:
        gate = operation["gate"]
        qubits = operation["qubits"]
        if gate == "H":
            circuit.h(qubits[0])
        elif gate == "RZ":
            circuit.rz(gammas[int(operation["parameter"].split("_")[1])] * operation["scale"], qubits[0])
        elif gate == "RZZ":
            circuit.rzz(gammas[int(operation["parameter"].split("_")[1])] * operation["scale"], *qubits)
        elif gate == "RX":
            circuit.rx(betas[int(operation["parameter"].split("_")[1])] * operation["scale"], qubits[0])
        elif gate == "MEASURE_ALL":
            circuit.measure_all()
    return circuit, gammas, betas


def load_gjq_sdk() -> Any:
    """Lazy optional imports; does not install, authenticate, or contact GJQ."""
    try:
        from qiskit import QuantumCircuit
        from qiskit.circuit import ParameterVector
        from gjq_client import GJQRuntimeService, Sampler, generate_preset_pass_manager
    except ImportError as exc:
        raise ImportError("GJQ hardware path requires qiskit and gjq-client extras.") from exc
    return type("GJQSDK", (), {
        "QuantumCircuit": QuantumCircuit,
        "ParameterVector": ParameterVector,
        "GJQRuntimeService": GJQRuntimeService,
        "Sampler": Sampler,
        "generate_preset_pass_manager": staticmethod(generate_preset_pass_manager),
    })


def _backend_value(row: Any, key: str) -> Any:
    return row.get(key) if isinstance(row, dict) else getattr(row, key, None)


def _blocked(code: str, message: str, *, jobs: int = 0) -> dict[str, Any]:
    return {
        "status": "blocked",
        "app": "quantum-optimization",
        "technique": "GJQ-QAOA",
        "result": {"code": code, "message": message},
        "evidence": {"jobs_submitted": jobs, "hardware_executed": False},
        "limitations": [message, "Nenhuma vantagem quântica é inferida."],
    }


def run_gjq_qaoa(
    payload: Any, *, backend_name: str, shots: int, max_evaluations: int,
    max_total_shots: int | None, confirm_remote: bool, depth: int = 1,
    seed: int = 42, sdk: Any = None,
) -> dict[str, Any]:
    """Run bounded QAOA evaluations on provider-confirmed hardware only.

    This function has intentional external effects. A single call requires a
    fresh boolean confirmation and explicit job/shot caps. It never retries a
    failed or uncertain submission automatically.
    """
    if confirm_remote is not True:
        return _blocked("remote_confirmation_required", "confirme explicitamente a submissão remota.")
    if not isinstance(backend_name, str) or not backend_name.strip() or len(backend_name) > 120:
        raise QuantumContractError("backend_name deve ser nome exato não vazio.")
    qubo = parse_qubo(payload)
    if isinstance(shots, bool) or not isinstance(shots, int) or not 1 <= shots <= MAX_REMOTE_SHOTS:
        raise QuantumContractError(f"shots deve estar em 1..{MAX_REMOTE_SHOTS}.")
    if (isinstance(max_evaluations, bool) or not isinstance(max_evaluations, int)
            or not 1 <= max_evaluations <= MAX_REMOTE_EVALUATIONS):
        raise QuantumContractError(f"max_evaluations deve estar em 1..{MAX_REMOTE_EVALUATIONS}.")
    if (isinstance(max_total_shots, bool) or not isinstance(max_total_shots, int)
            or max_total_shots < shots * max_evaluations
            or max_total_shots > MAX_REMOTE_TOTAL_SHOTS):
        raise QuantumContractError(
            f"max_total_shots deve cobrir shots*max_evaluations e não superar {MAX_REMOTE_TOTAL_SHOTS}."
        )
    if isinstance(depth, bool) or not isinstance(depth, int) or not 1 <= depth <= MAX_QAOA_DEPTH:
        raise QuantumContractError(f"depth deve estar em 1..{MAX_QAOA_DEPTH}.")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise QuantumContractError("seed deve ser inteiro.")

    api_key = os.environ.get("GJQ_API_KEY")
    if not api_key:
        return _blocked("credential_missing", "credencial GJQ ausente no ambiente; nenhuma chamada externa foi feita.")
    try:
        sdk = sdk if sdk is not None else load_gjq_sdk()
    except ImportError:
        return {
            "status": "unavailable", "app": "quantum-optimization", "technique": "GJQ-QAOA",
            "result": {"code": "optional_dependency_missing", "message": "Qiskit/gjq-client indisponível."},
            "evidence": {"jobs_submitted": 0, "hardware_executed": False},
            "limitations": ["Dependências opcionais não instaladas; nenhum job foi enviado."],
        }

    jobs_attempted = 0
    backend_type = None
    try:
        with redirect_stdout(io.StringIO()):
            service = sdk.GJQRuntimeService(api_key=api_key)
            backends = service.list_backends()
        selected = next((row for row in backends
                         if _backend_value(row, "name") == backend_name), None)
        if selected is None:
            return _blocked("backend_not_found", "nome de backend não apareceu na lista atual do provedor.")
        backend_type = _backend_value(selected, "type")
        if not is_confirmed_hardware_type(backend_type):
            return _blocked("backend_not_confirmed_hardware", "tipo do backend não confirma hardware quântico.")
        backend = service.backend(backend_name)
        circuit, gammas, betas = build_qiskit_circuit(qubo, depth, sdk)
        pass_manager = sdk.generate_preset_pass_manager(
            backend=backend, optimization_level=2, seed_transpiler=seed
        )
        sampler = sdk.Sampler(backend=backend)

        def evaluate(angles: list[float]) -> float:
            nonlocal jobs_attempted
            bindings = {gammas[i]: angles[i] for i in range(depth)}
            bindings.update({betas[i]: angles[depth + i] for i in range(depth)})
            bound = circuit.assign_parameters(bindings, inplace=False)
            isa = pass_manager.run(bound)
            # Count the attempt before calling the provider: a timeout can leave
            # submission state uncertain, so it must not be silently retried.
            jobs_attempted += 1
            with redirect_stdout(io.StringIO()):
                job = sampler.run(isa, shots=shots)
                result = job.result(timeout=300)
            counts = result.get("counts") if hasattr(result, "get") else result["counts"]
            return energy_from_counts(qubo, counts)["mean_energy"]

        optimized = bounded_angle_search(
            evaluate, depth=depth, max_evaluations=max_evaluations, seed=seed
        )
        return {
            "status": "success",
            "app": "quantum-optimization",
            "technique": "QAOA on GJQ provider-reported quantum hardware",
            "result": {
                **optimized,
                "problem_sha256": qubo.problem_sha256,
                "backend_name": backend_name,
                "backend_type": backend_type,
                "shots_per_job": shots,
            },
            "evidence": {
                "provider": "GJQRuntimeService",
                "backend_type_reported_by_provider": backend_type,
                "jobs_submitted": jobs_attempted,
                "total_shots": jobs_attempted * shots,
                "hardware_executed": jobs_attempted > 0,
                "external_validation": False,
            },
            "limitations": [
                "Backend type is the provider's current report, not independent hardware certification.",
                "Bounded coordinate search is heuristic; global optimality and quantum advantage are not established.",
                "Shot/job caps do not bound monetary charges; provider pricing and quota were not queried.",
                "GJQ SDK may cache account configuration locally; see upstream security documentation.",
            ],
        }
    except Exception as exc:  # External failures can have an uncertain submit state.
        return {
            "status": "partial" if jobs_attempted else "error",
            "app": "quantum-optimization",
            "technique": "GJQ-QAOA",
            "result": {
                "code": "provider_execution_error",
                "error_type": type(exc).__name__,
                "submission_state": "uncertain" if jobs_attempted else "not_submitted",
                "problem_sha256": qubo.problem_sha256,
            },
            "evidence": {
                "backend_name": backend_name,
                "backend_type_reported_by_provider": backend_type,
                "jobs_submitted_or_uncertain": jobs_attempted,
                "hardware_executed": False,
                "automatic_retry": False,
            },
            "limitations": [
                "Provedor falhou; resposta sem mensagem bruta para evitar vazamento de dados.",
                "Uma chamada que lançou exceção pode ter sido aceita remotamente; verificar o painel antes de repetir.",
            ],
        }
