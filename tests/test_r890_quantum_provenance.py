"""SPEC-935-R890: simulação clássica delimitada e evidência sem autopromoção."""
import hashlib
import json
from importlib import import_module

import pytest

from reasoning.engines import QuantumReasoningEngine, ReasoningResult
from reasoning.quantum import (
    QuantumSimulator,
    run_experiment_suite,
    uniform_superposition,
)


@pytest.fixture
def isolated_memory(monkeypatch, tmp_path):
    module = import_module("mci.metabus")
    monkeypatch.setattr(module, "MEMORY_FILE", str(tmp_path / "memory.json"))
    memory = module.MetacognitiveMemory()
    memory.confidence_ledger["marceloclaro"] = 0.5
    monkeypatch.setattr(module.metabus, "memory", memory)
    return memory


def test_quantum_engine_does_not_claim_to_answer_an_ignored_query():
    result = QuantumReasoningEngine().reason("Quanto é 2+3?", n_qubits=2, shots=8, seeds=[42]).to_dict()
    assert result["confidence"] == 0.0
    evidence = result.get("evidence", {})
    assert evidence.get("execution_kind") == "classical_simulation"
    assert evidence.get("backend") == "python_statevector"
    assert evidence.get("quantum_hardware_used") is False
    assert evidence.get("query_evaluated") is False
    assert "não" in result["conclusion"].lower()
    assert result["calibrated"] is False


def test_suite_preserves_per_seed_counts_and_honest_sampling_metrics():
    report = run_experiment_suite(2, seeds=[42], shots=1)
    row = report["experiments"]["superposition"]["runs"][0]
    assert "fidelity" not in row
    assert row.get("support_mass") == 1.0
    assert row.get("total_variation_distance") == pytest.approx(0.75)
    assert row.get("measurement_entropy") == pytest.approx(2.0)
    assert sum(row["counts"].values()) == 1


def test_report_hash_commits_to_configuration_and_all_runs():
    report = run_experiment_suite(3, seeds=[42, 123], shots=8)
    digest = report.get("report_sha256")
    body = {key: value for key, value in report.items() if key != "report_sha256"}
    assert digest == hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True, allow_nan=False).encode()).hexdigest()
    assert report.get("configuration") == {"n_qubits": 3, "shots": 8, "seeds": [42, 123]}
    assert report["experiments"]["bell"].get("n_qubits") == 2
    assert report["experiments"]["ghz"].get("n_qubits") == 3


def test_qiskit_availability_does_not_authorize_python_allocation_above_cap(monkeypatch):
    module = import_module("reasoning.quantum")
    monkeypatch.setattr(module, "_has_qiskit", lambda: True, raising=False)
    with pytest.raises(ValueError):
        QuantumSimulator(21)


@pytest.mark.parametrize("n", [True, 2.5, 1, 21, 100])
def test_qubit_type_and_range_are_strict(n):
    with pytest.raises(ValueError):
        QuantumSimulator(n)


@pytest.mark.parametrize("kwargs", [
    {"shots": 0}, {"shots": -1}, {"shots": 10001}, {"shots": True}, {"shots": 1.5},
    {"seeds": []}, {"seeds": [True]}, {"seeds": [1.5]}, {"seeds": list(range(11))},
])
def test_invalid_budget_is_rejected_before_any_circuit_is_built(monkeypatch, kwargs):
    module = import_module("reasoning.quantum")
    def forbidden(*args, **options):
        pytest.fail("A configuração inválida não pode construir circuito.")
    monkeypatch.setattr(module, "bell_state", forbidden)
    with pytest.raises(ValueError):
        module.run_experiment_suite(2, **kwargs)


@pytest.mark.parametrize("method,args", [
    ("h", (-1,)), ("x", (True,)), ("z", (2,)), ("cnot", (0, 0)),
    ("cnot", (0, 2)), ("cz", (-1, 1)), ("cz", (1, 1)), ("rx", (0, float("nan"))),
])
def test_invalid_gate_never_partially_changes_state(method, args):
    sim = QuantumSimulator(2, seed=42)
    before = (list(sim.state), list(sim.gate_log))
    with pytest.raises(ValueError):
        getattr(sim, method)(*args)
    assert (sim.state, sim.gate_log) == before


def test_measurement_prepares_sampling_weights_once(monkeypatch):
    sim = uniform_superposition(2, 42)
    original, calls = sim._rng.choices, []
    def observed(*args, **kwargs):
        calls.append(kwargs)
        return original(*args, **kwargs)
    monkeypatch.setattr(sim._rng, "choices", observed)
    assert sum(sim.measure(100).values()) == 100
    assert len(calls) == 1
    assert "cum_weights" in calls[0]


def test_measurement_entropy_is_explicit_and_legacy_name_deprecated():
    sim = uniform_superposition(2, 42)
    assert sim.measurement_entropy() == pytest.approx(2.0)
    with pytest.deprecated_call():
        assert sim.entanglement_entropy() == pytest.approx(2.0)


def test_non_quantum_results_keep_the_existing_dictionary_contract():
    assert "evidence" not in ReasoningResult("fixture", "x", "y").to_dict()


def test_primary_persists_compact_execution_provenance_without_counts(isolated_memory):
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    before = dict(isolated_memory.confidence_ledger)
    result = MarceloClaroOrchestrator(auto_load_agents=False).reason(
        "Quanto é 2+3?", engine="quantum", n_qubits=2, shots=8, seeds=[42])
    observation = isolated_memory.episodic[-1]["observation"]
    execution = observation.get("execution", {})
    assert execution.get("execution_kind") == "classical_simulation"
    assert execution.get("quantum_hardware_used") is False
    assert execution.get("query_evaluated") is False
    assert execution.get("configuration") == {"n_qubits": 2, "shots": 8, "seeds": [42]}
    assert execution.get("report_sha256") == result["evidence"]["report_sha256"]
    assert "counts" not in json.dumps(execution)
    assert dict(isolated_memory.confidence_ledger) == before


def test_direct_primary_suite_does_not_change_trust(isolated_memory):
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    before = dict(isolated_memory.confidence_ledger)
    result = MarceloClaroOrchestrator(auto_load_agents=False).quantum_experiment(2, [42], 8)
    assert result.get("execution_kind") == "classical_simulation"
    assert result["metacognition"]["persisted"] is True
    execution = isolated_memory.episodic[-1]["observation"]["execution"]
    assert execution["report_sha256"] == result["report_sha256"]
    assert "counts" not in json.dumps(execution)
    assert dict(isolated_memory.confidence_ledger) == before


@pytest.mark.parametrize("seed", [True, 1.5, "42"])
def test_simulator_seed_must_be_a_strict_integer(seed):
    with pytest.raises(ValueError):
        QuantumSimulator(2, seed=seed)


def test_sample_counts_are_reproducible_with_precomputed_weights():
    first = uniform_superposition(3, 42).measure(256)
    second = uniform_superposition(3, 42).measure(256)
    assert first == second
    assert sum(first.values()) == 256


def test_metadata_whitelist_does_not_store_histograms_or_instructions(isolated_memory):
    from mci.metabus import metabus
    from mci.metacognitive_loop import MetacognitiveLoop
    evidence = run_experiment_suite(2, [42], 8)
    evidence["instructions"] = "não é uma instrução"
    loop = MetacognitiveLoop(metabus)
    loop.observe_reasoning("fixture", {"engine": "quantum", "conclusion": "observado",
        "available": True, "evidence": evidence}, {"records": [], "lessons": []})
    execution = isolated_memory.episodic[-1]["observation"]["execution"]
    assert "instructions" not in execution
    assert "experiments" not in execution
    assert len(json.dumps(execution)) < 1000


@pytest.mark.parametrize("seed", [-1, 1 << 63, 1 << 15000], ids=["negative", "above_int64", "15001_bits"])
def test_seed_magnitude_is_rejected_before_any_circuit(monkeypatch, seed):
    module = import_module("reasoning.quantum")
    def forbidden(*args, **kwargs):
        pytest.fail("Seed fora da faixa não pode iniciar a construção de circuito.")
    monkeypatch.setattr(module, "bell_state", forbidden)
    with pytest.raises(ValueError):
        module.run_experiment_suite(2, [seed], 8)


@pytest.mark.parametrize("seed", [0, (1 << 63) - 1])
def test_seed_range_boundaries_remain_reproducible_and_serializable(seed):
    first = run_experiment_suite(2, [seed], 8)
    second = run_experiment_suite(2, [seed], 8)
    assert first == second
    assert first["configuration"]["seeds"] == [seed]
    assert len(first["report_sha256"]) == 64
    assert json.loads(json.dumps(first))["configuration"]["seeds"] == [seed]
