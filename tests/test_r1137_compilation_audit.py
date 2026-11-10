"""Auditoria local de compilação/layout (R1137)."""
from __future__ import annotations

from pathlib import Path

import pytest
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.transpiler import CouplingMap

import quantum_mitigation.compilation_audit as audit


def _backend():
    return GenericBackendV2(
        num_qubits=108,
        coupling_map=CouplingMap.from_line(108),
        basis_gates=["h", "cz", "measure"],
    )


def test_physical_circuit_shape():
    circuit = audit.build_physical_circuit((106, 107))
    assert circuit.num_qubits == 108
    assert circuit.num_clbits == 2
    assert circuit.count_ops().get("cz", 0) == 1
    assert circuit.count_ops().get("measure", 0) == 2


def test_layout_preserved_and_mapping():
    circuit = audit.build_physical_circuit((106, 107))
    payload = audit.audit_layout(circuit, _backend(), initial_layout=list(range(108)))
    assert payload["layout_preserved"] is True
    assert payload["mapping_preserved"] is True
    assert payload["identity_preserved"] is True
    assert payload["active_physical"] == [106, 107]
    assert payload["final_index_layout"][106] == 106
    assert payload["final_index_layout"][107] == 107
    assert payload["qreg_matches"] is True
    assert len(payload["qasm_sha256"]) == 64
    assert payload["hardware_executed"] is False


def test_active_set_alone_cannot_hide_swap():
    circuit = audit.build_physical_circuit((106, 107))
    layout = list(range(108))
    layout[106], layout[107] = layout[107], layout[106]
    payload = audit.audit_layout(circuit, _backend(), initial_layout=layout)
    assert payload["layout_preserved"] is True
    assert payload["mapping_preserved"] is True
    assert payload["identity_preserved"] is False
    assert payload["final_index_layout"][106] == 107
    assert payload["final_index_layout"][107] == 106


def test_invalid_pair():
    with pytest.raises(ValueError):
        audit.build_physical_circuit((1, 1))
    with pytest.raises(ValueError):
        audit.build_physical_circuit((0, 108))


def test_no_hardware_strings():
    text = Path(audit.__file__).read_text(encoding="utf-8")
    for forbidden in ("submit_optimized", "connect_gjq", "GJQ_API_KEY", "allow_hardware"):
        assert forbidden not in text
