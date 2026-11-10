"""Provider GJQ de primeira classe (R1139)."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

import integrations.gjq_core_provider as provider

QASM = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0],q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
"""


def test_status_is_local_and_does_not_expose_secret(monkeypatch):
    monkeypatch.setenv("GJQ_API_KEY", "super-secret-value")
    payload = provider.status()
    encoded = json.dumps(payload)
    assert "super-secret-value" not in encoded
    assert payload["sdk"] == "0.2.1"
    assert payload["network_access"] is False
    assert payload["hardware_executed"] is False
    assert "limits" in payload["budget"]


def test_submit_gates_fail_closed(monkeypatch):
    blocked = provider.submit(QASM, "FAS-CPU", confirm=False)
    assert blocked["status"] == "blocked"
    assert blocked["executed"] is False

    monkeypatch.setattr(provider, "credential_present", lambda _flag: True)
    hardware = provider.submit(QASM, "Baihua", confirm=True, allow_hardware=False)
    assert hardware["status"] == "blocked"
    assert hardware["executed"] is False

    monkeypatch.setattr(provider, "credential_present", lambda _flag: False)
    missing = provider.submit(QASM, "FAS-CPU", confirm=True)
    assert missing["status"] == "blocked"
    assert "credencial" in missing["reason"]


def test_submit_respects_budget_before_network(monkeypatch):
    monkeypatch.setattr(provider, "credential_present", lambda _flag: True)
    monkeypatch.setattr(
        provider,
        "check_budget",
        lambda backend, shots, hardware: {
            "allowed": False,
            "reason": "orçamento bloqueado",
        },
    )
    payload = provider.submit(QASM, "FAS-CPU", confirm=True)
    assert payload["status"] == "blocked"
    assert payload["reason"] == "orçamento bloqueado"
    assert payload["executed"] is False


def test_submit_success_path_with_mocks(monkeypatch):
    backend = SimpleNamespace(name="FAS-CPU")
    service = SimpleNamespace(backend=lambda name: backend)
    monkeypatch.setattr(provider, "credential_present", lambda _flag: True)
    monkeypatch.setattr(provider, "check_budget", lambda backend, shots, hardware: {"allowed": True})
    monkeypatch.setattr(provider, "_service", lambda use_cached: service)
    submitted_kwargs = {}

    def _fake_submit(backend, circuit, **kwargs):
        submitted_kwargs.update(kwargs)
        return {"task_id": "task-123"}

    monkeypatch.setattr(provider, "submit_optimized", _fake_submit)
    captured = {}
    monkeypatch.setattr(
        provider,
        "record_submission",
        lambda *args, **kwargs: captured.update({"args": args, "kwargs": kwargs}),
    )
    payload = provider.submit(
        QASM,
        "FAS-CPU",
        shots=128,
        confirm=True,
        transpile_circuit=False,
        compile=False,
    )
    assert payload["status"] == "submitted"
    assert payload["task_id"] == "task-123"
    assert payload["executed"] is True
    assert payload["compile"] is False
    assert len(payload["qasm_sha256"]) == 64
    assert captured["kwargs"]["qasm_sha256"] == payload["qasm_sha256"]
    assert submitted_kwargs["options"] == {"compile": False}


def test_list_backends_with_fake_service(monkeypatch):
    service = SimpleNamespace(list_backends=lambda: [{"name": "FAS-CPU", "qubits": 20}])
    monkeypatch.setattr(provider, "credential_present", lambda _flag: True)
    monkeypatch.setattr(provider, "_service", lambda use_cached: service)
    payload = provider.list_backends()
    assert payload["status"] == "success"
    assert payload["backends"][0]["name"] == "FAS-CPU"
    assert payload["executed"] is False


def test_compilation_audit_with_fake_target(monkeypatch):
    from qiskit.providers.fake_provider import GenericBackendV2
    from qiskit.transpiler import CouplingMap

    backend = GenericBackendV2(
        num_qubits=108,
        coupling_map=CouplingMap.from_line(108),
        basis_gates=["h", "cz", "measure"],
    )
    service = SimpleNamespace(backend=lambda name: backend)
    monkeypatch.setattr(provider, "credential_present", lambda _flag: True)
    monkeypatch.setattr(provider, "_service", lambda use_cached: service)
    payload = provider.compilation_audit("Baihua", (106, 107))
    assert payload["status"] == "success"
    assert payload["audit"]["layout_preserved"] is True
    assert payload["audit"]["identity_preserved"] is True
    assert payload["executed"] is False


def test_no_hardware_or_secret_strings():
    text = Path(provider.__file__).read_text(encoding="utf-8")
    for forbidden in ("sk-", "Bearer "):
        assert forbidden not in text
