"""Contraprovas do protótipo CB; simulação não é evidência de hardware."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest
from qiskit.quantum_info import Pauli, Statevector

import quantum_mitigation.cycle_benchmarking as cb


def test_parity_is_not_p00_and_ignores_identity_bits():
    counts = {"00": 40, "01": 10, "10": 20, "11": 30}
    assert cb.pauli_expectation(counts, "ZZ")["expectation"] == pytest.approx(.4)
    assert cb.pauli_expectation(counts, "IZ")["expectation"] == pytest.approx(.2)
    assert cb.pauli_expectation(counts, "ZI")["expectation"] == pytest.approx(0.)
    assert cb.pauli_expectation({"0x2": 7, "0x3": 3}, "IZ")["expectation"] == pytest.approx(.4)
    assert cb.pauli_expectation({"0b10": 7, "11": 3}, "IY")["expectation"] == pytest.approx(.4)


@pytest.mark.parametrize("counts", [{}, {"00": -1}, {"00": 1.5}, {"00": True},
                                     {"100": 2}, {"0x4": 2}, {"ab": 2}, {"00": 0}])
def test_invalid_counts_rejected(counts):
    with pytest.raises(ValueError):
        cb.pauli_expectation(counts, "ZZ")


@pytest.mark.parametrize("pauli", cb.PAULIS_2Q)
def test_ideal_parity_all_observables(pauli):
    for depth in (0, 2, 4, 8, 16):
        qc = cb.cycle_benchmarking_circuit(pauli, depth, seed=391)
        clean = qc.remove_final_measurements(inplace=False)
        obs = Pauli("".join("I" if x == "I" else "Z" for x in pauli))
        assert Statevector.from_instruction(clean).expectation_value(obs).real == pytest.approx(1)
        assert qc.count_ops().get("cz", 0) == depth
        assert qc.count_ops().get("barrier", 0) >= depth + 1


@pytest.mark.parametrize("depth", [-1, 1, 3, 2.5, True])
def test_odd_or_invalid_depth_is_not_silently_recovered(depth):
    with pytest.raises(ValueError):
        cb.cycle_benchmarking_circuit("XX", depth, seed=1)


@pytest.mark.parametrize("pauli,qubits", [("II", (0, 1)), ("XZ", (1, 0)),
                                        ("XZ", (0, 7)), ("+XX", (0, 1))])
def test_invalid_observable_or_mapping_rejected(pauli, qubits):
    with pytest.raises(ValueError):
        cb.cycle_benchmarking_circuit(pauli, 2, seed=1, qubits=qubits)


def test_cz_orbits_against_independent_matrix_conjugation():
    cz = np.diag([1, 1, 1, -1])
    for p in cb.PAULIS_2Q:
        q = cb.cz_conjugate_label(p)
        lhs, rhs = cz @ Pauli(p).to_matrix() @ cz, Pauli(q).to_matrix()
        assert np.allclose(lhs, rhs) or np.allclose(lhs, -rhs)


def test_rank_nine_and_nonnegative_indistinguishable_generators():
    audit = cb.identifiability_audit("cz_even")
    assert audit["rank"] == 9
    assert audit["nullity"] == 6
    assert len(audit["orbits"]) == 9
    assert not audit["identifiable"]
    matrix = cb.decay_design_matrix("cz_even")
    _, _, vh = np.linalg.svd(matrix)
    g1 = np.full(15, .02)
    g2 = g1 + .005 * vh[-1]
    assert np.all(g2 > 0) and not np.allclose(g1, g2)
    np.testing.assert_allclose(matrix @ g1, matrix @ g2, atol=1e-14)
    f = dict(zip(cb.PAULIS_2Q, np.exp(-2 * matrix @ g1)))
    result = cb.pauli_lindblad_rates(f, design="cz_even")
    assert result["status"] == "blocked_nonidentifiable"
    assert result["rates"] is None


def test_full_spectrum_inversion_not_scalar_gamma():
    rates = np.linspace(.0002, .003, 15)
    matrix = cb.decay_design_matrix("full_pauli_spectrum")
    assert np.linalg.matrix_rank(matrix) == 15
    f = np.exp(-2 * matrix @ rates)
    assert not np.allclose(-np.log(f)/2, rates)
    output = cb.pauli_lindblad_rates(dict(zip(cb.PAULIS_2Q, f)), design="full_pauli_spectrum")
    assert output["status"] == "model_compatible"
    np.testing.assert_allclose(list(output["rates"].values()), rates, atol=1e-12)
    assert output["pec_hardware_allowed"] is False


def test_physical_pauli_channel_not_always_lindblad_embeddable():
    # pI=.8, pIX=.1, pIY=.1: canal CPTP com uma taxa de gerador negativa.
    f = {p: .8 + .1 * (1 if Pauli(p).commutes(Pauli("IX")) else -1)
         + .1 * (1 if Pauli(p).commutes(Pauli("IY")) else -1) for p in cb.PAULIS_2Q}
    out = cb.pauli_lindblad_rates(f, design="full_pauli_spectrum")
    assert out["status"] == "blocked_non_lindblad"
    assert out["rates"] is None
    assert min(out["unconstrained_rates"].values()) < -.01


def test_joint_bootstrap_propagates_without_discarding_negative_draws():
    rng = np.random.default_rng(33)
    g = np.linspace(.001, .004, 15)
    m = cb.decay_design_matrix("full_pauli_spectrum")
    draws_g = g + rng.normal(0, .002, (200, 15))
    draws_f = np.exp(-2 * draws_g @ m.T)
    out = cb.pauli_lindblad_rates(dict(zip(cb.PAULIS_2Q, np.exp(-2*m@g))),
                                design="full_pauli_spectrum", eigenvalue_samples=draws_f)
    assert out["uncertainty"]["n_samples"] == 200
    assert out["uncertainty"]["negative_rate_draw_fraction"] > 0
    ci = np.array(list(out["uncertainty"]["ci95"].values()))
    np.testing.assert_allclose(ci, np.quantile(draws_g, [.025, .975], axis=0).T, atol=1e-12)


def test_parity_decay_recovers_known_value_and_is_reproducible():
    points = [(m, .92 * .97**m, 100000) for m in (0, 2, 4, 8, 16)]
    fit = cb.fit_pauli_decay(points, n_bootstrap=100, seed=31)
    assert fit["status"] == "conditional_fit"
    assert fit["effective_eigenvalue"] == pytest.approx(.97, abs=1e-5)
    assert fit["amplitude"] == pytest.approx(.92, abs=1e-5)
    assert fit["ci95"][0] < .97 < fit["ci95"][1]
    assert "gamma" not in fit
    assert cb.fit_pauli_decay(points, n_bootstrap=100, seed=31) == fit


@pytest.mark.parametrize("values", [[0, 0, 0, 0, 0], [.2, .3, .4, .5, .7],
                                    [.95, .15, .85, .1, .6]])
def test_uninformative_or_misspecified_decay_blocked(values):
    points = list(zip((0, 2, 4, 8, 16), values, [10000]*5))
    fit = cb.fit_pauli_decay(points, n_bootstrap=100, seed=5)
    assert fit["status"].startswith("blocked")
    assert fit["ci95"] is None


def test_density_matrix_oracle_injects_actual_pauli_noise():
    # Apenas erro XI: conjugação CZ alterna XI e XZ.
    # IZ e ZX têm anticommutações distintas. Todos os observáveis são checados.
    from scipy.linalg import expm
    rates = dict.fromkeys(cb.PAULIS_2Q, 0.)
    rates["XI"], rates["YZ"] = .013, .007
    ident = np.eye(16)
    gen = sum(g * (np.kron(Pauli(p).to_matrix().conj(), Pauli(p).to_matrix()) - ident)
              for p, g in rates.items())
    channel = expm(gen)
    cz = np.diag([1, 1, 1, -1])
    for p in cb.PAULIS_2Q:
        # Teste independente evolui (I+P)/4, não estados puros do gerador.
        rho = (np.eye(4) + Pauli(p).to_matrix())/4
        for _ in range(4):
            rho = cz @ rho @ cz
            rho = (channel @ rho.reshape(16, order="F")).reshape((4, 4), order="F")
        expected = np.trace(Pauli(p).to_matrix() @ rho).real
        qc = cb.cycle_benchmarking_circuit(p, 4, seed=49)
        probs = cb.simulate_pauli_probabilities(qc, rates)
        measured = sum(v * (-1)**sum(int(b) for b, a in zip(k, p) if a != "I")
                       for k, v in probs.items())
        assert measured == pytest.approx(expected, abs=1e-10)


def test_manifest_hash_budget_and_tamper_gate():
    manifest = cb.build_manifest()
    assert manifest == cb.build_manifest()
    assert manifest["budget"] == {"jobs": 150, "shots_per_job": 4096, "total_shots": 614400}
    assert manifest["settings"]["depths"] == [0, 2, 4, 8, 16]
    assert manifest["identifiability"]["rank"] == 9
    assert manifest["hardware_submission_allowed"] is False
    cb.validate_manifest(manifest)
    bad = copy.deepcopy(manifest)
    next(iter(bad["plan"].values()))["qasm_sha256"] = "0"*64
    with pytest.raises(ValueError):
        cb.validate_manifest(bad)


def test_analysis_rejects_missing_data_and_legacy_metadata():
    manifest = cb.build_manifest()
    with pytest.raises(ValueError):
        cb.analyze_cycle_benchmarking(manifest, {})
    with pytest.raises(ValueError):
        cb.analyze_cycle_benchmarking({"cb_ZZ_1_s1": {"pauli": "ZZ", "depth": 1}}, {})


def test_harness_offline_only_and_refuses_overwrite(tmp_path):
    path = Path(__file__).resolve().parents[1] / "harnesses/quantum-error-mitigation/cb_protocol.py"
    spec = importlib.util.spec_from_file_location("cb_protocol", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    out = tmp_path / "manifest.json"
    assert module.main(["plan", "--out", str(out)]) == 0
    assert json.loads(out.read_text())["hardware_submission_allowed"] is False
    assert module.main(["plan", "--out", str(out)]) == 2
    text = path.read_text()
    assert "submit_optimized" not in text and "connect_gjq" not in text


def test_explicit_xi_xz_counterexample():
    g1, g2 = np.zeros(15), np.zeros(15)
    g1[cb.PAULIS_2Q.index("XI")] = .013
    g2[cb.PAULIS_2Q.index("XZ")] = .013
    d = cb.decay_design_matrix("cz_even")
    np.testing.assert_allclose(d@g1, d@g2, atol=1e-14)


def test_opposing_sets_are_not_averaged_before_fit():
    points = [(m, .7*.97**m + sign*.12*(-1)**i, 10000)
              for sign in (-1, 1) for i, m in enumerate(cb.DEPTHS)]
    assert cb.fit_pauli_decay(points, n_bootstrap=100)["status"] == "blocked_fit"


def test_fit_diagnostics_are_not_validated_inference():
    points = [(m, .92*.97**m, 4096) for m in cb.DEPTHS]
    fit = cb.fit_pauli_decay(points, n_bootstrap=100)
    assert fit.get("inference_validated") is False
    assert fit.get("goodness_of_fit_gate") == "heuristic_chi2_not_calibrated"
    assert fit.get("ci_scope") == "pointwise_conditional_shots_not_simultaneous"


def test_tolerance_is_not_exact_positivity():
    g = np.full(15, .01)
    g[0] = -5e-11
    f = np.exp(-2*cb.decay_design_matrix("full_pauli_spectrum")@g)
    result = cb.pauli_lindblad_rates(dict(zip(cb.PAULIS_2Q, f)), design="full_pauli_spectrum")
    assert result.get("nonnegative_exactly") is False
    assert result.get("nonnegative_with_tolerance") is True
    assert result["rates"]["IX"] < 0


def _load_harness(filename):
    path = Path(__file__).resolve().parents[1] / "harnesses/quantum-error-mitigation" / filename
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("text", ['{"jobs": {}, "jobs": {"x": 1}}', '{"x": NaN}',
                                 '{"x": Infinity}', '[1,2]'])
def test_harness_rejects_ambiguous_json(tmp_path, text):
    module = _load_harness("cb_protocol.py")
    assert hasattr(module, "read_json_strict"), "Não aceitar JSON com chaves repetidas ou NaN"
    path = tmp_path / "ambiguous.json"
    path.write_text(text)
    with pytest.raises(ValueError):
        module.read_json_strict(path)


@pytest.mark.parametrize("defect", ["extra", "shots", "qasm", "task_id"])
def test_imported_jobs_reject_wrong_receipts_before_fitting(defect):
    manifest = cb.build_manifest(shots=10)
    data = {"schema_version": 2, "manifest_sha256": manifest["manifest_sha256"],
            "origin": {"kind": "imported_hardware_counts"},
            "jobs": {k: {"counts": {"00": 10}, "qasm_sha256": v["qasm_sha256"], "task_id": k}
                     for k, v in manifest["plan"].items()}}
    key = next(iter(data["jobs"]))
    if defect == "extra":
        data["jobs"]["extra"] = data["jobs"][key]
    elif defect == "shots":
        data["jobs"][key]["counts"] = {"00": 9}
    elif defect == "qasm":
        data["jobs"][key]["qasm_sha256"] = "bad"
    else:
        for job in data["jobs"].values():
            job["task_id"] = "duplicate"
    with pytest.raises(ValueError):
        cb.analyze_cycle_benchmarking(manifest, data, n_bootstrap=100)


def test_guidance_reconciles_hardware_and_identifiability():
    root = Path(__file__).resolve().parents[1]
    paths = [".opencode/skills/mitigacao-e-correcao-quantica/SKILL.md",
             "harnesses/quantum-error-mitigation/HARNESS.md", "docs/HANDOFF_CB_GST.md",
             "agents/catalog/quantum-error-mitigation.md", "agents/catalog/quantum-noise-characterization.md"]
    for path in paths:
        text = (root/path).read_text()
        assert "posto 9" in text.lower(), path
        assert "Três runs de mitigação 4×4" not in text, path
        assert "três runs de mitigação 4×4" not in text, path
        assert "RC real em hardware não foi executado" not in text, path


def test_readout_reports_real_calibration_scope():
    module = _load_harness("readout_repeat_analysis.py")
    output = module.build()
    for record in output["runs"].values():
        assert record.get("baseline_metric_scope") == "subspace_00_11"
        assert record.get("optimized_metric_scope") == "subspace_00_11"
    assert output["decision"].get("r1_gate_remeasured") is False
    assert "subespaço" in module.report(output).lower()


def test_readout_missing_runs_remains_fail_closed(tmp_path, monkeypatch):
    module = _load_harness("readout_repeat_analysis.py")
    monkeypatch.setattr(module, "RUNS", {"absent": tmp_path/"missing.json"})
    output = module.build()
    assert output["summary"]["n_runs"] == 0
    assert output["summary"]["baseline_mean"] is None
    assert output["decision"]["compare_layouts_now"] is False
    assert "ausente" in module.report(output).lower()
