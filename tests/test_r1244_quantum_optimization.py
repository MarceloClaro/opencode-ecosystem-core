"""TDD contracts for SPEC-935-R1244; no network, credentials, or QPU jobs."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from integrations import quantum_optimization as qo  # noqa: E402
from integrations import quantum_optimization_mcp as qomcp  # noqa: E402


def _problem():
    return {
        "schema_version": 1,
        "name": "two-variable-fixture",
        "num_variables": 2,
        "constant": 4.0,
        "linear": [1.0, 2.0],
        "quadratic": [[0, 1, -3.0]],
    }


def test_qubo_validation_energy_and_canonical_hash():
    original = qo.parse_qubo(_problem())
    reordered = _problem()
    reordered["quadratic"] = [[1, 0, -3.0]]
    normalized = qo.parse_qubo(reordered)
    assert original.problem_sha256 == normalized.problem_sha256
    assert original.energy([0, 0]) == pytest.approx(4.0)
    assert original.energy([1, 0]) == pytest.approx(5.0)
    assert original.energy([0, 1]) == pytest.approx(6.0)
    assert original.energy([1, 1]) == pytest.approx(4.0)


@pytest.mark.parametrize("mutate", [
    lambda p: p.update(schema_version=True),
    lambda p: p.update(num_variables=0),
    lambda p: p.update(linear=[1.0]),
    lambda p: p.update(linear=[True, 0.0]),
    lambda p: p.update(constant=10**10000),
    lambda p: p.update(quadratic=[[0, 0, 1.0]]),
    lambda p: p.update(quadratic=[[0, 1, float("nan")]]),
    lambda p: p.update(quadratic=[[0, 1, 1.0], [1, 0, 2.0]]),
    lambda p: p.update(unknown=True),
])
def test_qubo_rejects_invalid_schema_and_coefficients(mutate):
    payload = _problem()
    mutate(payload)
    with pytest.raises(qo.QuantumContractError):
        qo.parse_qubo(payload)


def test_exact_classical_baseline_and_limits():
    qubo = qo.parse_qubo(_problem())
    result = qo.exact_classical_baseline(qubo)
    assert result["backend"] == "classical-exact-baseline"
    assert result["quantum"] is False
    assert result["optimality"] == "exact_for_model"
    assert result["assignment"] == [0, 0]  # deterministic lexicographic tie-break
    assert result["objective"] == pytest.approx(4.0)

    too_large = {
        "schema_version": 1,
        "name": "beyond-baseline",
        "num_variables": 17,
        "constant": 0,
        "linear": [0] * 17,
        "quadratic": [],
    }
    with pytest.raises(qo.QuantumContractError, match="exact baseline"):
        qo.exact_classical_baseline(qo.parse_qubo(too_large))

    near_tie = qo.parse_qubo({
        "schema_version": 1, "name": "sub-picounit-improvement", "num_variables": 1,
        "constant": 0.0, "linear": [-5e-13], "quadratic": [],
    })
    near_tie_result = qo.exact_classical_baseline(near_tie)
    assert near_tie_result["assignment"] == [1]
    assert near_tie_result["objective"] == pytest.approx(-5e-13)

    near_tie_ising = qo.qubo_to_ising(near_tie)
    assert near_tie_ising["constant"] == pytest.approx(-2.5e-13)
    assert near_tie_ising["fields"] == [[0, pytest.approx(2.5e-13)]]
    near_tie_ir = qo.build_qaoa_ir(near_tie, depth=1)
    assert any(row["gate"] == "RZ" and row["scale"] == pytest.approx(5e-13)
               for row in near_tie_ir["operations"])


def test_energy_and_ising_reject_nonrepresentable_float_sums():
    large = qo.parse_qubo({
        "schema_version": 1, "name": "overflow-guard", "num_variables": 2,
        "constant": 1e308, "linear": [1e308, 1e308], "quadratic": [],
    })
    with pytest.raises(qo.QuantumContractError, match="finit"):
        large.energy([1, 1])
    with pytest.raises(qo.QuantumContractError, match="finit"):
        qo.qubo_to_ising(large)


def test_qubo_to_ising_and_qaoa_ir():
    qubo = qo.parse_qubo(_problem())
    ising = qo.qubo_to_ising(qubo)
    assert ising["constant"] == pytest.approx(4.75)
    assert ising["fields"] == [[0, pytest.approx(0.25)], [1, pytest.approx(-0.25)]]
    assert ising["couplers"] == [[0, 1, pytest.approx(-0.75)]]

    ir = qo.build_qaoa_ir(qubo, depth=1)
    assert ir["depth"] == 1
    assert ir["measurement_order"] == list(range(2))
    assert ir["parameter_order"] == ["gamma_0", "beta_0"]
    assert ir["operations"][0] == {"gate": "H", "qubits": [0]}
    assert any(row["gate"] == "RZZ" and row["parameter"] == "gamma_0"
               for row in ir["operations"])
    assert ir["operations"][-1]["gate"] == "MEASURE_ALL"


def test_bounded_optimizer_respects_evaluation_budget():
    calls = []

    def evaluate(angles):
        calls.append(tuple(angles))
        return sum((value - 0.4) ** 2 for value in angles)

    result = qo.bounded_angle_search(evaluate, depth=1, max_evaluations=7)
    assert result["evaluations"] == len(calls)
    assert result["evaluations"] <= 7
    assert result["method"] == "bounded-coordinate-search"
    assert result["best_objective"] <= result["initial_objective"]
    assert len(result["best_angles"]) == 2
    assert result["optimality"] == "not_proven"


def test_counts_to_energy_uses_qiskit_bit_order():
    payload = _problem()
    payload["constant"] = 0.0
    qubo = qo.parse_qubo(payload)
    result = qo.energy_from_counts(qubo, {"01": 3, "10": 1})
    # Qiskit/GJQ count strings are high-to-low; q0 is the rightmost bit.
    assert result["mean_energy"] == pytest.approx(1.25)
    assert result["samples"] == 4


def test_remote_runner_requires_per_call_consent_before_secret_or_sdk(monkeypatch):
    monkeypatch.setenv("GJQ_API_KEY", "test-token-not-secret")
    monkeypatch.setattr(qo, "load_gjq_sdk", lambda: pytest.fail("SDK carregado antes do consentimento"))
    result = qo.run_gjq_qaoa(
        _problem(), backend_name="Baihua", shots=128,
        max_evaluations=1, max_total_shots=128, confirm_remote=False,
    )
    assert result["status"] == "blocked"
    assert result["result"]["code"] == "remote_confirmation_required"
    assert result["evidence"]["jobs_submitted"] == 0


def test_remote_runner_requires_rotated_environment_credential(monkeypatch):
    monkeypatch.delenv("GJQ_API_KEY", raising=False)
    monkeypatch.setattr(qo, "load_gjq_sdk", lambda: pytest.fail("SDK carregado sem credencial"))
    result = qo.run_gjq_qaoa(
        _problem(), backend_name="Baihua", shots=128,
        max_evaluations=1, max_total_shots=128, confirm_remote=True,
    )
    assert result["status"] == "blocked"
    assert result["result"]["code"] == "credential_missing"
    assert "api_key" not in json.dumps(result).lower()


@pytest.mark.parametrize("backend_type,expected", [
    ("Superconducting", True),
    ("Quantum hardware", True),
    ("CPU Simulator", False),
    ("GPU Simulator", False),
    ("MPS", False),
    ("unknown", False),
    ("", False),
])
def test_hardware_classifier_rejects_simulators_and_unknown_types(backend_type, expected):
    assert qo.is_confirmed_hardware_type(backend_type) is expected


def test_remote_runner_uses_fake_provider_without_network(monkeypatch):
    monkeypatch.setenv("GJQ_API_KEY", "test-token-not-secret")

    class Param:
        def __init__(self, label):
            self.label = label

        def __rmul__(self, scalar):
            return (scalar, self.label)

    class ParamVector(list):
        def __init__(self, name, length):
            super().__init__(Param(f"{name}[{i}]") for i in range(length))

    class Circuit:
        def __init__(self, qubits):
            self.qubits = qubits
            self.operations = []

        def h(self, qubit): self.operations.append(("h", qubit))
        def rz(self, angle, qubit): self.operations.append(("rz", angle, qubit))
        def rzz(self, angle, a, b): self.operations.append(("rzz", angle, a, b))
        def rx(self, angle, qubit): self.operations.append(("rx", angle, qubit))
        def measure_all(self): self.operations.append(("measure_all",))
        def assign_parameters(self, values, inplace=False):
            self.operations.append(("bind", len(values)))
            return self

    class Service:
        def __init__(self, api_key):
            assert api_key == "test-token-not-secret"
            self.backend_calls = []

        def list_backends(self):
            return [{"name": "fake-qpu", "type": "Superconducting"}]

        def backend(self, name):
            self.backend_calls.append(name)
            return type("Backend", (), {"name": name})()

    class PassManager:
        def run(self, circuit): return circuit

    class Job:
        def result(self, timeout):
            assert timeout > 0
            return {"counts": {"00": 64, "11": 64}}

    class Sampler:
        def __init__(self, backend):
            self.backend = backend

        def run(self, circuit, shots):
            assert self.backend.name == "fake-qpu"
            assert shots == 128
            return Job()

    FakeSampler = Sampler

    class SDK:
        GJQRuntimeService = Service
        Sampler = FakeSampler
        QuantumCircuit = Circuit
        ParameterVector = ParamVector

        @staticmethod
        def generate_preset_pass_manager(**kwargs):
            assert kwargs["optimization_level"] == 2
            return PassManager()

    result = qo.run_gjq_qaoa(
        _problem(), backend_name="fake-qpu", shots=128,
        max_evaluations=2, max_total_shots=256, confirm_remote=True, sdk=SDK,
    )
    assert result["status"] == "success", result
    assert result["evidence"]["jobs_submitted"] == 2
    assert result["evidence"]["total_shots"] == 256
    assert result["result"]["optimality"] == "not_proven"
    assert "test-token-not-secret" not in json.dumps(result)

    class FailingSampler:
        def __init__(self, backend):
            self.backend = backend

        def run(self, circuit, shots):
            raise TimeoutError("provider outcome may be uncertain")

    class FailingSDK(SDK):
        Sampler = FailingSampler

    uncertain = qo.run_gjq_qaoa(
        _problem(), backend_name="fake-qpu", shots=128,
        max_evaluations=1, max_total_shots=128, confirm_remote=True, sdk=FailingSDK,
    )
    assert uncertain["status"] == "partial"
    assert uncertain["result"]["submission_state"] == "uncertain"
    assert uncertain["evidence"]["hardware_executed"] is None
    assert uncertain["evidence"]["automatic_retry"] is False


def test_mcp_catalog_and_tools():
    catalog = qo.quantum_catalog()
    assert catalog["status"] == "success"
    entries = {item["name"]: item for item in catalog["result"]["frameworks"]}
    assert entries["GJQ/Tiangong"]["qiskit"] is True
    assert entries["GJQ/Tiangong"]["pennylane"] is True
    assert entries["Cirq"]["gjq_adapter_documented"] is False
    assert entries["XQuad"]["dependency_selected"] is False
    assert entries["Transformers"]["quantum_runtime"] is False

    server = qomcp.create_server()
    assert server is not None


def test_mcp_negotiates_supported_protocol_versions():
    for requested, expected, has_annotations, has_structured_content in (
        ("2025-06-18", "2025-06-18", True, True),
        ("2024-11-05", "2024-11-05", False, False),
        ("unsupported-version", "2025-06-18", True, True),
    ):
        server = qomcp.create_server()
        initialized = server.handle({
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {"protocolVersion": requested, "capabilities": {},
                       "clientInfo": {"name": "pytest-r1244", "version": "1.0"}},
        })
        assert initialized["result"]["protocolVersion"] == expected
        assert initialized["result"]["capabilities"]["tools"]["listChanged"] is False

        listed = server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        catalog_tool = next(tool for tool in listed["result"]["tools"]
                            if tool["name"] == "quantum_catalog")
        assert ("annotations" in catalog_tool) is has_annotations

        called = server.handle({
            "jsonrpc": "2.0", "id": 3, "method": "tools/call",
            "params": {"name": "quantum_catalog", "arguments": {}},
        })
        assert ("structuredContent" in called["result"]) is has_structured_content


def test_mcp_unexpected_remote_failure_preserves_uncertain_effect_state(monkeypatch):
    def fail_after_possible_submission(_arguments):
        raise TimeoutError("provider response unavailable")

    monkeypatch.setitem(qomcp._HANDLERS, "qaoa_optimize_gjq", fail_after_possible_submission)
    server = qomcp.create_server()
    response = server.handle({
        "jsonrpc": "2.0", "id": 7, "method": "tools/call",
        "params": {
            "name": "qaoa_optimize_gjq",
            "arguments": {
                "problem": _problem(), "backend_name": "test-backend",
                "shots": 128, "max_evaluations": 1, "max_total_shots": 128,
                "confirm_remote": True,
            },
        },
    })
    payload = json.loads(response["result"]["content"][0]["text"])
    assert payload["status"] == "partial"
    assert payload["evidence"]["external_effect"] == "possible"
    assert payload["evidence"]["submission_state"] == "unknown"
    assert payload["evidence"]["automatic_retry"] is False


def _read_message(proc):
    while True:
        line = proc.stdout.readline()
        if not line:
            raise AssertionError(f"EOF inesperado: {proc.stderr.read()[-1000:]}")
        line = line.strip()
        if line.startswith("{"):
            return json.loads(line)


def _send(proc, message):
    proc.stdin.write(json.dumps(message) + "\n")
    proc.stdin.flush()


def test_mcp_stdio_transport_read_only_operations():
    environment = os.environ.copy()
    environment.pop("GJQ_API_KEY", None)
    proc = subprocess.Popen(
        [sys.executable, "-m", "integrations.quantum_optimization_mcp"],
        cwd=str(ROOT), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, env=environment,
    )
    try:
        _send(proc, {
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                       "clientInfo": {"name": "pytest-r1244", "version": "1.0"}},
        })
        initialized = _read_message(proc)
        assert initialized["result"]["serverInfo"]["name"] == "quantum-optimization"
        _send(proc, {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
        _send(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        listed = _read_message(proc)
        names = {tool["name"] for tool in listed["result"]["tools"]}
        assert {"quantum_catalog", "qubo_inspect", "qaoa_prepare", "qaoa_optimize_gjq"} <= names

        _send(proc, {
            "jsonrpc": "2.0", "id": 3, "method": "tools/call",
            "params": {"name": "quantum_catalog", "arguments": {}},
        })
        called = _read_message(proc)
        body = json.loads(called["result"]["content"][0]["text"])
        assert body["status"] == "success"
        assert body["result"]["network"] is False

        _send(proc, {
            "jsonrpc": "2.0", "id": 4, "method": "tools/call",
            "params": {"name": "qubo_inspect", "arguments": {"problem": _problem()}},
        })
        inspected = _read_message(proc)
        inspected_body = json.loads(inspected["result"]["content"][0]["text"])
        assert inspected_body["status"] == "success"
        assert inspected_body["result"]["network"] is False

        _send(proc, {
            "jsonrpc": "2.0", "id": 5, "method": "tools/call",
            "params": {"name": "qaoa_prepare", "arguments": {
                "problem": _problem(), "depth": 1, "shots": 128, "max_evaluations": 1,
            }},
        })
        prepared = _read_message(proc)
        prepared_body = json.loads(prepared["result"]["content"][0]["text"])
        assert prepared_body["status"] == "success"
        assert prepared_body["result"]["remote_submission"] is False

        _send(proc, {
            "jsonrpc": "2.0", "id": 6, "method": "tools/call",
            "params": {"name": "qaoa_optimize_gjq", "arguments": {
                "problem": _problem(), "backend_name": "unused-backend",
                "shots": 128, "max_evaluations": 1, "max_total_shots": 128,
                "confirm_remote": False,
            }},
        })
        blocked = _read_message(proc)
        blocked_body = json.loads(blocked["result"]["content"][0]["text"])
        assert blocked_body["status"] == "blocked"
        assert blocked_body["result"]["code"] == "remote_confirmation_required"
        assert blocked_body["evidence"]["jobs_submitted"] == 0
    finally:
        proc.stdin.close()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
    assert proc.returncode == 0


def test_managed_quantum_research_profiles_are_valid():
    from agents.lifecycle import AgentLifecycleService

    lifecycle = AgentLifecycleService(ROOT)
    for agent_id in ("quantum-applicability-researcher", "quantum-optimization-researcher"):
        report = lifecycle.validate(agent_id)
        assert report["definition_validated"] is True
        assert report["executed"] is False
        profile = report["profile"]
        assert profile["allow_edit"] is False
        assert profile["parent"] == "marceloclaro"
        assert profile["permission"]["task"] == "deny"
        assert profile["permission"]["webfetch"] == "deny"
        assert profile["permission"]["bash"]["*"] == "deny"


def test_quantum_documentation_and_mcp_disabled_by_default():
    doc = (ROOT / "docs/quantum/QUANTUM_OPTIMIZATION_GJQ.md").read_text(encoding="utf-8")
    for required in (
        '"enabled": false',
        "revogado/rotacionado",
        "AGPL-3.0-or-later",
        "https://tiangongqs.com/docs/en/",
        "https://github.com/guoji-quantum/gjq_client",
        "https://modelcontextprotocol.io/specification/2025-06-18/server/tools",
        "custo em",
        "tarefa enviada a uma",
    ):
        assert required in doc

    generated = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    remote = generated.get("mcp", {}).get("quantum-optimization")
    assert remote is None or remote.get("enabled") is False
