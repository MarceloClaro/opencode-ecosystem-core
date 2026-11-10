"""R1126 — limites de posto e aumento de desenho no CB do CZ.

Resultado central: o posto 9 é específico do desenho somente-CZ. A matriz de
anticomutação completa tem posto 15. Acrescentar outros ciclos Cliffords pode
elevar o posto a 15 **se** o mesmo gerador de Pauli-Lindblad (ou um gerador
conjugado por transformação conhecida) governar todos os ciclos. Se cada ciclo
tiver seu próprio gerador, o desenho continua subdeterminado (9k equações para
15k incógnitas). Nada aqui executa hardware, rede ou submissão.
"""
from __future__ import annotations

import itertools

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Clifford, Pauli, random_clifford

from .randomized_compiling import conjugate_pauli

PAULIS_2Q = [
    "".join(chars)
    for chars in itertools.product("IXYZ", repeat=2)
    if chars != ("I", "I")
]
LOCAL_LABELS = ("XI", "YI", "ZI", "IX", "IY", "IZ")
TWO_QUBIT_LABELS = tuple(
    label for label in PAULIS_2Q if label[0] != "I" and label[1] != "I"
)
_XZ = {"I": (0, 0), "X": (1, 0), "Y": (1, 1), "Z": (0, 1)}
LIMITS = (
    "Análise linear local. O posto 15 com ciclos extras supõe gerador "
    "compartilhado/conjugado; não foi medido nem validado no Baihua. "
    "Identidade não é um ciclo físico comparável ao CZ. Submodelos locais "
    "só são identificáveis se as demais taxas forem nulas por hipótese. "
    "Nenhuma taxa foi medida; nada foi executado em hardware; PEC 2q permanece bloqueado."
)


def _anticommutes(left: str, right: str) -> int:
    return sum(
        _XZ[a][0] * _XZ[b][1] + _XZ[a][1] * _XZ[b][0]
        for a, b in zip(left, right)
    ) % 2


def anticommutation_matrix() -> np.ndarray:
    """Matriz D (15x15): y_P = soma_Q D[P,Q] gamma_Q."""
    return np.array(
        [[_anticommutes(p, q) for q in PAULIS_2Q] for p in PAULIS_2Q],
        dtype=float,
    )


def full_matrix_rank() -> int:
    return int(np.linalg.matrix_rank(anticommutation_matrix()))


def _clifford(kind) -> Clifford:
    if kind == "cz":
        circuit = QuantumCircuit(2)
        circuit.cz(0, 1)
        return Clifford(circuit)
    if kind == "identity":
        return Clifford(QuantumCircuit(2))
    if isinstance(kind, tuple) and len(kind) == 2 and kind[0] == "random":
        seed = kind[1]
        if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
            raise ValueError("semente aleatória deve ser inteiro >= 0")
        return random_clifford(2, seed=seed)
    raise ValueError("ciclo deve ser 'cz', 'identity' ou ('random', seed)")


def clifford_permutation(kind) -> list[int]:
    """Permutação P -> U P U† nos 15 Paulis, na ordem PAULIS_2Q."""
    clifford = _clifford(kind)
    permutation = []
    for label in PAULIS_2Q:
        image = str(conjugate_pauli(clifford, Pauli(label)))
        if image not in PAULIS_2Q:
            raise ValueError(f"imagem Pauli inválida: {image}")
        permutation.append(PAULIS_2Q.index(image))
    return permutation


def cz_orbits() -> list[tuple[str, ...]]:
    """Órbitas do CZ, ordenadas pela primeira ocorrência em PAULIS_2Q."""
    permutation = clifford_permutation("cz")
    seen: set[int] = set()
    orbits: list[tuple[str, ...]] = []
    for start in range(15):
        if start in seen:
            continue
        orbit: list[int] = []
        current = start
        while current not in orbit:
            orbit.append(current)
            current = permutation[current]
        seen.update(orbit)
        orbits.append(tuple(sorted(PAULIS_2Q[index] for index in orbit)))
    return sorted(orbits, key=lambda orbit: PAULIS_2Q.index(orbit[0]))


def orbit_average_matrix(kind) -> np.ndarray:
    """Matriz A_U D: cada linha é a média de D sobre a órbita de U."""
    permutation = clifford_permutation(kind)
    design = anticommutation_matrix()
    matrix = np.zeros((15, 15), dtype=float)
    seen: set[int] = set()
    for start in range(15):
        if start in seen:
            continue
        orbit: list[int] = []
        current = start
        while current not in orbit:
            orbit.append(current)
            current = permutation[current]
        seen.update(orbit)
        average = design[orbit].mean(axis=0)
        for index in orbit:
            matrix[index] = average
    if not np.all(np.isfinite(matrix)):
        raise ValueError("matriz de órbita não finita")
    return matrix


def orbit_average_rank(kind) -> int:
    return int(np.linalg.matrix_rank(orbit_average_matrix(kind)))


def stacked_rank(kinds: list) -> dict:
    """Posto do desenho empilhado sob a hipótese de gerador compartilhado."""
    if not kinds:
        raise ValueError("pelo menos um ciclo é necessário")
    matrices = [orbit_average_matrix(kind) for kind in kinds]
    stacked = np.vstack(matrices)
    rank = int(np.linalg.matrix_rank(stacked))
    return {
        "rank": rank,
        "n_rows": int(stacked.shape[0]),
        "n_columns": int(stacked.shape[1]),
        "full_column_rank": bool(rank == 15),
        "condition_number": float(np.linalg.cond(stacked)) if rank == 15 else float("inf"),
        "per_cycle_ranks": [int(np.linalg.matrix_rank(m)) for m in matrices],
        "assumption": "mesmo gerador de Pauli-Lindblad para todos os ciclos",
    }


def submodel_rank(labels) -> dict:
    """Posto ao restringir as incógnitas a um subconjunto de Paulis."""
    labels = tuple(labels)
    unknown = set(labels)
    if not unknown or not unknown <= set(PAULIS_2Q):
        raise ValueError("submodelo deve usar rótulos Pauli válidos")
    columns = [PAULIS_2Q.index(label) for label in labels]
    matrix = anticommutation_matrix()[:, columns]
    rank = int(np.linalg.matrix_rank(matrix))
    return {
        "labels": labels,
        "n_parameters": len(labels),
        "rank": rank,
        "identifiable": bool(rank == len(labels)),
        "requires_other_rates_zero": True,
        "note": (
            "O posto mede identificabilidade apenas sob a hipótese de que todas "
            "as taxas fora do submodelo são nulas."
        ),
    }


def separate_generator_audit(cycles: int) -> dict:
    """Cada ciclo com gerador próprio: 9k equações para 15k incógnitas."""
    if isinstance(cycles, bool) or not isinstance(cycles, int) or cycles < 1:
        raise ValueError("cycles deve ser inteiro >= 1")
    rank = 9 * cycles
    unknowns = 15 * cycles
    return {
        "cycles": cycles,
        "rank": rank,
        "unknowns": unknowns,
        "deficiency": unknowns - rank,
        "identifiable": False,
        "reason": (
            "cada ciclo tem 15 taxas próprias e fornece no máximo 9 "
            "combinações independentes; a deficiência cresce 6 por ciclo"
        ),
    }


def augmentation_search(
    *,
    seeds=range(4),
    max_cycles: int = 4,
) -> dict:
    """Busca gulosa determinística por um conjunto que atinja posto 15."""
    seeds = tuple(int(seed) for seed in seeds)
    if not seeds:
        raise ValueError("seeds não pode ser vazio")
    if max_cycles < 1:
        raise ValueError("max_cycles deve ser >= 1")
    selected: list[tuple[str, int]] = []
    current_rank = orbit_average_rank("cz")
    current_kinds: list = ["cz"]
    while current_rank < 15 and len(selected) < max_cycles:
        best = None
        for seed in seeds:
            if ("random", seed) in selected:
                continue
            candidate = stacked_rank(current_kinds + [("random", seed)])
            key = (candidate["rank"], -seed)
            if best is None or key > best[0]:
                best = (key, seed, candidate)
        if best is None:
            break
        _, seed, candidate = best
        if candidate["rank"] <= current_rank:
            break
        selected.append(("random", seed))
        current_kinds.append(("random", seed))
        current_rank = candidate["rank"]
    result = stacked_rank(current_kinds)
    return {
        "status": "design_found" if result["rank"] == 15 else "not_found",
        "selected_seeds": [seed for _, seed in selected],
        "cycles": ["cz"] + [f"random:{seed}" for _, seed in selected],
        "rank": result["rank"],
        "condition_number": result["condition_number"],
        "per_cycle_ranks": result["per_cycle_ranks"],
        "assumption": "mesmo gerador conjugado para todos os ciclos",
        "limits": (
            "Existência matemática, não validação física. Os ciclos aleatórios "
            "adicionam portas e ruído próprio; a hipótese de gerador compartilhado "
            "precisa de evidência independente."
        ),
        "hardware_executed": False,
    }


def audit() -> dict:
    local = submodel_rank(LOCAL_LABELS)
    twoq = submodel_rank(TWO_QUBIT_LABELS)
    augmentation = augmentation_search(seeds=range(4))
    return {
        "schema_version": 1,
        "full_matrix_rank": full_matrix_rank(),
        "cz_only_rank": orbit_average_rank("cz"),
        "identity_rank": orbit_average_rank("identity"),
        "identity_note": "não é um ciclo físico comparável ao CZ",
        "cz_orbits": [list(orbit) for orbit in cz_orbits()],
        "augmentation": {**augmentation, "rank_possible": augmentation["rank"]},
        "separate_generators": separate_generator_audit(3),
        "local_submodel": local,
        "two_qubit_submodel": twoq,
        "assumptions": [
            "mesmo gerador de Pauli-Lindblad (ou conjugado conhecido) entre ciclos",
            "profundidades pares e observáveis de paridade",
            "submodelos exigem que as taxas excluídas sejam nulas",
        ],
        "limits": LIMITS,
        "rates_measured": False,
        "pec_hardware_allowed": False,
        "hardware_executed": False,
    }
