"""R1128 — aprendibilidade de Pauli e grafo de padrões do CZ.

Base: Chen, Liu, Otten, Seif, Fefferman e Jiang, "The learnability of Pauli
noise", Nature Communications 14, 52 (2023), DOI 10.1038/s41467-022-35759-4,
Teoremas 1 e 2.

Para um Clifford de 2 qubits, o espaço de funções aprendíveis é o espaço de
ciclos do grafo de transferência de padrões; o não aprendível é o espaço de
cortes. O CZ tem 15 arestas, 4 vértices e 2 componentes: 13 funções
aprendíveis e 2 não aprendíveis. O posto 9 da R1126 é apenas o subespaço
medido por médias de órbita, não o limite fundamental. Nada aqui executa
hardware, rede ou submissão.
"""
from __future__ import annotations

import itertools

import numpy as np
from scipy.linalg import null_space, orth

PAULIS_2Q = [
    "".join(chars)
    for chars in itertools.product("IXYZ", repeat=2)
    if chars != ("I", "I")
]
VERTICES = ("00", "01", "10", "11")
_XZ = {"I": (0, 0), "X": (1, 0), "Y": (1, 1), "Z": (0, 1)}
_CHAR = {value: key for key, value in _XZ.items()}
SOURCE = {
    "authors": "Chen, Liu, Otten, Seif, Fefferman e Jiang",
    "title": "The learnability of Pauli noise",
    "journal": "Nature Communications 14, 52 (2023)",
    "doi": "10.1038/s41467-022-35759-4",
    "theorem": "2",
    "url": "https://www.nature.com/articles/s41467-022-35759-4",
}
LIMITS = (
    "13 funções aprendíveis e 2 não aprendíveis para o CZ sob ruído de Pauli "
    "e SPAM twirlado. As 2 funções de corte exigem hipótese adicional "
    "(preparação perfeita, GST ou restrição física) e não são medidas pelo "
    "CB padrão. Cliffords de 1 qubit intercalados são supostos suficientemente "
    "menos ruidosos; isso não foi validado no Baihua. Nenhuma taxa foi medida; "
    "PEC 2q permanece bloqueado."
)


def pauli_weight_pattern(label: str) -> str:
    if label not in PAULIS_2Q:
        raise ValueError(f"Pauli de 2 qubits inválido: {label}")
    return "".join("0" if char == "I" else "1" for char in label)


def cz_image(label: str) -> str:
    if label not in PAULIS_2Q:
        raise ValueError(f"Pauli de 2 qubits inválido: {label}")
    (x1, z1), (x0, z0) = (_XZ[char] for char in label)
    return _CHAR[(x1, z1 ^ x0)] + _CHAR[(x0, z0 ^ x1)]


def _identity_image(label: str) -> str:
    if label not in PAULIS_2Q:
        raise ValueError(f"Pauli de 2 qubits inválido: {label}")
    return label


def _image(kind: str, label: str) -> str:
    if kind == "cz":
        return cz_image(label)
    if kind == "identity":
        return _identity_image(label)
    raise ValueError("kind deve ser 'cz' ou 'identity'")


def incidence_matrix(kind: str = "cz") -> np.ndarray:
    """Matriz B (4x15): aresta liga padrão de entrada ao de saída."""
    matrix = np.zeros((4, 15), dtype=float)
    index = {vertex: position for position, vertex in enumerate(VERTICES)}
    for column, label in enumerate(PAULIS_2Q):
        source = pauli_weight_pattern(label)
        target = pauli_weight_pattern(_image(kind, label))
        matrix[index[source], column] += 1.0
        matrix[index[target], column] -= 1.0
    return matrix


def _components(edges: list[dict]) -> int:
    parent = {vertex: vertex for vertex in VERTICES}

    def find(vertex):
        while parent[vertex] != vertex:
            parent[vertex] = parent[parent[vertex]]
            vertex = parent[vertex]
        return vertex

    def union(left, right):
        root_left, root_right = find(left), find(right)
        if root_left != root_right:
            parent[root_right] = root_left

    for edge in edges:
        union(edge["source"], edge["target"])
    return len({find(vertex) for vertex in VERTICES})


def _vector_to_dict(vector: np.ndarray) -> dict[str, float]:
    rounded = np.round(np.asarray(vector, dtype=float), 12)
    return {
        label: float(value)
        for label, value in zip(PAULIS_2Q, rounded)
    }


def _basis_matrix_to_dicts(matrix: np.ndarray) -> list[dict[str, float]]:
    return [_vector_to_dict(matrix[:, column]) for column in range(matrix.shape[1])]


def pattern_graph(kind: str = "cz") -> dict:
    edges = []
    for label in PAULIS_2Q:
        source = pauli_weight_pattern(label)
        target = pauli_weight_pattern(_image(kind, label))
        edges.append(
            {
                "pauli": label,
                "source": source,
                "target": target,
                "preserved": bool(source == target),
                "image": _image(kind, label),
            }
        )
    matrix = incidence_matrix(kind)
    rank = int(np.linalg.matrix_rank(matrix))
    cycle = null_space(matrix)
    cut = orth(matrix.T)
    components = _components(edges)
    return {
        "kind": kind,
        "paulis": len(edges),
        "vertices": list(VERTICES),
        "components": components,
        "cycle_rank": int(cycle.shape[1]),
        "cut_rank": int(cut.shape[1]),
        "learnable_dimension": int(cycle.shape[1]),
        "unlearnable_dimension": int(cut.shape[1]),
        "edges": edges,
        "individually_learnable": [
            edge["pauli"] for edge in edges if edge["preserved"]
        ],
        "cycle_basis": _basis_matrix_to_dicts(cycle),
        "cut_basis": _basis_matrix_to_dicts(cut),
    }


def compare_with_orbit_design() -> dict:
    from .cb_rank_bounds import orbit_average_rank

    orbit_rank = orbit_average_rank("cz")
    learnable = pattern_graph("cz")["learnable_dimension"]
    return {
        "orbit_rank": int(orbit_rank),
        "learnable_rank": int(learnable),
        "missing": int(learnable - orbit_rank),
        "missing_reason": (
            "O desenho de médias de órbita não insere Cliffords de 1 qubit "
            "para mapear o Pauli de volta ao mesmo padrão; mede 9 das 13 "
            "funções aprendíveis."
        ),
        "note": (
            "O posto 9 não é o limite fundamental; 13 é o espaço de ciclos e "
            "2 funções permanecem não aprendíveis sem hipótese adicional."
        ),
    }


def audit() -> dict:
    cz = pattern_graph("cz")
    identity = pattern_graph("identity")
    return {
        "schema_version": 1,
        "source": SOURCE,
        "cz": cz,
        "identity": {
            "components": identity["components"],
            "cycle_rank": identity["cycle_rank"],
            "cut_rank": identity["cut_rank"],
            "note": "identidade: todas as fidelidades aprendíveis, mas não é um ciclo físico comparável ao CZ",
        },
        "comparison": compare_with_orbit_design(),
        "interpretation": [
            "fidelidade individual é aprendível se e somente se o padrão de peso é preservado",
            "funções aprendíveis formam o espaço de ciclos do grafo de padrões",
            "funções não aprendíveis formam o espaço de cortes",
            "CB é ótimo para a informação aprendível; não resolve o corte",
        ],
        "limits": LIMITS,
        "rates_measured": False,
        "pec_hardware_allowed": False,
        "hardware_executed": False,
    }
