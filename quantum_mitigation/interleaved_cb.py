"""R1129 — CB com correções de 1 qubit para 13 funções do CZ.

Base: Chen et al., Nat. Commun. 14, 52 (2023), DOI 10.1038/s41467-022-35759-4.
Sete ciclos individuais e seis ciclos de pares formam uma base de 13 funções
aprendíveis do CZ. As 2 funções de corte permanecem não aprendíveis.

Convenção: ruído de Pauli **antes** de cada CZ, como no modelo do artigo.
As correções de 1 qubit são ideais por padrão; o simulador aceita
`correction_rate` para depolarização 1q após cada correção e `twirl=True`
para twirl de Pauli em cada CZ, com registro dos frames. Nada aqui executa
hardware, rede ou submissão.
"""
from __future__ import annotations

import hashlib
import json
from collections import deque

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import HGate, SGate, SdgGate, XGate, YGate, ZGate
from qiskit.quantum_info import Clifford, DensityMatrix, Pauli, Statevector

from .cb_learnability import PAULIS_2Q, cz_image, incidence_matrix, pauli_weight_pattern
from .randomized_compiling import conjugate_pauli, pauli_frame_pass

INDIVIDUAL = (
    "IZ", "ZI", "XX", "XY", "YX", "YY", "ZZ",
)
PAIR_CYCLES = (
    ("IX", "ZX"),
    ("IX", "ZY"),
    ("IY", "ZX"),
    ("XI", "XZ"),
    ("XI", "YZ"),
    ("YI", "XZ"),
)
FUNCTIONS = tuple((label,) for label in INDIVIDUAL) + PAIR_CYCLES
DEPTHS = (0, 2, 4, 8, 16)
_XZ = {"I": (0, 0), "X": (1, 0), "Y": (1, 1), "Z": (0, 1)}
LIMITS = (
    "13 funções aprendíveis; 2 funções de corte não são medidas. Ruído de "
    "Pauli antes do CZ, correções de 1 qubit ideais e profundidades pares. "
    "A hipótese de correções suficientemente menos ruidosas não foi validada "
    "no Baihua; nenhuma taxa foi medida e PEC 2q permanece bloqueado."
)


def _one_qubit_table() -> list[tuple[Clifford, tuple[str, ...]]]:
    start = Clifford(QuantumCircuit(1))
    table: list[tuple[Clifford, tuple[str, ...]]] = [(start, ())]
    queue = deque([start])
    while queue:
        clifford = queue.popleft()
        sequence = next(seq for item, seq in table if item == clifford)
        for name, gate in (("h", lambda circuit: circuit.h(0)), ("s", lambda circuit: circuit.s(0))):
            circuit = QuantumCircuit(1)
            circuit.compose(clifford.to_circuit(), inplace=True)
            gate(circuit)
            candidate = Clifford(circuit)
            if not any(item == candidate for item, _ in table):
                table.append((candidate, sequence + (name,)))
                queue.append(candidate)
    return table


_TABLE = _one_qubit_table()


def _find_sequence(source: str, target: str) -> tuple[str, ...]:
    for clifford, sequence in _TABLE:
        if str(conjugate_pauli(clifford, Pauli(source))) == target:
            return sequence
    raise ValueError(f"sem Clifford de 1 qubit para {source} -> {target}")


def correction_gates(source: str, target: str) -> list[tuple[str, int]]:
    """Gates de 1 qubit que levam source a target (mesmo padrão de peso)."""
    if source not in PAULIS_2Q or target not in PAULIS_2Q:
        raise ValueError("Pauli de 2 qubits inválido")
    if pauli_weight_pattern(source) != pauli_weight_pattern(target):
        raise ValueError("correção de 1 qubit não muda o padrão de peso")
    gates: list[tuple[str, int]] = []
    for qubit, (left, right) in enumerate(zip(reversed(source), reversed(target))):
        if left == right:
            continue
        if "I" in (left, right):
            raise ValueError("não é possível corrigir identidade para não-identidade")
        for gate in _find_sequence(left, right):
            gates.append((gate, qubit))
    return gates


_MARKED = {
    "h": HGate,
    "s": SGate,
    "sdg": SdgGate,
    "x": XGate,
    "y": YGate,
    "z": ZGate,
}


def _apply(
    circuit: QuantumCircuit,
    gates: list[tuple[str, int]],
    *,
    mark: bool = False,
) -> None:
    for gate, qubit in gates:
        if mark:
            circuit.append(_MARKED[gate](label="corr"), [qubit])
        else:
            getattr(circuit, gate)(qubit)


def _prepare(circuit: QuantumCircuit, pauli: str) -> None:
    for qubit, char in enumerate(reversed(pauli)):
        if char in "XY":
            circuit.h(qubit)
        if char == "Y":
            circuit.s(qubit)
    circuit.barrier()


def _measure_basis(circuit: QuantumCircuit, pauli: str) -> None:
    for qubit, char in enumerate(reversed(pauli)):
        if char == "Y":
            circuit.sdg(qubit)
        if char in "XY":
            circuit.h(qubit)
    circuit.barrier()


def validate_cycle(cycle) -> tuple[str, ...]:
    cycle = tuple(cycle)
    if not cycle:
        raise ValueError("ciclo vazio")
    if any(label not in PAULIS_2Q for label in cycle):
        raise ValueError("ciclo contém Pauli inválido")
    for index, label in enumerate(cycle):
        expected = pauli_weight_pattern(cycle[(index + 1) % len(cycle)])
        if pauli_weight_pattern(cz_image(label)) != expected:
            raise ValueError(f"ciclo não fecha em {label}")
    return cycle


def cycle_body_framed(
    cycle,
    depth: int,
    *,
    twirl: bool = False,
    seed: int = 0,
) -> tuple[QuantumCircuit, list[dict]]:
    """Circuito sem base de medida, com frames de twirl registrados."""
    cycle = validate_cycle(cycle)
    if isinstance(depth, bool) or not isinstance(depth, int) or depth < 0:
        raise ValueError("depth deve ser inteiro >= 0")
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise ValueError("seed deve ser inteiro >= 0")
    circuit = QuantumCircuit(2)
    _prepare(circuit, cycle[0])
    frames: list[dict] = []
    twirl_index = 0
    for depth_index in range(depth):
        current = cycle[0]
        for label in cycle:
            if current != label:
                _apply(circuit, correction_gates(current, label), mark=True)
            if twirl:
                single = QuantumCircuit(2)
                single.cz(0, 1)
                result = pauli_frame_pass(single, seed=seed + twirl_index)
                circuit.compose(result["circuit"], inplace=True)
                frames.append(
                    {
                        "depth_index": depth_index,
                        "cycle": list(cycle),
                        "twirls": result["twirls"],
                    }
                )
                twirl_index += 1
            else:
                circuit.cz(0, 1)
            current = cz_image(label)
        if current != cycle[0]:
            _apply(circuit, correction_gates(current, cycle[0]), mark=True)
    return circuit, frames


def cycle_body(cycle, depth: int, *, twirl: bool = False, seed: int = 0) -> QuantumCircuit:
    """Circuito sem base de medida; ruído é injetado pelo simulador."""
    return cycle_body_framed(cycle, depth, twirl=twirl, seed=seed)[0]


def cycle_circuit(cycle, depth: int) -> QuantumCircuit:
    body = cycle_body(cycle, depth)
    circuit = QuantumCircuit(2, 2)
    circuit.compose(body, inplace=True)
    _measure_basis(circuit, validate_cycle(cycle)[0])
    circuit.measure([0, 1], [0, 1])
    return circuit


def design_matrix() -> np.ndarray:
    matrix = np.zeros((len(FUNCTIONS), 15), dtype=float)
    for row, cycle in enumerate(FUNCTIONS):
        for label in cycle:
            matrix[row, PAULIS_2Q.index(label)] += 1.0
    return matrix


def design_rank() -> dict:
    matrix = design_matrix()
    rank = int(np.linalg.matrix_rank(matrix))
    return {
        "rank": rank,
        "n_functions": len(FUNCTIONS),
        "n_fidelities": 15,
        "nullity": 15 - rank,
        "full_cycle_space": bool(rank == 13),
        "incidence_residual": float(
            np.max(np.abs(incidence_matrix("cz") @ matrix.T))
        ),
    }


def _anticommutes(left: str, right: str) -> int:
    return sum(
        _XZ[a][0] * _XZ[b][1] + _XZ[a][1] * _XZ[b][0]
        for a, b in zip(left, right)
    ) % 2


def true_function(cycle, rates: dict) -> float:
    cycle = validate_cycle(cycle)
    if set(rates) != set(PAULIS_2Q):
        raise ValueError("taxas devem cobrir os 15 Paulis")
    product = 1.0
    for label in cycle:
        exponent = sum(rates[q] for q in PAULIS_2Q if _anticommutes(label, q))
        product *= float(np.exp(-2.0 * exponent))
    return product


def _depolarize_1q(
    rho: DensityMatrix,
    qubit: int,
    probability: float,
) -> DensityMatrix:
    if probability <= 0:
        return rho
    labels = ("IX", "IY", "IZ") if qubit == 0 else ("XI", "YI", "ZI")
    data = (1.0 - probability) * rho.data
    for label in labels:
        matrix = Pauli(label).to_matrix()
        data = data + (probability / 3.0) * (
            matrix @ rho.data @ matrix.conj().T
        )
    return DensityMatrix(data)


def simulate_expectation(
    cycle,
    depth: int,
    rates: dict,
    *,
    twirl: bool = False,
    seed: int = 0,
    correction_rate: float = 0.0,
) -> float:
    """Matriz densidade com ruído Pauli antes de cada CZ (convenção do artigo)."""
    if set(rates) != set(PAULIS_2Q):
        raise ValueError("taxas devem cobrir os 15 Paulis")
    if not 0.0 <= correction_rate <= 1.0:
        raise ValueError("correction_rate deve estar em [0,1]")
    body = cycle_body(cycle, depth, twirl=twirl, seed=seed)
    rho = DensityMatrix.from_label("00")
    operators = [
        (Pauli(label).to_matrix(), -np.expm1(-2.0 * rates[label]) / 2.0)
        for label in PAULIS_2Q
        if rates[label] > 0
    ]
    for instruction in body.data:
        operation = instruction.operation
        qargs = [body.find_bit(qubit).index for qubit in instruction.qubits]
        if operation.name == "cz":
            data = rho.data
            for matrix, probability in operators:
                data = (1.0 - probability) * data + probability * (
                    matrix @ data @ matrix.conj().T
                )
            rho = DensityMatrix(data)
            rho = rho.evolve(operation, qargs=qargs)
            continue
        rho = rho.evolve(operation, qargs=qargs)
        if operation.label == "corr" and correction_rate > 0:
            if len(qargs) != 1:
                raise ValueError("correção marcada deve ser de 1 qubit")
            rho = _depolarize_1q(rho, qargs[0], correction_rate)
    return float(np.real(rho.expectation_value(Pauli(cycle[0]))))


def _fit_decay(points: list[tuple[int, float]]) -> dict:
    positive = [(depth, value) for depth, value in points if value > 0]
    if len(positive) < 2:
        return {"status": "blocked_nonpositive", "f": None, "amplitude": None}
    depths = np.asarray([item[0] for item in positive], dtype=float)
    values = np.log(np.asarray([item[1] for item in positive], dtype=float))
    design = np.column_stack([np.ones_like(depths), depths])
    coefficients, *_ = np.linalg.lstsq(design, values, rcond=None)
    return {
        "status": "fit",
        "amplitude": float(np.exp(coefficients[0])),
        "f": float(np.exp(coefficients[1])),
        "n_points": len(positive),
    }


def recover_function(
    cycle,
    rates: dict,
    depths=DEPTHS,
    *,
    twirl: bool = False,
    seed: int = 0,
    correction_rate: float = 0.0,
) -> dict:
    cycle = validate_cycle(cycle)
    points = [
        (
            int(depth),
            simulate_expectation(
                cycle,
                int(depth),
                rates,
                twirl=twirl,
                seed=seed,
                correction_rate=correction_rate,
            ),
        )
        for depth in depths
    ]
    fit = _fit_decay(points)
    truth = true_function(cycle, rates)
    return {
        "cycle": list(cycle),
        "points": points,
        "fit": fit,
        "truth": truth,
        "absolute_error": None if fit["f"] is None else abs(fit["f"] - truth),
    }


def audit(
    rates: dict | None = None,
    *,
    twirl: bool = False,
    seed: int = 0,
    correction_rate: float = 0.0,
) -> dict:
    if rates is None:
        rates = {label: 0.002 for label in PAULIS_2Q}
    if set(rates) != set(PAULIS_2Q):
        raise ValueError("taxas devem cobrir os 15 Paulis")
    recoveries = [
        recover_function(
            cycle,
            rates,
            twirl=twirl,
            seed=seed,
            correction_rate=correction_rate,
        )
        for cycle in FUNCTIONS
    ]
    errors = [item["absolute_error"] for item in recoveries if item["absolute_error"] is not None]
    return {
        "schema_version": 1,
        "source": {
            "authors": "Chen, Liu, Otten, Seif, Fefferman e Jiang",
            "title": "The learnability of Pauli noise",
            "journal": "Nature Communications 14, 52 (2023)",
            "doi": "10.1038/s41467-022-35759-4",
        },
        "functions": [list(cycle) for cycle in FUNCTIONS],
        "individual": list(INDIVIDUAL),
        "pair_cycles": [list(cycle) for cycle in PAIR_CYCLES],
        "design": design_rank(),
        "recovery": recoveries,
        "max_absolute_error": max(errors) if errors else None,
        "n_recovered": sum(item["fit"]["status"] == "fit" for item in recoveries),
        "unlearnable_cut_rank": 2,
        "twirl": bool(twirl),
        "seed": int(seed),
        "correction_rate": float(correction_rate),
        "rates_measured": False,
        "pec_hardware_allowed": False,
        "hardware_executed": False,
        "limits": LIMITS,
    }


def noise_audit(
    rates: dict | None = None,
    *,
    correction_rates=(0.0, 0.001, 0.005, 0.01),
    twirl_values=(False, True),
    seed: int = 0,
) -> dict:
    """Simula degradação por ruído 1q nas correções e por twirl de Pauli."""
    if rates is None:
        rates = {label: 0.002 for label in PAULIS_2Q}
    if set(rates) != set(PAULIS_2Q):
        raise ValueError("taxas devem cobrir os 15 Paulis")
    results = []
    for twirl in twirl_values:
        for correction_rate in correction_rates:
            recoveries = [
                recover_function(
                    cycle,
                    rates,
                    twirl=bool(twirl),
                    seed=seed,
                    correction_rate=float(correction_rate),
                )
                for cycle in FUNCTIONS
            ]
            errors = [
                item["absolute_error"]
                for item in recoveries
                if item["absolute_error"] is not None
            ]
            results.append(
                {
                    "twirl": bool(twirl),
                    "correction_rate": float(correction_rate),
                    "n_recovered": sum(
                        item["fit"]["status"] == "fit" for item in recoveries
                    ),
                    "max_absolute_error": max(errors) if errors else None,
                    "per_function_error": {
                        "·".join(item["cycle"]): item["absolute_error"]
                        for item in recoveries
                    },
                }
            )
    return {
        "schema_version": 1,
        "n_functions": len(FUNCTIONS),
        "results": results,
        "hardware_executed": False,
        "rates_measured": False,
        "limits": (
            "Simulação de depolarização 1q após cada correção e twirl de Pauli "
            "em cada CZ. Não é ruído real do Baihua; twirl e correções não "
            "foram executados em hardware. As 2 funções de corte não são medidas."
        ),
    }


def _canonical_sha256(payload: dict) -> str:
    text = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_preregistration(
    *,
    shots: int = 4096,
    twirl: bool = True,
    correction_rate: float = 0.002,
    seed: int = 1129,
    twirl_seeds=(1, 2, 3, 4, 5),
) -> dict:
    """Pré-registro local do desenho; não autoriza hardware."""
    if isinstance(shots, bool) or not isinstance(shots, int) or shots < 1:
        raise ValueError("shots deve ser inteiro >= 1")
    if not 0.0 <= correction_rate <= 1.0:
        raise ValueError("correction_rate deve estar em [0,1]")
    twirl_seeds = tuple(int(item) for item in twirl_seeds)
    if twirl and not twirl_seeds:
        raise ValueError("twirl exige ao menos uma seed")
    jobs = len(FUNCTIONS) * len(DEPTHS) * (len(twirl_seeds) if twirl else 1)
    payload = {
        "schema_version": 1,
        "protocol": "r1130-interleaved-cb-preregistration",
        "source": {
            "doi": "10.1038/s41467-022-35759-4",
            "title": "The learnability of Pauli noise",
        },
        "functions": [list(cycle) for cycle in FUNCTIONS],
        "individual": list(INDIVIDUAL),
        "pair_cycles": [list(cycle) for cycle in PAIR_CYCLES],
        "depths": list(DEPTHS),
        "shots": int(shots),
        "twirl": bool(twirl),
        "twirl_seeds": list(twirl_seeds),
        "correction_noise": {
            "model": "depolarizacao 1q apos cada correcao",
            "rate": float(correction_rate),
        },
        "seed": int(seed),
        "jobs": jobs,
        "total_shots": jobs * int(shots),
        "decision_rules": [
            "so avancar se 13/13 funcoes forem recuperadas em simulacao",
            "se twirl ou ruido das correcoes reduzir a recuperacao, bloquear hardware",
            "as 2 funcoes de corte nao sao medidas por este desenho",
            "nenhuma submissao sem autorizacao explicita e compilacao auditada",
        ],
        "hardware_submission_allowed": False,
        "analysis_allowed": False,
        "limits": (
            "Pre-registro de planejamento. Nao e prova de execucao, nao mede "
            "taxas e nao valida o ruido real das correcoes. As 2 funcoes de "
            "corte continuam fora do CB."
        ),
    }
    payload["manifest_sha256"] = _canonical_sha256(payload)
    return payload


def validate_preregistration(payload: dict) -> None:
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError("pre-registro v1 exigido")
    try:
        expected = build_preregistration(
            shots=payload["shots"],
            twirl=payload["twirl"],
            correction_rate=payload["correction_noise"]["rate"],
            seed=payload["seed"],
            twirl_seeds=payload["twirl_seeds"],
        )
    except (KeyError, TypeError) as exc:
        raise ValueError("pre-registro incompleto") from exc
    if payload != expected:
        raise ValueError("pre-registro alterado ou divergente")
