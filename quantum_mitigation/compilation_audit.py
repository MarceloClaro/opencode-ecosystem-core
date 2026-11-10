"""R1137 — auditoria local de compilação e layout físico.

O sampler GJQ envia o QASM original e o servidor compila; o layout físico não
é devolvido. Esta auditoria pré-transpila com `initial_layout` explícito e
verifica, localmente, quais qubits físicos ficaram ativos. Não executa
hardware e não prova que o servidor respeitará `compile=False`.

Uso:
    payload = audit_layout(build_physical_circuit((106, 107)), backend)
"""
from __future__ import annotations

import hashlib

from qiskit import QuantumCircuit, qasm2, transpile

LIMITS = (
    "Auditoria local com o Target fornecido. Não executa o servidor GJQ; "
    "para o Baihua, o Target precisa vir do backend real. A preservação de "
    "layout no servidor com compile=False não foi testada."
)


def build_physical_circuit(
    pair: tuple[int, int] = (106, 107),
    *,
    num_qubits: int = 108,
) -> QuantumCircuit:
    pair = tuple(int(item) for item in pair)
    if len(pair) != 2 or pair[0] == pair[1]:
        raise ValueError("pair deve conter dois qubits distintos")
    if any(item < 0 or item >= num_qubits for item in pair):
        raise ValueError("pair fora do registrador")
    circuit = QuantumCircuit(num_qubits, 2)
    circuit.h(pair[0])
    circuit.h(pair[1])
    circuit.cz(pair[0], pair[1])
    circuit.h(pair[1])
    circuit.measure([pair[0], pair[1]], [0, 1])
    return circuit


def transpile_with_layout(
    circuit: QuantumCircuit,
    backend,
    *,
    initial_layout=None,
    optimization_level: int = 0,
    seed_transpiler: int = 42,
) -> QuantumCircuit:
    if not 0 <= optimization_level <= 3:
        raise ValueError("optimization_level deve estar em 0..3")
    kwargs = {
        "backend": backend,
        "optimization_level": int(optimization_level),
        "seed_transpiler": int(seed_transpiler),
    }
    if initial_layout is not None:
        kwargs["initial_layout"] = list(initial_layout)
    return transpile(circuit, **kwargs)


def audit_layout(
    circuit: QuantumCircuit,
    backend,
    *,
    initial_layout=None,
    optimization_level: int = 0,
    seed_transpiler: int = 42,
) -> dict:
    compiled = transpile_with_layout(
        circuit,
        backend,
        initial_layout=initial_layout,
        optimization_level=optimization_level,
        seed_transpiler=seed_transpiler,
    )
    layout = compiled.layout.final_index_layout() if compiled.layout else None
    active = sorted({
        compiled.find_bit(qubit).index
        for instruction in compiled.data
        for qubit in instruction.qubits
    })
    qasm = qasm2.dumps(compiled)
    expected = sorted({
        circuit.find_bit(qubit).index
        for instruction in circuit.data
        for qubit in instruction.qubits
    })
    preserved = set(active) == set(expected)
    requested = None if initial_layout is None else list(initial_layout)
    mapping_preserved = None
    identity_preserved = None
    if layout is not None:
        identity_preserved = all(int(layout[index]) == index for index in expected)
    if requested is not None and layout is not None:
        mapping_preserved = all(
            int(layout[index]) == int(requested[index]) for index in expected
        )
    return {
        "schema_version": 1,
        "n_qubits": int(compiled.num_qubits),
        "expected_active": expected,
        "active_physical": active,
        "requested_layout": requested,
        "final_index_layout": layout,
        "layout_preserved": bool(preserved),
        "mapping_preserved": mapping_preserved,
        "identity_preserved": identity_preserved,
        "qreg_matches": bool(
            f"qreg q[{compiled.num_qubits}]" in qasm
        ),
        "qasm_sha256": hashlib.sha256(qasm.encode()).hexdigest(),
        "compiled_qasm": qasm,
        "limits": LIMITS,
        "hardware_executed": False,
    }
