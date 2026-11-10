"""Contraprovas do CB com correções de 1 qubit (R1129)."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from qiskit import qasm2
from qiskit.quantum_info import Clifford, Pauli, Statevector

import quantum_mitigation.interleaved_cb as icb


def test_functions_and_design_rank():
    assert len(icb.FUNCTIONS) == 13
    assert len(icb.INDIVIDUAL) == 7
    assert len(icb.PAIR_CYCLES) == 6
    matrix = icb.design_matrix()
    assert matrix.shape == (13, 15)
    rank = icb.design_rank()
    assert rank["rank"] == 13
    assert rank["nullity"] == 2
    assert rank["full_cycle_space"] is True
    assert rank["incidence_residual"] < 1e-12


def test_all_cycles_close_and_are_valid():
    for cycle in icb.FUNCTIONS:
        assert icb.validate_cycle(cycle) == tuple(cycle)
    for invalid in ((), ("IX",), ("IX", "IY"), ("II",), ("XX", "ZY")):
        with pytest.raises(ValueError):
            icb.validate_cycle(invalid)


def test_corrections_map_same_pattern():
    gates = icb.correction_gates("XX", "YY")
    circuit = icb.QuantumCircuit(2)
    icb._apply(circuit, gates)
    image = str(icb.conjugate_pauli(Clifford(circuit), Pauli("XX")))
    assert image == "YY"
    with pytest.raises(ValueError):
        icb.correction_gates("IX", "ZX")


def test_ideal_body_returns_plus_one_at_even_depths():
    for cycle in icb.FUNCTIONS:
        for depth in (0, 2, 4):
            body = icb.cycle_body(cycle, depth)
            value = Statevector.from_instruction(body).expectation_value(Pauli(cycle[0])).real
            assert value == pytest.approx(1.0, abs=1e-10)


def test_cross_cycles_have_minus_one_at_odd_depth():
    for cycle in (("IX", "ZY"), ("IY", "ZX"), ("XI", "YZ"), ("YI", "XZ")):
        body = icb.cycle_body(cycle, 1)
        value = Statevector.from_instruction(body).expectation_value(Pauli(cycle[0])).real
        assert value == pytest.approx(-1.0, abs=1e-10)


def test_circuit_qasm_and_depth():
    circuit = icb.cycle_circuit(("XX",), 2)
    text = qasm2.dumps(circuit)
    assert circuit.count_ops().get("cz", 0) == 2
    assert circuit.count_ops().get("measure", 0) == 2
    assert "OPENQASM 2.0" in text
    with pytest.raises(ValueError):
        icb.cycle_body(("XX",), -1)
    with pytest.raises(ValueError):
        icb.cycle_body(("XX",), True)


def test_exact_recovery_of_all_thirteen():
    payload = icb.audit()
    assert payload["design"]["rank"] == 13
    assert payload["n_recovered"] == 13
    assert payload["max_absolute_error"] < 1e-10
    assert payload["unlearnable_cut_rank"] == 2
    assert payload["rates_measured"] is False
    assert payload["hardware_executed"] is False
    for item in payload["recovery"]:
        assert item["fit"]["status"] == "fit"
        assert item["absolute_error"] < 1e-10


def test_no_hardware_or_secret_strings():
    text = Path(icb.__file__).read_text(encoding="utf-8")
    for forbidden in ("submit_optimized", "connect_gjq", "GJQ_API_KEY", "allow_hardware"):
        assert forbidden not in text


def test_harness_interleaved_command(tmp_path):
    import importlib.util
    import json

    path = (
        Path(__file__).resolve().parents[1]
        / "harnesses/quantum-error-mitigation/cb_protocol.py"
    )
    spec = importlib.util.spec_from_file_location("cb_protocol_interleaved", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    out = tmp_path / "interleaved.json"
    assert module.main(["interleaved", "--out", str(out)]) == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["design"]["rank"] == 13
    assert payload["hardware_executed"] is False
    assert module.main(["interleaved", "--out", str(out)]) == 2
