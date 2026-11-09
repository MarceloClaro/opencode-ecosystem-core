"""Templates OpenQASM 2.0 para experimentos GJQ (SPEC-935-R1105).

São textos de referência; não são executados por este módulo. CHSH retorna
quatro circuitos (ZZ, ZX, XZ, XX) para medir o mesmo estado de Bell em bases
diferentes. Nenhum template declara fidelidade ou resultado.
"""
from __future__ import annotations

import copy
from typing import Any

_TEMPLATES: dict[str, dict[str, Any]] = {
    "bell": {
        "name": "bell",
        "qubits": 2,
        "qasm": """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0],q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
""",
        "observable": None,
        "notes": "Estado |Φ+>; counts ~50/50 em 00 e 11 dentro da flutuação.",
    },
    "ghz3": {
        "name": "ghz3",
        "qubits": 3,
        "qasm": """OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
creg c[3];
h q[0];
cx q[0],q[1];
cx q[1],q[2];
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
""",
        "observable": None,
        "notes": "GHZ de 3 qubits; mede correlação tripla, não prova emaranhamento.",
    },
    "chsh": {
        "name": "chsh",
        "qubits": 2,
        "circuits": {
            "zz": """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0],q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
""",
            "zx": """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0],q[1];
h q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
""",
            "xz": """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0],q[1];
h q[0];
measure q[0] -> c[0];
measure q[1] -> c[1];
""",
            "xx": """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0],q[1];
h q[0];
h q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
""",
        },
        "observable": None,
        "notes": (
            "S = E(ZZ) + E(ZX) + E(XZ) - E(XX). Para |Φ+>, o ideal é 2√2. "
            "Uma execução não é prova estatística; repita e reporte incerteza."
        ),
    },
    "qft2": {
        "name": "qft2",
        "qubits": 2,
        "qasm": """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cu1(pi/2) q[0],q[1];
h q[1];
cx q[0],q[1];
cx q[1],q[0];
cx q[0],q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
""",
        "observable": None,
        "notes": "QFT de 2 qubits; a ordem dos qubits e os swaps precisam ser conferidos.",
    },
    "vqe_ansatz": {
        "name": "vqe_ansatz",
        "qubits": 2,
        "qasm": """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
ry(pi/4) q[0];
ry(pi/2) q[1];
cx q[0],q[1];
""",
        "observable": [["ZZ", 1.0]],
        "notes": (
            "Ansatz variacional mínimo; sem medida. Use Estimator com observable "
            "ZZ. Não é um resultado de VQE nem prova de vantagem."
        ),
    },
}


def template_names() -> list[str]:
    return sorted(_TEMPLATES)


def get_template(name: str) -> dict[str, Any]:
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name obrigatório")
    key = name.strip().lower()
    if key not in _TEMPLATES:
        raise ValueError(f"template desconhecido: {name!r}; disponíveis: {template_names()}")
    return copy.deepcopy(_TEMPLATES[key])


def template_catalog() -> dict[str, Any]:
    return {
        "total": len(_TEMPLATES),
        "templates": [
            {
                "name": key,
                "qubits": value["qubits"],
                "kind": "chsh-4-circuitos" if "circuits" in value else "qasm",
                "notes": value["notes"],
            }
            for key, value in sorted(_TEMPLATES.items())
        ],
        "executed": False,
        "network_access": False,
        "note": "Textos de referência; não executam circuito.",
    }
