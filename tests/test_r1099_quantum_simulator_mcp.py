"""R1099: MCP nativo de simulação quântica e gates da auditoria de MCPs."""
from __future__ import annotations

import pytest

pytest.importorskip("qiskit")

BELL_QASM = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0],q[1];
measure q -> c;
"""


def _tools():
    pytest.importorskip("mcp")
    from integrations.quantum_simulator_mcp import create_server

    return create_server()._tool_manager._tools


def test_simulator_status_and_catalog():
    tools = _tools()
    assert set(tools) >= {"sim_status", "sim_noise_models", "sim_run_qasm", "sim_audit_counts"}
    status = tools["sim_status"].fn()
    assert status["executed"] is False
    assert status["max_qubits"] == 12
    assert status["max_shots"] == 10000
    assert status["qiskit_version"].startswith("2.")
    assert "noise_models" in status
    models = tools["sim_noise_models"].fn()
    assert {"none", "depolarizing", "thermal_relaxation", "readout_error"} <= set(models)


def test_simulator_runs_bell_and_audits_counts():
    tools = _tools()
    r = tools["sim_run_qasm"].fn(BELL_QASM, 512, "none", None, 42, True)
    assert r["ok"] is True
    assert r["metadata"]["shots"] == 512
    assert r["metadata"]["qubits"] == 2
    assert sum(r["counts"].values()) == 512
    assert abs(sum(r["probabilities"].values()) - 1.0) < 1e-9
    audit = tools["sim_audit_counts"].fn(r["counts"], 512)
    assert audit["ok"] is True
    bad = tools["sim_audit_counts"].fn(r["counts"], 511)
    assert bad["ok"] is False


def test_simulator_runs_noise_model():
    tools = _tools()
    r = tools["sim_run_qasm"].fn(
        BELL_QASM, 256, "depolarizing", {"error_rate": 0.01}, 7, True
    )
    assert r["ok"] is True
    assert sum(r["counts"].values()) == 256
    assert r["metadata"]["noise_model"] == "depolarizing"


def test_simulator_requires_confirm_and_enforces_limits():
    tools = _tools()
    with pytest.raises(ValueError):
        tools["sim_run_qasm"].fn(BELL_QASM, 512, "none", None, 42, False)
    with pytest.raises(ValueError):
        tools["sim_run_qasm"].fn(BELL_QASM, 0, "none", None, 42, True)
    with pytest.raises(ValueError):
        tools["sim_run_qasm"].fn(BELL_QASM, 10001, "none", None, 42, True)
    with pytest.raises(ValueError):
        tools["sim_run_qasm"].fn(BELL_QASM, 512, "desconhecido", None, 42, True)
    with pytest.raises(ValueError):
        tools["sim_run_qasm"].fn("OPENQASM 9.9;", 512, "none", None, 42, True)

    qreg = "\n".join(f"h q[{i}];" for i in range(13))
    oversize = f'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[13];\ncreg c[13];\n{qreg}\nmeasure q -> c;\n'
    with pytest.raises(ValueError):
        tools["sim_run_qasm"].fn(oversize, 512, "none", None, 42, True)


def test_simulator_does_not_pollute_stdout(capfd):
    tools = _tools()
    r = tools["sim_run_qasm"].fn(BELL_QASM, 128, "none", None, 42, True)
    assert r["ok"] is True
    out, _ = capfd.readouterr()
    assert out == ""
